import time
import pygame
import sys
import numpy as np
import heapq


class Layer:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Load assets before running the simulation
        self.background = pygame.image.load("graphics/enviroment_large.png")
        self.wide, self.height = self.background.get_size()
        self.image_player = pygame.image.load("graphics/Agent_front.png").convert_alpha()
        self.image_player_width, self.image_player_height = self.image_player.get_size()
        self.loaded_collisions = np.loadtxt("graphics/collision_layer.txt", dtype=int)

        # Constants
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = self.wide, self.height
        self.CURSOR_SIZE = 10
        self.CURSOR_STEP = 10
        self.BG_COLOR = (30, 30, 30)

        # Screen setup
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Omgeving Simulatie")
        self.clock = pygame.time.Clock()

        # Camera properties
        self.zoom = 1.0
        self.zoom_levels = [1.0, 2.0, 4.0]
        self.offset = [0, 0]
        self.cursor_pos = [self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2]

        # Pathfinding setup
        self.star = Star()
        self.start = (400, 100)
        self.goal = (670, 150)

        # Player setup
        self.player = Player(self)
        self.path = self.star.search_path(self.start, self.goal, self.loaded_collisions)
        if self.path:
            self.player.set_path(self.path)

        # Start game loop
        self.run()

    def move_cursor(self, dx, dy):
        self.cursor_pos[0] = max(0, min(self.WINDOW_WIDTH - self.CURSOR_SIZE, self.cursor_pos[0] + dx * self.CURSOR_STEP))
        self.cursor_pos[1] = max(0, min(self.WINDOW_HEIGHT - self.CURSOR_SIZE, self.cursor_pos[1] + dy * self.CURSOR_STEP))
        self.adjust()

    def adjust(self):
        self.offset[0] = self.cursor_pos[0] * self.zoom - self.WINDOW_WIDTH // 2 + self.CURSOR_SIZE // 2
        self.offset[1] = self.cursor_pos[1] * self.zoom - self.WINDOW_HEIGHT // 2 + self.CURSOR_SIZE // 2
        self.clamp()

    def clamp(self):
        max_offset_x = max(0, self.wide * self.zoom - self.WINDOW_WIDTH)
        self.offset[0] = max(0, min(self.offset[0], max_offset_x))

        max_offset_y = max(0, self.height * self.zoom - self.WINDOW_HEIGHT)
        self.offset[1] = max(0, min(self.offset[1], max_offset_y))

    def zoom_in(self):
        if self.zoom < max(self.zoom_levels):
            self.zoom = self.zoom_levels[self.zoom_levels.index(self.zoom) + 1]
            self.center_cursor()
            time.sleep(0.2)

    def zoom_out(self):
        if self.zoom > min(self.zoom_levels):
            self.zoom = self.zoom_levels[self.zoom_levels.index(self.zoom) - 1]
            self.center_cursor()
            time.sleep(0.2)

    def center_cursor(self):
        self.offset[0] = self.cursor_pos[0] * self.zoom - self.WINDOW_WIDTH // 2 + self.CURSOR_SIZE // 2
        self.offset[1] = self.cursor_pos[1] * self.zoom - self.WINDOW_HEIGHT // 2 + self.CURSOR_SIZE // 2
        self.clamp()

    def draw_background(self):
        scaled_bg = pygame.transform.scale(self.background, (int(self.wide * self.zoom), int(self.height * self.zoom)))
        bg_x = -self.offset[0]
        bg_y = -self.offset[1]
        self.screen.blit(scaled_bg, (bg_x, bg_y))

    def draw_cursor(self):
        cursor_rect = pygame.Rect(
            self.WINDOW_WIDTH // 2 - self.CURSOR_SIZE // 2,
            self.WINDOW_HEIGHT // 2 - self.CURSOR_SIZE // 2,
            self.CURSOR_SIZE,
            self.CURSOR_SIZE
        )
        cursor_color = (255, 0, 0)
        pygame.draw.ellipse(self.screen, cursor_color, cursor_rect)

    def draw_player(self):
        scale_factor = self.zoom
        x_pos = (self.player.position_current[0] - self.image_player_width // 2) * scale_factor - self.offset[0]
        y_pos = (self.player.position_current[1] - self.image_player_height) * scale_factor - self.offset[1]
        scaled_image = pygame.transform.scale(self.image_player, (int(self.image_player_width * scale_factor), int(self.image_player_height * scale_factor)))
        self.screen.blit(scaled_image, (x_pos, y_pos))

    def run(self):
        running = True
        while running:
            self.screen.fill(self.BG_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.move_cursor(0, -1)
            if keys[pygame.K_DOWN]:
                self.move_cursor(0, 1)
            if keys[pygame.K_LEFT]:
                self.move_cursor(-1, 0)
            if keys[pygame.K_RIGHT]:
                self.move_cursor(1, 0)
            if keys[pygame.K_1]:
                self.zoom_out()
            if keys[pygame.K_2]:
                self.zoom_in()

            # Update player position along the path
            self.player.step()

            # Draw the background, cursor, and player
            self.draw_background()
            self.draw_cursor()
            self.draw_player()

            pygame.display.flip()
            self.clock.tick(10)

        pygame.quit()
        sys.exit()


class Player:
    def __init__(self, camera):
        self.camera = camera
        self.position_current = [camera.WINDOW_WIDTH // 2, camera.WINDOW_HEIGHT // 2]
        self.path = []
        self.current_path_index = 0

    def set_path(self, path):
        self.path = path
        self.current_path_index = 0

    def step(self):
        if self.path and self.current_path_index < len(self.path):
            next_position = self.path[self.current_path_index]
            self.position_current = [next_position[1], next_position[0]]
            self.current_path_index += 1


class Star:
    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node, collisions):
        height, width = collisions.shape
        y, x = node
        neighbors = [(y+dy, x+dx) for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= y+dy < height and 0 <= x+dx < width and collisions[y+dy, x+dx] == 0]
        return neighbors

    def search_path(self, start, goal, collisions):
        open_set = [(0, start)]
        came_from, g_score = {}, {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            for neighbor in self.get_neighbors(current, collisions):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    heapq.heappush(open_set, (tentative_g + self.heuristic(neighbor, goal), neighbor))
        return None
