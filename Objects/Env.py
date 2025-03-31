import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import random
import os
import numpy as np
import pygame
import time
from PIL import Image
from Objects.Agent import Agent
import ast
import json
from itertools import tee
from datetime import datetime, timedelta


class Env:
    def __init__(self, start_date, epochs, steps_per_day=4000, breakpoint_time=None):
        self.positions_filtered = []
        self.activity_colors = {"thuis": "red", "vrije tijd": "blue", "school": "green", "vriend thuis": "red dark"}
        self.colors_activities = ["red", "green", "blue", "red dark"]
        self.name_activity = {}
        self.action = False
        self.activity = "idle"
        # self.age_counts = {12: 1, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0}
        # self.age_counts = {12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1}
        # self.age_counts = {12: 3, 13: 3, 14: 3, 15: 3, 16: 3, 17: 3, 18: 3}
        self.age_counts = {12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5, 18: 5}
        # self.age_counts = {12: 10, 13: 10, 14: 10, 15: 10, 16: 10, 17: 10, 18: 10}
        # self.binge_percentages = {12: 1, 13: 3, 14: 6, 15: 14, 16: 36, 17: 48, 18: 86}
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
        self.positions_color = self.get_positions()
        self.positions_color_sorted = {key: sorted(value) for key, value in self.positions_color.items()}
        self.positions_friends = self.positions_color_sorted
        self.agents_count = sum(self.age_counts.values())
        # self.agents = [Agent(positions_color, self.root, agents_count) for i in range(agents_count)]  # statitieken
        self.agents = self.get_agents()
        self.cursor_zooms = [1.0, 2.0, 4.0]
        self.cursor_zoom = 1.0
        self.cursor_size = 10
        self.cursor_step = 10
        self.cursor_color = (255, 0, 0)
        self.cursor_offset = [0, 0]
        self.pictogram_cache = {}  # Cache for loaded pictograms
        self.textbox_color = (181, 101, 29, 128)  # Textbox color with transparency
        self.pictogram_size = (20, 20)  # Fixed pictogram size
        #
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
        # step
        self.epochs = epochs
        self.steps_per_day = steps_per_day
        self.steps_per_week = self.steps_per_day * 7
        self.steps_per_epoch = self.steps_per_week * 4
        self.step = 950
        self.step_current = 950
        # time
        self.start_date = start_date
        self.date_current = start_date
        self.breakpoint_time = breakpoint_time  # Time to trigger breakpoint
        while True:

            # self.check_breakpoint()  # Check if we are at the breakpoint
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
            self.activity = "idle"
            if self.step_current == 0:
                self.activity = "activiteit_kiezen"
            elif self.step_current == 1000:
                self.activity = "vrienden_maken"
                self.positions_end = self.get_positions_end()
            elif self.step_current == 1250:
                self.vrienden_maken()
                self.action = True
            elif self.step_current == 1500:
                self.set_agents_actions_false()
                self.action = False
                self.activity = "middelen_gebruiken"
                # self.middelen_gebruiken()
            elif self.step_current == 1750:
                pass
            elif self.step_current == 1950:
                pass
            elif self.step_current == 2000:
                self.activity = "activiteit_kiezen"
            elif self.step_current == 3000:
                self.activity = "vrienden_maken"
                self.positions_end = self.get_positions_end()
            elif self.step_current == 3250:
                self.vrienden_maken()
                self.action = True
            elif self.step_current == 3500:
                self.set_agents_actions_false()
                self.action = False
                self.activity = "middelen_gebruiken"
            #
            #
            for agent in self.agents:
                agent_position_end = None
                if self.activity == "vrienden_maken":
                    agent_position_end = self.positions_end.get(agent.name, agent.position_current)
                agent.step(self.activity, agent_position_end)
                self.draw_agent(agent.position_current)
                self.draw_textbox(agent.position_current, text=f"{agent.name, len(agent.friends)}", action=agent.action)
            self.draw_step_info()
            # print(self)
            self.set_time()
            #
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def middelen_gebruiken(self):
        """TEST DIT IN NOTEBOOK"""
        substance = "alcohol"

        for agent in self.agents:
            # print(agent.age, self.binge_percentages[agent.age], 24, self.age_counts[agent.age], self.binge_percentages[agent.age]/24/self.age_counts[agent.age])
            rn = round(random.uniform(1, 100), 1)
            # F= percentage bingedrinkers gegeven leeftijd / aantal agents gegeven leeftijd/ 4 weken
            threshold = self.binge_percentages[agent.age] / 24
            change = True if threshold >= rn else False
            if change == True:
                print(rn, change)
        return 0

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

    from collections import defaultdict

    from collections import defaultdict

    def set_positions(self):
        for color in self.colors_activities:
            layer_collision = np.loadtxt(self.root + f"/Data/Input/collisions/['{color}'].txt", dtype=int)
            # filter (x%32=0, y%16=0)
            positions_valid = [(x, y)
                               for x in range(layer_collision.shape[1])
                               for y in range(layer_collision.shape[0])
                               if not layer_collision[y, x] and x % 32 == 0 and y % 16 == 0]
            # filter even op de x-as
            y_groups = defaultdict(list)
            for x, y in positions_valid:
                y_groups[y].append((x, y))  # Group by y-coordinate

            positions_filtered = []
            for y in sorted(y_groups.keys()):  # Process row by row
                y_groups[y].sort()  # Ensure left-to-right order

                # Ensure pairs are formed **horizontally** by taking two at a time
                while len(y_groups[y]) >= 2:
                    positions_filtered.append(y_groups[y].pop(0))  # Take the leftmost
                    positions_filtered.append(y_groups[y].pop(0))  # Take the next one on the right

            # Step 3: Sort positions **left to right, row by row**
            positions_filtered.sort(key=lambda pos: (pos[1], pos[0]))

            # Store for plotting
            self.positions_filtered = positions_filtered
            self.plot_positions(next(k for k, v in self.activity_colors.items() if v == color))
            # Step 4: Write filtered positions to file
            with open(self.root + f"/Data/Input/coordinates/{color}.txt", "w") as file:
                json.dump(positions_filtered, file)

    def plot_positions(self, activity):
        """Plots the filtered positions on a 500x700 grid with only numbered labels (no scatter points)."""
        if not self.positions_filtered:
            print("No positions to plot. Run set_positions() first.")
            return

        fig, ax = plt.subplots(figsize=(5, 7))  # 500x700 scale in inches (assuming 100 dpi per inch)

        # Add only numbers at each position
        for i, (x, y) in enumerate(self.positions_filtered):
            ax.text(x, y, str(i + 1), fontsize=8, ha='center', va='center', color='black')

        # Formatting
        ax.set_xlim(0, 500)
        ax.set_ylim(700, 0)  # Inverting y-axis to match grid convention (top-left origin)
        ax.set_xlabel("X Position")
        ax.set_ylabel("Y Position")
        ax.set_title("Filtered Positions on 500x700 Map (Numbers Only)")
        ax.grid(True)
        save_path = f"/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/Data/Input/{activity}.png"
        plt.savefig(save_path, dpi=100, bbox_inches="tight")
        plt.close()
        # Show plot
        # plt.show()

    def get_positions_end(self):
        """
        Assigns agents to valid end positions using pre-filtered positions.

        Returns:
            dict: Mapping of agent names to their assigned (x, y) positions.
        """
        # Step 1: Sort agents by activity
        activities_agents = {"vrije tijd": [], "school": [], "vriend thuis": []}
        for agent in self.agents:
            if agent.activity in activities_agents:
                activities_agents[agent.activity].append(agent.name)

        # Step 2: Define color mapping for activities
        activity_colors = {"thuis": "red", "vrije tijd": "blue", "school": "green", "vriend thuis": "red dark"}
        agents_positions_end = {}

        # Step 3: Assign positions per activity
        for activity, agent_names in activities_agents.items():
            color = activity_colors[activity]
            valid_positions = self.positions_color_sorted[color]  # Already filtered by `set_positions`

            # Step 4: Assign agents to positions and print pairs per row
            for agent_name, position in zip(agent_names, valid_positions):
                current_position = self.agents[
                    agent_name].position_current  # Assuming this method gets current position
                agents_positions_end[agent_name] = tuple(position)[::-1]

                # Print agent info with current position, end position, name, and activity
                print(
                    f"Agent: {agent_name} | Activity: {activity} | Current Position: {current_position} | End Position: {position}")

        return agents_positions_end

    def vrienden_maken(self):
        agents = sorted(self.positions_end.keys(), key=lambda name: self.positions_end[name])  # Ensure correct order

        pairwise = lambda it: zip(it[::2], it[1::2])  # Guarantees adjacent pairing
        friendship_status = {}

        for agent_left_name, agent_right_name in pairwise(agents):
            agent_left = self.agents[agent_left_name]
            agent_right = self.agents[agent_right_name]

            if agent_left.friend_request.get(agent_right_name, 0) < 5 and \
                    agent_right_name not in agent_left.friends and \
                    len(agent_left.friends) < 5 and len(agent_right.friends) < 5 and \
                    random.getrandbits(1):

                agent_left.friends.append(agent_right_name)
                agent_right.friends.append(agent_left_name)

                agent_left.action, agent_right.action = "checkmark", "checkmark"
                friendship_status[agent_left_name] = True
                friendship_status[agent_right_name] = True

                print(f"{agent_left_name} and {agent_right_name} became friends!")

            else:
                friendship_status[agent_left_name] = False
                friendship_status[agent_right_name] = False

        # Handle an unpaired agent (if odd number of agents)
        if len(agents) % 2 == 1:
            last_agent = self.agents[agents[-1]]
            friendship_status[agents[-1]] = False
            print(f"{agents[-1]} has no pair and made no new friends.")

        return friendship_status

    def move_cursor(self, dx, dy):
        """Move the camera (background) instead of the cursor."""
        self.cursor_offset[0] -= dx * self.cursor_step * self.cursor_zoom
        self.cursor_offset[1] -= dy * self.cursor_step * self.cursor_zoom
        self.clamp()

    def draw_step_info(self):
        """Draws step information including time progression."""
        date_format = self.date_current.strftime('%d %B %Y').lstrip("0")
        font = pygame.font.Font(None, 36)

        # Calculate the current step in the day
        step_in_day = self.step_current
        step_text = f"Step: {step_in_day}"
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

    import os

    def get_positions_friends(self):
        activities = ["school", "vriend thuis", "vrije tijd"]
        all_positions = {}  # Change this to a dictionary instead of a list
        for activity in activities:
            file_path = os.path.join(self.root, "Data", "Input", "positions_friends", f"{activity}.txt")
            try:
                with open(file_path, "r") as f:
                    # Read the file and process each line as a tuple
                    positions = [tuple(map(int, line.strip().strip('(),').split(','))) for line in f.readlines()]
                    all_positions[activity] = positions
            except FileNotFoundError:
                print(f"\033[93mposities-activiteit-{activity} nog niet geschreven\033[0m")
                all_positions[activity] = []
            except ValueError as e:
                print(f"\033[91mError processing file for activity {activity}: {e}\033[0m")
                all_positions[activity] = []
        return all_positions

    def get_agents(self):
        agents = []  # Store agents in a list
        agent_counter = 0  # To keep track of agent names from 0 to total count

        for age, count in self.age_counts.items():  # Loop through age and count
            for _ in range(count):
                agents.append(Agent(
                    name=agent_counter,  # Assign sequential name
                    age=age,  # Assign the correct age from the dictionary
                    positions_color=self.positions_color,
                    root=self.root,
                    agents_count=self.agents_count
                ))
                agent_counter += 1
        return agents

    def set_time(self):
        self.step += 1
        self.step_current = self.step % self.steps_per_day  # Compute current step first
        days_elapsed = self.step // self.steps_per_day  # Compute elapsed days
        self.date_current = self.start_date + timedelta(days=days_elapsed)  # Update date

    def check_breakpoint(self):
        if self.breakpoint_time and self.date_current >= self.breakpoint_time:
            print(self)  # Trigger __str__ method if breakpoint is reached

    # def __repr__(self):
    # return f"{self.step_counter}, '{self.activity}'"

    def __str__(self):
        # Ensure the epoch only updates when a full epoch is completed
        current_epoch = (self.step - 1) // self.steps_per_epoch
        date_str = self.date_current.strftime("%Y-%m-%d")
        return f"{date_str} | step current: {self.step_current} | step: {self.step} | epoch:{current_epoch}"
