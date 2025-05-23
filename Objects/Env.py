from PIL import ImageDraw, ImageFont
from pathlib import Path
from collections import defaultdict
import random
import os
import numpy as np
import pygame
import time
from PIL import Image
from Objects.Agent import Agent
from datetime import timedelta


class Env:
    def __init__(self, start_date, epochs, steps_per_day=4000, breakpoint_time=None):
        self.activities = ["thuis", "school", "vriend thuis", "vrije tijd"]
        self.colors_activities = ["red", "green", "blue", "red dark"]
        self.activity_colors = {"thuis": "red", "vrije tijd": "blue", "school": "green", "vriend thuis": "red dark"}
        self.name_activity = {}
        self.action = False
        self.activity = "idle"
        # self.age_counts = {12: 1, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0}
        # self.age_counts = {12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1}
        # self.age_counts = {12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5, 18: 5}
        self.age_counts = {12: 10, 13: 10, 14: 10, 15: 10, 16: 10, 17: 10, 18: 10}
        self.binge_percentages = {12: 1, 13: 3, 14: 6, 15: 14, 16: 36, 17: 48, 18: 86}
        self.fixed_drinker_counts = {12: 6, 13: 6, 14: 6, 15: 6, 16: 8, 17: 8, 18: 10}
        self.colors = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "thuis": (255, 0, 0),
            "school": (0, 255, 0),
            "vrije tijd": (0, 0, 255),
            "grey": (128, 128, 128),
            "brown": (143, 110, 26),
            "vriend thuis": (155, 0, 0)
        }
        self.root = Path(__file__).parent.parent
        self.agents_count = sum(self.age_counts.values())
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
        self.background = pygame.image.load(os.path.join(self.root, "graphics", "enviroment_background.png"))
        # self.background = pygame.image.load(os.path.join(self.root, "graphics", "enviroment_raster.png"))
        # self.background = pygame.image.load(os.path.join(self.root, "graphics", "enviroment_activity.png"))
        self.width, self.lenght = self.background.get_size()
        self.cursor_position = [self.width // 2, self.lenght // 2]
        self.screen = pygame.display.set_mode((self.width, self.lenght))
        self.clock = pygame.time.Clock()
        #
        self.collisions = self.set_collision()  # TODO door pasen aan pathfinding
        self.positions = self.get_positions()
        # agent
        self.agents = self.get_agents()
        self.image_agent = pygame.image.load(str(self.root / "graphics" / "Agent_front.png")).convert_alpha()
        self.image_agent_width, self.image_agent_height = self.image_agent.get_size()
        self.font = pygame.font.Font(None, 24)  # Load font once
        # step
        self.epochs = epochs
        self.steps_per_day = steps_per_day
        self.steps_per_week = self.steps_per_day * 7
        self.steps_per_epoch = self.steps_per_week * 4
        self.step = self.steps_per_epoch - self.steps_per_day -1
        self.step_current = self.step
        # time
        self.start_date = start_date
        self.date_current = start_date
        while True:
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
            #
            self.activity = "idle"
            if self.step_current == 0:
                self.activity = "activiteit_kiezen"
            elif self.step_current == 1000:
                self.activity = "vrienden_maken"
                self.activities_agents_names, self.agents_positions_pairs = self.get_positions_pairs()
            elif self.step_current == 1250:
                self.vrienden_maken()
                self.action = True
            elif self.step_current == 1500:
                self.set_agents_actions_false()
                self.action = False
                self.activity = "middelen_gebruiken"
                self.middelen_gebruiken()
            elif self.step_current == 2000:
                self.activity = "activiteit_kiezen"
            elif self.step_current == 3000:
                self.activity = "vrienden_maken"
                self.activities_agents_names, self.agents_positions_pairs = self.get_positions_pairs()
            elif self.step_current == 3250:
                self.vrienden_maken()
                self.action = True
            elif self.step_current == 3500:
                self.set_agents_actions_false()
                self.action = False
                # self.activity = "middelen_gebruiken"
                #     # self.middelen_gebruiken()
            for agent in self.agents:
                agent_position_end = None
                if self.activity == "vrienden_maken":
                    agent_position_end = self.agents_positions_pairs.get(agent.name, agent.position_current)
                agent.step(self.activity, agent_position_end)
                self.draw_agent(agent.position_current)
                self.draw_textbox(agent.position_current, text=f"", action=agent.action)
            self.draw_step_info()
            # print(self)
            self.set_time()
            #
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def middelen_gebruiken(self):
        """TEST DIT IN NOTEBOOK"""
        # TODO: koppelen inefficient, duppelop
        pings = self.get_pings()  # {age: number_of_drinkers_this_epoch}

        for age, num_pings in pings.items():
            if num_pings == 0:
                continue

            # Get all agents of this age
            agents_of_age = [agent for agent in self.agents if agent.age == age]

            # Sort agents by resistance (lowest first)
            agents_sorted = sorted(agents_of_age, key=lambda agent: agent.resistance)

            # Select the agents with the lowest resistance to assign pings
            for agent in agents_sorted[:num_pings]:
                agent.substance_count += 1  # Track usage
                print(f"Agent {agent.name} (age {agent.age}) used a substance.")

        return 0

    def get_pings(self):
        """
        Returns a dictionary {age: number_of_drinkers_this_epoch} for the given epoch.
        geeft drinkers terug
        """
        age_counts = {12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5, 18: 5}
        binge_percentages = {12: 0.8, 13: 2.5, 14: 5.5, 15: 13, 16: 37, 17: 50, 18: 88}
        fixed_drinker_counts = {12: 3, 13: 3, 14: 3, 15: 3, 16: 4, 17: 4, 18: 5}
        results = {}

        for age, count in age_counts.items():
            num_drinkers = fixed_drinker_counts[age]
            binge_percentage = binge_percentages[age]

            # Willekeurige drinkers aanwijzen
            is_drinker = np.zeros(count, dtype=bool)
            is_drinker[:num_drinkers] = True
            np.random.shuffle(is_drinker)

            # Weerstand toekennen aan drinkers
            resistance = np.zeros(count)
            resistances = np.random.uniform(0.05, 0.95, size=num_drinkers)
            np.random.shuffle(resistances)

            index = 0
            for i in range(count):
                if is_drinker[i]:
                    resistance[i] = resistances[index]
                    index += 1

            # Genereer één ping-waarde voor deze epoch
            # Voeg ruis toe aan het percentage
            adjusted_percentage = max(0, min(binge_percentage + np.random.normal(0, 1.5), 100))
            mean_total_pings = adjusted_percentage / 100 * num_drinkers
            std_dev = max(1, mean_total_pings * np.random.uniform(0.08, 0.15))

            # Genereer waarde voor deze specifieke epoch
            # GAUSSIAN DISTRIBUTION
            ping_value = int(np.random.normal(mean_total_pings, std_dev))
            ping_value = max(0, min(ping_value, num_drinkers))

            if ping_value > 0:
                drinker_indices = np.where(is_drinker)[0]
                weights = np.array([1.0 - resistance[i] for i in drinker_indices])
                weights /= weights.sum()
                selected = np.random.choice(drinker_indices, ping_value, replace=False, p=weights)
                results[age] = len(selected)
            else:
                results[age] = 0

        return results

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
        pictogram_width = 12 if show_pictogram else 0  # Half of 24
        pictogram_height = 12  # Half of 24
        box_width = text_width + pictogram_width + 4
        box_height = max(text_height + 4, 24)

        # Calculate position
        screen_x = position[0] * self.cursor_zoom - self.cursor_offset[0]
        screen_y = position[1] * self.cursor_zoom - self.cursor_offset[1]
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
                    (pictogram_width, pictogram_height)
                )
            self.screen.blit(self.pictogram_cache[action], (text_x, box_y + (box_height - pictogram_height) // 2))
            text_x += pictogram_width

        # Draw text if available
        if text_surface:
            self.screen.blit(text_surface, (text_x, box_y + (box_height - text_height) // 2))

    def get_positions(self):
        positions_activity = {}
        for activity in self.activities:
            activity_position = self.collisions[f"['{activity}']"]
            y_groups = defaultdict(list)
            for y in range(self.lenght):
                for x in range(0, self.width):
                    if not activity_position[y][x] and x % 16 == 0 and y % 16 == 0:
                        y_groups[y].append((x, y))  # Let op!: vanag hier x, y
            positions = []
            for y in y_groups:
                group = y_groups[y]
                for i in range(0, len(group), 2):
                    if i + 1 < len(group):
                        positions.append(group[i])
                        positions.append(group[i + 1])
            positions = sorted(positions, key=lambda pos: (pos[1], pos[0]))
            positions = [(positions[i], positions[i + 1])
                                  for i in range(0, len(positions) - 1, 2)]
            random.shuffle(positions)
            positions = [coord for pair in positions for coord in pair]
            positions_activity[activity] = positions
            self.plot_positions(activity, positions)
        return positions_activity

    def get_positions_pairs(self):
        # Sort agents per activity
        activities_agents_names = {"vrije tijd": [], "school": [], "vriend thuis": []}
        for agent in self.agents:
            if agent.activity != "thuis":
                activities_agents_names[agent.activity].append(agent.name)

        agents_positions_pairs = {}
        for activity, agent_names in activities_agents_names.items():
            for i in range(0, len(agent_names) & ~1, 2):
                # print(self.positions[activity][i], self.positions[activity][i + 1])
                agents_positions_pairs[agent_names[i]] = self.positions[activity][i]
                agents_positions_pairs[agent_names[i + 1]] = self.positions[activity][i + 1]
        return activities_agents_names, agents_positions_pairs

    def vrienden_maken(self):
        friendship_status = {}
        for activity, agent_names in self.activities_agents_names.items():
            for i in range(0, len(agent_names) & ~1, 2):
                # print(activity, agent_names[i], agent_names[i + 1])
                agent_left = self.agents[agent_names[i]]
                agent_right = self.agents[agent_names[i + 1]]

                if agent_left.friend_request.get(agent_right.name, 0) < 5 and \
                        agent_right.name not in agent_left.friends and \
                        len(agent_left.friends) < 5 and len(agent_right.friends) < 5 and \
                        random.getrandbits(1):
                    agent_left.friends.append(agent_right.name)
                    agent_right.friends.append(agent_left.name)
                    agent_left.action, agent_right.action = "checkmark", "checkmark"
                    friendship_status[agent_left.name] = True
                    friendship_status[agent_right.name] = True
                    # print(f"{agent_left.name} and {agent_right.name} became friends!")
                else:
                    friendship_status[agent_left.name] = False
                    friendship_status[agent_right.name] = False
        return friendship_status

    def move_cursor(self, dx, dy):
        """Move the camera (background) instead of the cursor."""
        # Apply zoom to movement deltas
        self.cursor_offset[0] -= dx * self.cursor_step * self.cursor_zoom
        self.cursor_offset[1] -= dy * self.cursor_step * self.cursor_zoom

        # Clamp to prevent moving beyond bounds
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
        max_offset_y = max(0, self.lenght * self.cursor_zoom - self.lenght)

        self.cursor_offset[0] = max(0, min(self.cursor_offset[0], max_offset_x))
        self.cursor_offset[1] = max(0, min(self.cursor_offset[1], max_offset_y))

    def draw_background(self):
        """Render scaled background at adjusted position."""
        scaled_bg = pygame.transform.scale(self.background,
                                           (int(self.width * self.cursor_zoom), int(self.lenght * self.cursor_zoom)))
        bg_x = -self.cursor_offset[0]
        bg_y = -self.cursor_offset[1]
        self.screen.blit(scaled_bg, (bg_x, bg_y))

    def draw_cursor(self):
        """Draw cursor at center of screen."""
        cursor_rect = pygame.Rect(
            self.width // 2 - self.cursor_size // 2,
            self.lenght // 2 - self.cursor_size // 2,
            self.cursor_size,
            self.cursor_size
        )
        pygame.draw.ellipse(self.screen, self.cursor_color, cursor_rect)

    def draw_agent(self, coordinates):
        scale_factor = self.cursor_zoom

        # Define your offsets for adjusting position
        offset_x = -4  # Adjust this value to your desired horizontal offset
        offset_y = -16 # Adjust this value to your desired vertical offset

        # Swap x and y axis to match the movement and zoom behavior
        x_pos = (coordinates[0] * scale_factor) - self.cursor_offset[
            0] - self.image_agent_width // 2 + offset_x  # Adjust x_pos with offset_x
        y_pos = (coordinates[1] * scale_factor) - self.cursor_offset[
            1] - self.image_agent_height // 2 + offset_y  # Adjust y_pos with offset_y

        # Scale the agent image based on the zoom factor
        scaled_image = pygame.transform.scale(
            self.image_agent,
            (int(self.image_agent_width * scale_factor), int(self.image_agent_height * scale_factor))
        )

        # Draw the agent on the screen
        self.screen.blit(scaled_image, (x_pos, y_pos))

    def set_collision(self):
        """voor pathfinding"""
        activity_combinations = [['thuis'], ['school'], ['vrije tijd'], ['vriend thuis'],
                                 ['thuis', 'black', 'school'],
                                 ['thuis', 'black', 'vrije tijd'],
                                 ['thuis', 'black', 'vriend thuis'],
                                 ['school', 'black', 'thuis'],
                                 ['school', 'black', 'vrije tijd'],
                                 ['school', 'black', 'vriend thuis'],
                                 ['vrije tijd', 'black', 'thuis'],
                                 ['vrije tijd', 'black', 'school'],
                                 ['vrije tijd', 'black', 'vriend thuis'],
                                 ['vriend thuis', 'black', 'thuis'],
                                 ['vriend thuis', 'black', 'school'],
                                 ['vriend thuis', 'black', 'vrije tijd']]
        colissions = {}
        for activity in activity_combinations:
            colors_rgb = [self.colors[color] for color in activity]
            image = Image.open(self.root / "graphics" / "enviroment_activity.png").convert("RGB")
            width, height = image.size
            pixels = image.load()
            sprite = np.zeros((height, width), dtype=int)
            for y in range(height):
                for x in range(width):
                    if pixels[x, y] not in colors_rgb:
                        sprite[y, x] = 1
            colissions[f"{activity}"] = sprite
        return colissions

    import numpy as np

    def get_agents(self):
        agents = []  # Store agents in a list
        agent_counter = 0  # To keep track of agent names from 0 to total count

        for age, count in self.age_counts.items():  # Loop through age and count
            # Generate evenly distributed resistance levels between 0.01 and 0.99
            resistance_levels = np.linspace(0.01, 0.99, count)

            for resistance in resistance_levels:
                agents.append(Agent(
                    name=agent_counter,  # Assign sequential name
                    age=age,  # Assign the correct age from the dictionary
                    resistance=resistance,  # Add resistance input here
                    positions_color=self.activity_colors,
                    root=self.root,
                    agents_count=self.agents_count,
                    positions=self.positions,
                    activities=self.activities,
                    collisions=self.collisions
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

    def plot_positions(self, activity, positions):
        """Plots the given positions on a 500x700 grid with numbered labels using Pillow."""
        img = Image.new("RGB", (self.width, self.lenght), "white")
        draw = ImageDraw.Draw(img)

        # Load default font
        font = ImageFont.load_default()

        # Draw numbers at each position
        for i, (x, y) in enumerate(positions):
            draw.text((x, y), str(i + 1), fill="black", font=font, anchor="mm")

        # Save the image
        save_path = self.root / "Data" / "Input" / f"{activity}.png"
        img.save(save_path)
        print(f"Plot saved: {save_path}")
