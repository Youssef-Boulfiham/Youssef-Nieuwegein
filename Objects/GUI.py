import os
import numpy as np
import pygame
import time
from PIL import Image
from Objects.Agent import Agent
import ast


class GUI:
    def __init__(self, agent_count, start_date, end_date, steps_max):
        self.name_activity = {}
        # self.
        #
        self.cursor_zooms = [1.0, 2.0, 4.0]
        self.cursor_zoom = 1.0
        self.cursor_size = 10
        self.cursor_step = 10
        self.cursor_color = (255, 0, 0)
        self.cursor_offset = [0, 0]
        self.root = "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein"
        self.colors = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "grey": (128, 128, 128),
            "brown": (143, 110, 26),
            "red dark": (155, 0, 0)
        }
        # self.set_collision_sprite()
        # self.set_positions_valid()
        positions_color = self.get_positions()
        self.agents = [Agent(i, positions_color, self.root) for i in range(agent_count)]

        self.step_counter = 1
        self.date_current = start_date
        self.start_date = start_date
        self.end_date = end_date
        self.steps_max = steps_max
        self.time_per_step = (end_date - start_date) / steps_max
        # init
        self.set_collision_sprite()
        self.set_positions_valid()
        [agent.set_positions() for agent in self.agents]
        pygame.init()
        pygame.display.set_caption("Omgeving Simulatie")
        self.background = pygame.image.load(self.root + "/graphics/enviroment_background.png")
        # self.background = pygame.image.load(self.root + "/graphics/enviroment_activity.png")
        self.width, self.height = self.background.get_size()
        self.cursor_position = [self.width // 2, self.height // 2]
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.image_agent = pygame.image.load(self.root + "/graphics/Agent_front.png").convert_alpha()
        self.clock = pygame.time.Clock()
        self.image_agent_width, self.image_agent_height = self.image_agent.get_size()
        #
        running = True
        while running:
            self.date_current = self.start_date + (self.time_per_step * self.step_counter)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                self.move_cursor(0, -1)
            if keys[pygame.K_UP]:
                self.move_cursor(0, 1)
            if keys[pygame.K_RIGHT]:
                self.move_cursor(-1, 0)
            if keys[pygame.K_LEFT]:
                self.move_cursor(1, 0)
            if keys[pygame.K_1]:
                self.zoom(1)
            if keys[pygame.K_2]:
                self.zoom(-1)
            #
            for agent in self.agents:
                agent.step(step_current=self.step_counter % 2000)
                self.name_activity = {agent.name: agent.activity}
            if self.step_counter % 250 == 0:
                print(self.name_activity)
            # draw
            self.draw_background()
            self.draw_cursor()
            for agent in self.agents:
                self.draw_agent(agent.position_current)
                self.draw_textbox(agent.position_current, str(agent), agent.action)
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

    def draw_agent(self, coordinates):
        scale_factor = self.cursor_zoom
        y_pos = (coordinates[0] * scale_factor) - self.cursor_offset[1] - self.image_agent_height // 2
        x_pos = (coordinates[1] * scale_factor) - self.cursor_offset[0] - self.image_agent_width // 2
        scaled_image = pygame.transform.scale(self.image_agent, (
            int(self.image_agent_width * scale_factor), int(self.image_agent_height * scale_factor)))
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

    def draw_textbox(self, agent_position, text, action):
        fixed_font_size = 24  # Smaller font size
        font = pygame.font.Font(None, fixed_font_size)
        text_surface = font.render(str(text), True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()
        fixed_padding = 2  # Reduced padding
        box_width = text_width + fixed_padding * 2
        box_height = text_height + fixed_padding * 2
        image_path = os.path.join(self.root, f"graphics/{action}.png")
        pictogram = pygame.image.load(image_path)
        pictogram = pygame.transform.scale(pictogram, (20, 20))  # Resize if needed
        box_width += 24  # Add extra space for the pictogram
        box_height = max(box_height, 24)  # Ensure enough height
        screen_x = agent_position[1] * self.cursor_zoom - self.cursor_offset[0]
        screen_y = agent_position[0] * self.cursor_zoom - self.cursor_offset[1]
        box_x = screen_x - box_width // 2
        box_y = screen_y - 30 - box_height
        textbox_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        textbox_surface.fill((181, 101, 29, 128))  # Light brown with 50% transparency
        self.screen.blit(textbox_surface, (box_x, box_y))
        if pictogram:
            self.screen.blit(pictogram, (box_x + fixed_padding, box_y + (box_height - 20) // 2))
            text_x = box_x + fixed_padding + 24  # Shift text right if pictogram is present
        else:
            text_x = box_x + fixed_padding
        self.screen.blit(text_surface, (text_x, box_y + fixed_padding))

    def set_collision_sprite(self):
        colors_possible = [['red'], ['green'], ['blue'], ['red dark'],
                           ['red', 'black', 'red'],
                           ['red', 'black', 'green'],
                           ['red', 'black', 'blue'],
                           ['red', 'black', 'red dark'],
                           ['green', 'black', 'red'],
                           ['green', 'black', 'green'],
                           ['green', 'black', 'blue'],
                           ['green', 'black', 'red dark'],
                           ['blue', 'black', 'red'],
                           ['blue', 'black', 'green'],
                           ['blue', 'black', 'blue'],
                           ['blue', 'black', 'red dark'],
                           ['red dark', 'black', 'red'],
                           ['red dark', 'black', 'green'],
                           ['red dark', 'black', 'blue'],
                           ['red dark', 'black', 'red dark']]

        for i in colors_possible:
            colors_rgb = [self.colors[color] for color in i]
            image = Image.open(self.root + "/graphics/enviroment_activity.png").convert("RGB")
            width, height = image.size
            pixels = image.load()
            collision_layer = np.zeros((height, width), dtype=int)
            for y in range(height):
                for x in range(width):
                    if pixels[x, y] not in colors_rgb:
                        collision_layer[y, x] = 1  # Block the color
            np.savetxt(f"{self.root + "/Data/collisions/"}{i}.txt", collision_layer, fmt='%d')

    def set_positions_valid(self):
        for i in ["red", "green", "blue", "red dark"]:
            layer_collision = np.loadtxt(self.root + f"/Data/collisions/['{i}'].txt", dtype=int)
            positions_valid = [(j, i) for i in range(layer_collision.shape[0]) for j in
                               range(layer_collision.shape[1])
                               if not layer_collision[i, j]]
            #
            with open(self.root + f"/Data/coordinates/{i}.txt", "w") as file:
                file.write(str(positions_valid))

    def get_positions(self):
        """Load all valid coordinates per activity."""
        color_positions = {}
        for color in ['red', 'green', 'blue', 'red dark']:
            # noinspection PyBroadException
            try:
                file_path = os.path.join(self.root, f"{self.root}/Data/coordinates/{color}.txt")
                with open(file_path, "r") as file:
                    positions_valid = ast.literal_eval(file.read())
                    color_positions[color] = positions_valid
            except Exception as e:
                print(
                    f"\033[93m{f'posities-activiteit-{color} nog niet berekend'}\033[0m \033 {e}")
        return color_positions

    # def get_