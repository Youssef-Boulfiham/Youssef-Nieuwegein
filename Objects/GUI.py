import numpy as np
import time
import pygame
from PIL import Image


class GUI:
    def __init__(self, player):
        pygame.init()
        pygame.display.set_caption("Omgeving Simulatie")
        self.background = pygame.image.load("graphics/enviroment_large1.png")
        self.width, self.height = self.background.get_size()
        self.screen = pygame.display.set_mode((self.width, self.height))

        # cursor
        self.cursor_position = [self.width // 2, self.height // 2]
        self.cursor_zooms = [1.0, 2.0, 4.0]
        self.cursor_zoom = 1.0
        self.cursor_size = 10
        self.cursor_step = 10
        self.cursor_color = (30, 30, 30)
        self.cursor_offset = [0, 0]

        # time
        self.clock = pygame.time.Clock()
        step_counter = 0

        # player

        self.image_player = pygame.image.load("graphics/Agent_front.png").convert_alpha()
        self.image_player_width, self.image_player_height = self.image_player.get_size()

        # colors
        self.color_white = (255, 255, 255)

        self.colors = {
            "blue": (30, 49, 227),
            "black": (0, 0, 0),
            "grey": (128, 128, 128),
            "green": (41, 161, 39),
            "brown": (143, 110, 26),
            "white": (255, 255, 255)
        }

        running = True
        while running:
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
                self.zoom(1)
            if keys[pygame.K_2]:
                self.zoom(-1)
            # if layer.tick_counter >= 200:
            #     layer.tick_counter = 0  # Reset tick counter
            #     layer.week_count += 1

            # Update player position along the path
            player.step(step_counter)

            # Draw the background, cursor, and player
            self.draw_background()
            self.draw_cursor()
            self.draw_player(player.position_current)

            # Draw the step and week info
            self.draw_step_info()

            pygame.display.flip()
            self.clock.tick(60)
            step_counter += 1

        pygame.quit()

    def move_cursor(self, dx, dy):
        self.cursor_position[0] = max(0, min(self.width - self.cursor_size,
                                             self.cursor_position[0] + dx * self.cursor_step))
        self.cursor_position[1] = max(0, min(self.height - self.cursor_size,
                                             self.cursor_position[1] + dy * self.cursor_step))
        self.adjust()

    def adjust(self):
        self.cursor_offset[0] = self.cursor_position[0] * self.cursor_zoom - self.width // 2 + self.cursor_size // 2
        self.cursor_offset[1] = self.cursor_position[1] * self.cursor_zoom - self.height // 2 + self.cursor_size // 2
        self.clamp()

    def zoom(self, direction):
        if direction == 1 and self.cursor_zoom < max(self.cursor_zooms):
            self.cursor_zoom = self.cursor_zooms[self.cursor_zooms.index(self.cursor_zoom) + 1]
        elif direction == -1 and self.cursor_zoom > min(self.cursor_zooms):
            self.cursor_zoom = self.cursor_zooms[self.cursor_zooms.index(self.cursor_zoom) - 1]
        else:
            return  # No valid zoom change

        self.center_cursor()
        time.sleep(0.2)

    def center_cursor(self):
        self.cursor_offset[0] = self.cursor_offset[0] * self.cursor_zoom - self.width // 2 + self.cursor_size // 2
        self.cursor_offset[1] = self.cursor_position[1] * self.cursor_zoom - self.height // 2 + self.cursor_size // 2
        self.clamp()

    def clamp(self):
        max_offset_x = max(0, self.width * self.cursor_zoom - self.width)
        self.cursor_offset[0] = max(0, min(self.cursor_offset[0], max_offset_x))

    def draw_background(self):
        scaled_bg = pygame.transform.scale(self.background,
                                           (int(self.width * self.cursor_zoom), int(self.height * self.cursor_zoom)))
        bg_x = -self.cursor_offset[0]
        bg_y = -self.cursor_offset[1]
        self.screen.blit(scaled_bg, (bg_x, bg_y))

    def draw_cursor(self):
        cursor_rect = pygame.Rect(
            self.width // 2 - self.cursor_size // 2,
            self.height // 2 - self.cursor_size // 2,
            self.cursor_size,
            self.cursor_size
        )
        cursor_color = (255, 0, 0)
        pygame.draw.ellipse(self.screen, cursor_color, cursor_rect)

    def draw_player(self, coordinates):
        scale_factor = self.cursor_zoom
        y_pos = (coordinates[0] - self.image_player_height) * scale_factor - self.cursor_offset[1]
        x_pos = (coordinates[1] - self.image_player_width // 2) * scale_factor - self.cursor_offset[0]
        scaled_image = pygame.transform.scale(self.image_player, (
        int(self.image_player_width * scale_factor), int(self.image_player_height * scale_factor)))
        self.screen.blit(scaled_image, (x_pos, y_pos))

    def draw_step_info(self):
        font = pygame.font.Font(None, 36)
        step_text = f"Step: {0}"
        week_text = f"Week: {0}"
        step_surface = font.render(step_text, True, self.colors["white"])
        week_surface = font.render(week_text, True, self.colors["white"])
        self.screen.blit(step_surface, (10, 10))
        self.screen.blit(week_surface, (10, 50))

    def get_collision_layer(self, allowed_colors):
        allowed_colors = [self.colors[color] for color in allowed_colors]
        image = self.background.convert("RGB")
        pixels = Image.open("enviroment_large1.png").convert("RGB")
        collision_layer = np.zeros((self.height, self.width), dtype=int)
        for y in range(self.height):
            for x in range(self.width):
                if pixels[x, y] not in allowed_colors:
                    collision_layer[y, x] = 1  # Block the color
        np.savetxt("test.txt", collision_layer, fmt='%d')