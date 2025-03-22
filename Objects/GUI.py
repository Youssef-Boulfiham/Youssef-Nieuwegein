import random
import os
import numpy as np
import pygame
import time
from PIL import Image
from Objects.Agent import Agent
import ast
import json
from collections import defaultdict
from itertools import tee


class GUI:
    def __init__(self, agents_count, start_date, end_date, steps_max):
        self.name_activity = {}
        self.action = False
        self.activity = "idle"
        #
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
        self.root = "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/"
        self.set_collision()
        self.set_positions()
        # self.set_positions_friends()
        positions_color = self.get_positions()
        self.positions_friends = self.get_positions_friends()
        self.agents_count = agents_count
        self.agents = [Agent(i, positions_color, self.root, agents_count) for i in range(agents_count)]  # statitieken
        self.step_counter = 1
        self.date_current = start_date
        self.start_date = start_date
        self.end_date = end_date
        self.steps_max = steps_max
        self.time_per_step = (end_date - start_date) / steps_max
        self.cursor_zooms = [1.0, 2.0, 4.0]
        self.cursor_zoom = 1.0
        self.cursor_size = 10
        self.cursor_step = 10
        self.cursor_color = (255, 0, 0)
        self.cursor_offset = [0, 0]
        self.pictogram_cache = {}  # Cache for loaded pictograms
        self.textbox_color = (181, 101, 29, 128)  # Textbox color with transparency
        self.pictogram_size = (20, 20)  # Fixed pictogram size

        # pygame
        pygame.init()
        pygame.display.set_caption("Omgeving Simulatie")
        self.background = pygame.image.load(self.root + "/graphics/enviroment_background.png")
        # self.background = pygame.image.load(self.root + "/graphics/enviroment_activity.png")
        self.width, self.height = self.background.get_size()
        self.cursor_position = [self.width // 2, self.height // 2]
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        # agent
        self.image_agent = pygame.image.load(self.root + "/graphics/Agent_front.png").convert_alpha()
        self.image_agent_width, self.image_agent_height = self.image_agent.get_size()
        self.font = pygame.font.Font(None, 24)  # Load font once

        #
        running = True
        self.step_counter = 1000
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
            self.draw_cursor()
            self.draw_background()
            ##
            step_counter_mod = self.step_counter % 2000
            self.activity = "idle"
            if step_counter_mod == 0:
                self.action = True
                self.activity = "activiteit_kiezen"
            elif step_counter_mod == 1000:
                self.action = False
                self.activity = "vrienden_maken"
                self.positions_end = self.get_positions_end()
            elif step_counter_mod == 1250:
                self.vrienden_maken()
                self.action = True
            elif step_counter_mod == 1450:
                self.action = False
                self.set_agents_actions_false()
            elif step_counter_mod == 1500:
                self.activity = "middelen_gebruiken"
            elif step_counter_mod == 1750:
                self.action = True
            elif step_counter_mod == 1950:
                self.action = False
            #
            for agent in self.agents:
                agent_position = self.positions_end.get(agent.name, agent.position_current)
                agent.step(self.activity, agent_position)
                self.draw_agent(agent.position_current)
                self.draw_textbox(agent.position_current, text="", action=agent.action)

            self.draw_step_info()
            pygame.display.flip()
            self.clock.tick(600)
            self.step_counter += 1
        pygame.quit()

    def vrienden_maken(self):
        print(';')
        agents = list(self.positions_end.keys())

        # Ensure an even number of agents
        if len(agents) % 2 != 0:
            print("Uneven number of agents, skipping pairing for one agent.")
            agents = agents[:-1]

        pairwise = lambda it: zip(*[iter(it)] * 2)  # verkeerd
        friendship_status = {}

        for agent_left_name, agent_right_name in pairwise(agents):
            agent_left = self.agents[agent_left_name]
            agent_right = self.agents[agent_right_name]

            # Enforce strict friendship limits
            if agent_left.friend_request.get(agent_right_name, 0) < 5 and \
                    agent_right_name not in agent_left.friends and \
                    len(agent_left.friends) < 5 and len(agent_right.friends) < 5 and \
                    random.getrandbits(1):

                agent_left.friends.append(agent_right_name)
                agent_right.friends.append(agent_left_name)

                agent_left.action, agent_right.action = "checkmark", "checkmark"
                friendship_status[agent_left_name] = True
                friendship_status[agent_right_name] = True
                print(agent_left.activity, agent_right.activity, agent_left_name, agent_right_name)
            else:
                friendship_status[agent_left_name] = False
                friendship_status[agent_right_name] = False

        # print(friendship_status)



    def set_agents_actions_false(self):
        for agent in self.agents:
            agent.action = False

    def draw_textbox(self, position, text, action):
        # Ensure text is a string and check if there's anything to display
        text = str(text).strip()
        show_pictogram = self.action and bool(action)

        if not text and not show_pictogram:
            return  # Nothing to display

        # Render text if it's not empty
        text_surface = self.font.render(text, True, (255, 255, 255)) if text else None
        text_width, text_height = text_surface.get_size() if text_surface else (0, 0)

        # Calculate box size
        pictogram_width = 24 if show_pictogram else 0
        box_width = text_width + pictogram_width + 4
        box_height = max(text_height + 4, 24)

        # Calculate position
        screen_x = position[1] * self.cursor_zoom - self.cursor_offset[0]
        screen_y = position[0] * self.cursor_zoom - self.cursor_offset[1]
        box_x = screen_x - box_width // 2
        box_y = screen_y - 30 - box_height

        # Create surface if size changes
        if not hasattr(self, 'textbox_surface') or self.textbox_surface.get_size() != (box_width, box_height):
            self.textbox_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        self.textbox_surface.fill(self.textbox_color)
        self.screen.blit(self.textbox_surface, (box_x, box_y))

        # Draw pictogram if needed
        text_x = box_x + 2
        if show_pictogram:
            if action not in self.pictogram_cache:
                self.pictogram_cache[action] = pygame.transform.scale(
                    pygame.image.load(os.path.join(self.root, f"graphics/{action}.png")),
                    self.pictogram_size
                )
            self.screen.blit(self.pictogram_cache[action], (text_x, box_y + (box_height - self.pictogram_size[1]) // 2))
            text_x += 24

        # Draw text if available
        if text_surface:
            self.screen.blit(text_surface, (text_x, box_y + (box_height - text_height) // 2))

    import random
    from collections import defaultdict

    def get_positions_end(self):
        agents_per_activity = defaultdict(list)
        for agent in self.agents:
            activity = agent.activity
            if activity != "thuis":
                agents_per_activity[activity].append(agent.name)

        agents_positions = {}

        for activity, agents in agents_per_activity.items():
            positions_friends_activity = self.positions_friends[activity]
            random.shuffle(agents)

            # Ensure even count by removing the last agent if odd
            if len(agents) % 2 != 0:
                agents.pop()

            # Assign positions in pairs
            for i, agent in enumerate(agents):
                agents_positions[agent] = positions_friends_activity[i]

        return agents_positions

    def move_cursor(self, dx, dy):
        """Move the camera (background) instead of the cursor."""
        self.cursor_offset[0] -= dx * self.cursor_step * self.cursor_zoom
        self.cursor_offset[1] -= dy * self.cursor_step * self.cursor_zoom
        self.clamp()

    def draw_step_info(self):
        """Draws step information including time progression."""
        date_format = self.date_current.strftime('%d %B %Y').lstrip("0")
        font = pygame.font.Font(None, 36)
        step_text = f"{self.step_counter % 2000}"
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

    def set_collision(self):
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
                        collision_layer[y, x] = 1
            np.savetxt(f"{self.root + "/Data/Input/collisions/"}{i}.txt", collision_layer, fmt='%d')

    def set_positions(self):
        for color in ["red", "green", "blue", "red dark"]:
            layer_collision = np.loadtxt(self.root + f"/Data/Input/collisions/['{color}'].txt", dtype=int)
            positions_valid = [(x, y) for y in range(layer_collision.shape[0])
                               for x in range(layer_collision.shape[1])
                               if not layer_collision[y, x] and x % 32 == 0 and y % 16 == 0]
            with open(self.root + f"/Data/Input/coordinates/{color}.txt", "w") as file:
                json.dump(positions_valid, file)

    def get_positions(self):
        """Load all valid coordinates per activity."""
        positions_color = {}
        for color in ['red', 'green', 'blue', 'red dark']:
            # noinspection PyBroadException
            try:
                file_path = os.path.join(self.root, "Data", "Input", "coordinates", f"{color}.txt")
                with open(file_path, "r") as file:
                    positions_valid = ast.literal_eval(file.read())
                    positions_color[color] = positions_valid
            except FileNotFoundError:
                print(f"\033[93mposities-activiteit-{color} nog niet berekend\033[0m")
        return positions_color

    def set_positions_friends(self):
        activities = ["school", "vriend thuis", "vrije tijd"]
        coordinates = [[384, 336, 350, 224],
                       [270, 462, 240, 380],
                       [480, 624, 432, 524]]
        all_positions = []
        for i, activity in enumerate(activities):
            x, y, x1, y1 = coordinates[i]
            n = 12
            y_values = [y + round(j * (y1 - y) / n) for j in range(n + 1)]
            positions = [(yi, x) for yi in y_values] + [(yi, x1) for yi in y_values]
            all_positions.append(positions)
            #
            file_path = os.path.join(self.root, "Data", "Input", "positions_friends", f"{activity}.txt")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(str(positions))

    def get_positions_friends(self):
        activities = ["school", "vriend thuis", "vrije tijd"]
        all_positions = {}  # Change this to a dictionary instead of a list
        for activity in activities:
            file_path = os.path.join(self.root, "Data", "Input", "positions_friends", f"{activity}.txt")
            try:
                with open(file_path, "r") as f:
                    positions = ast.literal_eval(f.read())
                    all_positions[activity] = positions
            except FileNotFoundError:
                print(f"\033[93mposities-activiteit-{activity} nog niet geschreven\033[0m")
                all_positions[activity] = []
        return all_positions

    def __str__(self):
        return str(f"{self.step_counter}, {self.activity}")
