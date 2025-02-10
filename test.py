import time
import pygame
import sys
import numpy as np
import heapq

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 500, 700
CURSOR_SIZE = 10
CURSOR_STEP = 10
BG_COLOR = (30, 30, 30)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Omgeving Simulatie")
clock = pygame.time.Clock()

class Camera:
    def __init__(self):
        self.zoom = 1.0
        self.zoom_levels = [1.0, 2.0, 4.0]
        self.offset = [0, 0]
        self.cursor_pos = [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2]
        self.image_player = pygame.image.load("graphics/Agent_front.png").convert_alpha()
        self.image_player_width = self.image_player.get_width()
        self.image_player_height = self.image_player.get_height()

    def move_cursor(self, dx, dy):
        self.cursor_pos[0] = max(0, min(WINDOW_WIDTH - CURSOR_SIZE, self.cursor_pos[0] + dx * CURSOR_STEP))
        self.cursor_pos[1] = max(0, min(WINDOW_HEIGHT - CURSOR_SIZE, self.cursor_pos[1] + dy * CURSOR_STEP))
        self.adjust()

    def adjust(self):
        self.offset[0] = self.cursor_pos[0] * self.zoom - WINDOW_WIDTH // 2 + CURSOR_SIZE // 2
        self.offset[1] = self.cursor_pos[1] * self.zoom - WINDOW_HEIGHT // 2 + CURSOR_SIZE // 2
        self.clamp()

    def clamp(self):
        max_offset_x = max(0, WINDOW_WIDTH * self.zoom - WINDOW_WIDTH)
        self.offset[0] = max(0, min(self.offset[0], max_offset_x))

        max_offset_y = max(0, WINDOW_HEIGHT * self.zoom - WINDOW_HEIGHT)
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
        self.offset[0] = self.cursor_pos[0] * self.zoom - WINDOW_WIDTH // 2 + CURSOR_SIZE // 2
        self.offset[1] = self.cursor_pos[1] * self.zoom - WINDOW_HEIGHT // 2 + CURSOR_SIZE // 2
        self.clamp()

    def draw_background(self):
        scaled_bg = pygame.transform.scale(
            pygame.image.load("graphics/enviroment_large.png"),
            (int(WINDOW_WIDTH * self.zoom), int(WINDOW_HEIGHT * self.zoom))
        )
        bg_x = -self.offset[0]
        bg_y = -self.offset[1]
        screen.blit(scaled_bg, (bg_x, bg_y))

    def draw_cursor(self):
        cursor_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - CURSOR_SIZE // 2,
            WINDOW_HEIGHT // 2 - CURSOR_SIZE // 2,
            CURSOR_SIZE,
            CURSOR_SIZE
        )
        cursor_color = (255, 0, 0)
        pygame.draw.ellipse(screen, cursor_color, cursor_rect)

    def draw_player(self, player_position_next):
        scale_factor = self.zoom
        x_pos = (player_position_next[0] - self.image_player_width // 2) * scale_factor - self.offset[0]
        y_pos = (player_position_next[1] - self.image_player_height) * scale_factor - self.offset[1]
        scaled_image = pygame.transform.scale(self.image_player,
                                              (int(self.image_player_width * scale_factor),
                                               int(self.image_player_height * scale_factor)))
        screen.blit(scaled_image, (x_pos, y_pos))

class Player:
    def __init__(self, camera):
        self.camera = camera
        self.position_current = [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2]  # Starting position
        self.path = []  # Path for the player to follow
        self.current_path_index = 0  # Current step in the path

    def set_path(self, path):
        """Set the path for the player to follow."""
        self.path = path
        self.current_path_index = 0

    def step(self):
        """Move the player along the path."""
        if self.path and self.current_path_index < len(self.path):
            next_position = self.path[self.current_path_index]
            self.position_current = [next_position[1], next_position[0]]  # Swap x and y for pygame coordinates
            self.current_path_index += 1

class Star:
    def __init__(self):
        pass

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node, collisions):
        height, width = collisions.shape
        y, x = node
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and collisions[ny, nx] == 0:
                neighbors.append((ny, nx))
        return neighbors

    def search_path(self, start, goal, collisions):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            for neighbor in self.get_neighbors(current, collisions):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None

# Main Game Loop
camera = Camera()
player = Player(camera)
BG_IMAGE = pygame.image.load("graphics/enviroment_large.png")
running = True

# Pathfinding setup
background_image_path = "graphics/enviroment_large1.png"
loaded_collisions = np.loadtxt("graphics/collision_layer.txt", dtype=int)
star = Star()
start = (400, 100)  # Starting position (y, x)
goal = (670, 150)   # Goal position (y, x)
path = star.search_path(start, goal, loaded_collisions)

if path:
    player.set_path(path)  # Set the calculated path for the player

while running:
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        camera.move_cursor(0, -1)
    if keys[pygame.K_DOWN]:
        camera.move_cursor(0, 1)
    if keys[pygame.K_LEFT]:
        camera.move_cursor(-1, 0)
    if keys[pygame.K_RIGHT]:
        camera.move_cursor(1, 0)
    if keys[pygame.K_1]:
        camera.zoom_out()
    if keys[pygame.K_2]:
        camera.zoom_in()

    # Update player position along the path
    player.step()

    # Draw the background, cursor, and player
    camera.draw_background()
    camera.draw_cursor()
    camera.draw_player(player.position_current)

    pygame.display.flip()
    clock.tick(10)  # Control the frame rate

pygame.quit()
sys.exit()