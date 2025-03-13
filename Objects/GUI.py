import numpy as np
from datetime import datetime, timedelta
import pygame
import time
import matplotlib


class GUI:
    def __init__(self, players, start_date, end_date, steps_max):
        self.root = "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/"
        pygame.init()
        pygame.display.set_caption("Omgeving Simulatie")

        self.background = pygame.image.load(
            "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/graphics/enviroment_background.png"
        )
        self.width, self.height = self.background.get_size()
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.cursor_position = [self.width // 2, self.height // 2]
        self.cursor_zooms = [1.0, 2.0, 4.0]
        self.cursor_zoom = 1.0
        self.cursor_size = 10
        self.cursor_step = 10
        self.cursor_color = (255, 0, 0)
        self.cursor_offset = [0, 0]

        self.clock = pygame.time.Clock()

        self.players = players
        self.image_player = pygame.image.load(
            "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/graphics/Agent_front.png"
        ).convert_alpha()
        self.image_player_width, self.image_player_height = self.image_player.get_size()

        self.colors = {
            "blue": (30, 49, 227),
            "black": (0, 0, 0),
            "grey": (128, 128, 128),
            "green": (41, 161, 39),
            "brown": (143, 110, 26),
            "white": (255, 255, 255)
        }

        self.step_counter = 0
        self.date_current = start_date

        self.start_date = start_date
        self.end_date = end_date
        self.steps_max = steps_max
        self.time_per_step = (end_date - start_date) / steps_max
        self.bar()
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
            if keys[pygame.K_RIGHT]:
                self.move_cursor(-1, 0)
            if keys[pygame.K_LEFT]:
                self.move_cursor(1, 0)
            if keys[pygame.K_1]:
                self.zoom(1)
            if keys[pygame.K_2]:
                self.zoom(-1)

            next_activity = False
            for player in self.players:
                if not self.step_counter % 1000:
                    next_activity = True
                player.step(next_activity)

            self.date_current = self.start_date + (self.time_per_step * self.step_counter)

            self.draw_background()
            self.draw_cursor()
            for player in self.players:
                self.draw_player(player.position_current)
                self.draw_textbox(player.position_current, f"{player}")
            self.draw_step_info()

            pygame.display.flip()
            self.clock.tick(60)
            self.step_counter += 1

        pygame.quit()


    def move_cursor(self, dx, dy):
        """Move the camera (background) instead of the cursor."""
        self.cursor_offset[0] -= dx * self.cursor_step * self.cursor_zoom
        self.cursor_offset[1] -= dy * self.cursor_step * self.cursor_zoom
        self.clamp()

    def zoom(self, direction):
        """Zoom in/out at the cursor's current position."""
        if direction == 1 and self.cursor_zoom < max(self.cursor_zooms):
            new_zoom = self.cursor_zooms[self.cursor_zooms.index(self.cursor_zoom) + 1]
        elif direction == -1 and self.cursor_zoom > min(self.cursor_zooms):
            new_zoom = self.cursor_zooms[self.cursor_zooms.index(self.cursor_zoom) - 1]
        else:
            return  # No valid zoom change

        # Convert cursor position to world coordinates before zooming
        world_x = (self.cursor_position[0] + self.cursor_offset[0]) / self.cursor_zoom
        world_y = (self.cursor_position[1] + self.cursor_offset[1]) / self.cursor_zoom

        # Apply new zoom level
        self.cursor_zoom = new_zoom

        # Recalculate camera offset to keep world position fixed under cursor
        self.cursor_offset[0] = world_x * self.cursor_zoom - self.cursor_position[0]
        self.cursor_offset[1] = world_y * self.cursor_zoom - self.cursor_position[1]

        self.clamp()

        time.sleep(0.2)  # Prevent continuous zooming

    def clamp(self):
        """Ensure camera offset stays within bounds."""
        max_offset_x = max(0, self.width * self.cursor_zoom - self.width)
        max_offset_y = max(0, self.height * self.cursor_zoom - self.height)

        self.cursor_offset[0] = max(0, min(self.cursor_offset[0], max_offset_x))
        self.cursor_offset[1] = max(0, min(self.cursor_offset[1], max_offset_y))

    def draw_background(self):
        """Render scaled background at adjusted position."""
        scaled_bg = pygame.transform.scale(self.background,
                                           (int(self.width * self.cursor_zoom), int(self.height * self.cursor_zoom)))
        bg_x = -self.cursor_offset[0]
        bg_y = -self.cursor_offset[1]
        self.screen.blit(scaled_bg, (bg_x, bg_y))

    def draw_cursor(self):
        """Draw cursor at center of screen."""
        cursor_rect = pygame.Rect(
            self.width // 2 - self.cursor_size // 2,
            self.height // 2 - self.cursor_size // 2,
            self.cursor_size,
            self.cursor_size
        )
        pygame.draw.ellipse(self.screen, self.cursor_color, cursor_rect)

    def draw_player(self, coordinates):
        scale_factor = self.cursor_zoom
        y_pos = (coordinates[0] * scale_factor) - self.cursor_offset[1] - self.image_player_height // 2
        x_pos = (coordinates[1] * scale_factor) - self.cursor_offset[0] - self.image_player_width // 2
        scaled_image = pygame.transform.scale(self.image_player, (
            int(self.image_player_width * scale_factor), int(self.image_player_height * scale_factor)))
        self.screen.blit(scaled_image, (x_pos, y_pos))

    def draw_step_info(self):
        """Draws step information including time progression."""
        date_format = self.date_current.strftime('%d %B %Y').lstrip("0")
        font = pygame.font.Font(None, 36)
        step_text = f"Step: {self.step_counter}"
        week_text = f"Date: {date_format}"

        step_surface = font.render(step_text, True, (255, 255, 255))
        week_surface = font.render(week_text, True, (255, 255, 255))

        base_width = 230
        box_width = int(base_width * 1.25)
        box_height = step_surface.get_height() + week_surface.get_height() + 30
        box_x, box_y = 10, 10
        text_x = box_x + 10
        step_y = box_y + 10
        week_y = step_y + step_surface.get_height() + 10

        pygame.draw.rect(self.screen, (139, 69, 19), (box_x, box_y, box_width, box_height), border_radius=10)
        self.screen.blit(step_surface, (text_x, step_y))
        self.screen.blit(week_surface, (text_x, week_y))

    def draw_textbox(self, player_position, text="None"):
        # Use fixed font size and padding so the textbox stays constant on screen.
        fixed_font_size = 36
        font = pygame.font.Font(None, fixed_font_size)
        text_surface = font.render(text, True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()
        fixed_padding = 5
        box_width = text_width + fixed_padding * 2
        box_height = text_height + fixed_padding * 2

        # Convert the player's world position to screen coordinates.
        # Note: using player_position[1] for x and player_position[0] for y as in your original code.
        screen_x = player_position[1] * self.cursor_zoom - self.cursor_offset[0]
        screen_y = player_position[0] * self.cursor_zoom - self.cursor_offset[1]

        # Position the textbox above the player's head.
        # Here, we use a fixed vertical offset (e.g. 40 pixels) regardless of zoom.
        box_x = screen_x - box_width // 2
        box_y = screen_y - 40 - box_height  # Adjust 40 pixels above the head; modify as needed

        # Draw the textbox background and then the text.
        pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height))
        self.screen.blit(text_surface, (box_x + fixed_padding, box_y + fixed_padding))

    def bar(self):
        for i in ["red", "green", "blue", "red dark"]:
            layer_collision = np.loadtxt(self.root + f"Data/layer_collision/['{i}'].txt", dtype=int)
            positions_valid = [(j, i) for i in range(layer_collision.shape[0]) for j in range(layer_collision.shape[1])
                               if not layer_collision[i, j]]
            with open(self.root + f"Data/positions_valid/{i}.txt", "w") as file:
                file.write(str(positions_valid))
            print(len(positions_valid))