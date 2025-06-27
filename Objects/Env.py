from PIL import ImageDraw, ImageFont
from pathlib import Path
from collections import defaultdict
import random
import os
import numpy as np
import pygame
from PIL import Image
from Objects.Agent import Agent
from datetime import timedelta, time as dt_time, datetime
import time

class Env:
    def __init__(self, start_date, epochs, steps_per_day=4000):
        #
        # self.action_display = False
        # self.rng = np.random.default_rng()  # Centrale Mersenne Twister RNG
        # self.rn = lambda: round(self.rng.uniform(0.01, 0.99), 5)  # get rn
        # self.root = Path(__file__).parent.parent
        # self.cursor_zooms = [1.0, 2.0, 4.0]
        # self.cursor_zoom = 1.0
        # self.cursor_size = 10
        # self.cursor_step = 10
        # self.cursor_color = (255, 0, 0)
        # self.cursor_offset = [0, 0]
        # self.pictogram_cache = {}  # Cache for loaded pictograms
        # self.textbox_color = (181, 101, 29, 128)  # Textbox color with transparency
        # self.pictogram_size = (20, 20)  # Fixed pictogram size
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
        # env
        # TODO: clean code van
        self.colors_domains = {"thuis": "red", "vrije tijd": "blue", "school": "green", "vriend thuis": "red dark"}
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
        # TODO: tot
        self.collisions = self.set_collision()  # TODO door pasen aan pathfinding
        # agent
        self.domain = ["thuis", "school", "vriend thuis", "vrije tijd"]
        self.positions = self.get_positions()
        self.action = "idle"
        self.substance_data = {
            "alcohol": {
                "age_counts": {age: 10 for age in range(12, 19)},
                "percentages": {12: 0.8, 13: 2.5, 14: 5.5, 15: 13, 16: 37, 17: 50, 18: 88},
                "fixed_counts": {12: 6, 13: 6, 14: 6, 15: 6, 16: 8, 17: 8, 18: 10},
            },
            "roken": {
                "age_counts": {age: 10 for age in range(12, 19)},
                "percentages": {12: 0.5, 13: 1.2, 14: 4.0, 15: 9.1, 16: 30, 17: 45, 18: 72},
                "fixed_counts": {12: 5, 13: 5, 14: 6, 15: 6, 16: 7, 17: 8, 18: 9},
            }
        }
        self.agents_count = sum(self.substance_data["alcohol"]["age_counts"].values())
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
        # self.run_setup_menu()
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
            self.action = "idle"
            if self.step_current == 0:
                self.action = "activiteit_kiezen"
            elif self.step_current == 1000:
                self.action = "vrienden_maken"
                self.domain_agents_names, self.agents_positions_pairs = self.get_positions_pairs()
            elif self.step_current == 1250:
                self.vrienden_maken()
                self.action_display = True
            elif self.step_current == 1500:
                self.set_agents_actions_false()
                self.action_display = False
                self.action = "middelen_gebruiken"
                self.middelen_gebruiken()
            elif self.step_current == 1550:
                self.action_display = True
            elif self.step_current == 2000:
                self.set_agents_actions_false()
                self.step_current = False
                self.action = "activiteit_kiezen"
            elif self.step_current == 3000:
                self.action = "vrienden_maken"
                self.domain_agents_names, self.agents_positions_pairs = self.get_positions_pairs()
            elif self.step_current == 3250:
                self.vrienden_maken()
                self.action_display = True
            elif self.step_current == 3500:
                self.set_agents_actions_false()
                self.action_display = False
                # self.action = "middelen_gebruiken"
                #     # self.middelen_gebruiken()
            for agent in self.agents:
                agent_position_end = None
                if self.action == "vrienden_maken":
                    agent_position_end = self.agents_positions_pairs.get(agent.name, agent.position_current)
                agent.step(self.action, agent_position_end)
                self.draw_agent(agent.position_current)
                self.draw_textbox(agent.position_current, text=f"", action=agent.action)
            self.draw_step_info()
            self.draw_progress_cursor(self.screen, self.step_current, 2000, self.width, self.lenght)
            self.set_time()
            #
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

    def get_pings(self, substance_data):
        results = {}
        for age, count in substance_data["age_counts"].items():
            num_users = substance_data["fixed_counts"].get(age, 0)
            binge_percentage = substance_data["percentages"].get(age, 0)

            is_user = np.zeros(count, dtype=bool)
            is_user[:num_users] = True
            np.random.shuffle(is_user)

            resistance = np.zeros(count)
            resistances = np.random.uniform(0.05, 0.95, size=num_users)
            np.random.shuffle(resistances)

            idx = 0
            for i in range(count):
                if is_user[i]:
                    resistance[i] = resistances[idx]
                    idx += 1

            noise = np.random.normal(0, 2)
            expected = int(round((binge_percentage / 100) * num_users + noise))
            expected = max(0, min(expected, num_users))
            results[age] = expected
        return results

    def middelen_gebruiken(self):
        for substance in ["alcohol", "roken"]:
            pings = self.get_pings(self.substance_data[substance])
            for age, num_pings in pings.items():
                if num_pings == 0:
                    continue

                fixed_attr = f"fixed_{substance if substance == 'roken' else substance}"  # 'fixed_drinker' of 'fixed_smoker'
                resistance_attr = f"{substance}_resistance"  # bv 'alcohol_resistance' of 'smoking_resistance'
                count_attr = f"{substance}_count"  # bv 'alcohol_count' of 'smoking_count'

                fixed_users = [a for a in self.agents if a.age == age and getattr(a, fixed_attr)]
                sorted_agents = sorted(fixed_users, key=lambda a: getattr(a, resistance_attr))

                candidates = []
                for agent in sorted_agents:
                    # Init count attribuut als nog niet aanwezig
                    if not hasattr(agent, count_attr):
                        setattr(agent, count_attr, 0)
                    base_chance = 1 - getattr(agent, resistance_attr)
                    usage_count = getattr(agent, count_attr)
                    usage_factor = 1 + (usage_count * 0.1)
                    chance = base_chance * usage_factor
                    candidates.append((agent, chance))

                total_chance = sum(chance for _, chance in candidates)
                if total_chance == 0:
                    continue

                normalized = [(agent, chance / total_chance) for agent, chance in candidates]
                selected_agents = np.random.choice(
                    [agent for agent, _ in normalized],
                    size=min(num_pings, len(normalized)),
                    replace=False,
                    p=[chance for _, chance in normalized]
                )

                for agent in selected_agents:
                    setattr(agent, count_attr, getattr(agent, count_attr) + 1)
                    agent.action = f"{substance}"
                    print(f"Agent {agent.name} (age {agent.age}) used {substance}.")

    def set_agents_actions_false(self):
        for agent in self.agents:
            agent.action = False

    def draw_textbox(self, position, text, action):
        # Ensure text is a string and check if there's anything to display
        text = str(text).strip()
        show_pictogram = self.action_display and bool(action)

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
        for activity in self.domain:
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
                agents_positions_pairs[agent_names[i]] = self.positions[activity][i]
                agents_positions_pairs[agent_names[i + 1]] = self.positions[activity][i + 1]
        return activities_agents_names, agents_positions_pairs

    def vrienden_maken(self):
        for activity, agent_names in self.domain_agents_names.items():
            for i in range(0, len(agent_names) & ~1, 2):
                agent_left = self.agents[agent_names[i]]
                agent_right = self.agents[agent_names[i + 1]]

                if agent_left.friend_request.get(agent_right.name, 0) < 5 and \
                        agent_right.name not in agent_left.friends and \
                        len(agent_left.friends) < 5 and len(agent_right.friends) < 5 and \
                        random.getrandbits(1):
                    agent_left.friends.append(agent_right.name)
                    agent_right.friends.append(agent_left.name)
                    agent_left.action, agent_right.action = "checkmark", "checkmark"

    def move_cursor(self, dx, dy):
        """Move the camera (background) instead of the cursor."""
        # Apply zoom to movement deltas
        self.cursor_offset[0] -= dx * self.cursor_step * self.cursor_zoom
        self.cursor_offset[1] -= dy * self.cursor_step * self.cursor_zoom

        # Clamp to prevent moving beyond bounds
        self.clamp()

    def draw_step_info(self):
        # Format time and date
        if hasattr(self, "time_current"):
            time_string = self.time_current.strftime("%H:%M")
        else:
            time_string = "08:00"

        weekday = self.date_current.strftime("%A").lower()
        day = self.date_current.strftime("%d").lstrip("0")
        month = self.date_current.strftime("%B").lower()
        year = self.date_current.strftime("%Y")
        date_line = f"{time_string} {weekday} {day} {month} {year}"

        # Activity/substance line
        activity_line = "alcohol: 12 | nicotine: 5 | cannabis: 2"

        # Step line
        step_line = f"step: {self.step_current} / {self.step}"

        # Font setup
        font = pygame.font.Font(None, 28)
        surfaces = [
            font.render(date_line, True, (255, 255, 255)),
            font.render(activity_line, True, (255, 255, 255)),
            font.render(step_line, True, (255, 255, 255))
        ]

        # Calculate box dimensions
        padding = 10
        line_spacing = 5
        box_x, box_y = 10, 10
        box_width = max(surface.get_width() for surface in surfaces) + 2 * padding
        box_height = sum(surface.get_height() for surface in surfaces) + (len(surfaces) + 1) * padding + (
                    len(surfaces) - 1) * line_spacing

        # Draw background box
        pygame.draw.rect(self.screen, (139, 69, 19), (box_x, box_y, box_width, box_height), border_radius=10)

        # Blit lines
        y = box_y + padding
        for surface in surfaces:
            self.screen.blit(surface, (box_x + padding, y))
            y += surface.get_height() + line_spacing

    # def draw_step_info(self):
    #     """Draws step information including time progression."""
    #     date_format = self.date_current.strftime('%d %B %Y').lstrip("0")
    #     font = pygame.font.Font(None, 36)
    #
    #     # Calculate the current step in the day
    #     step_in_day = self.step_current
    #     step_text = f"Step: {step_in_day}"
    #     week_text = f"Date: {date_format}"
    #
    #     step_surface = font.render(step_text, True, (255, 255, 255))
    #     week_surface = font.render(week_text, True, (255, 255, 255))
    #
    #     base_width = 230
    #     box_width = int(base_width * 1.25)
    #     box_height = step_surface.get_height() + week_surface.get_height() + 30
    #     box_x, box_y = 10, 10
    #     text_x = box_x + 10
    #     step_y = box_y + 10
    #     week_y = step_y + step_surface.get_height() + 10
    #
    #     pygame.draw.rect(self.screen, (139, 69, 19), (box_x, box_y, box_width, box_height), border_radius=10)
    #     self.screen.blit(step_surface, (text_x, step_y))
    #     self.screen.blit(week_surface, (text_x, week_y))

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
        # TODO: comprihension moet automatisch
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


    def get_agents(self):
        agents = []

        names =  list(range(sum(self.substance_data["alcohol"]["age_counts"].values())))


        name_index = 0
        age_counts = self.substance_data["alcohol"]["age_counts"]
        fixed_drinker_counts = self.substance_data["alcohol"]["fixed_counts"]
        fixed_smoker_counts = self.substance_data["roken"]["fixed_counts"]

        for age in range(12, 19):
            count = age_counts.get(age, 0)
            num_drinkers = fixed_drinker_counts.get(age, 0)
            num_smokers = fixed_smoker_counts.get(age, 0)

            indices = list(range(count))
            self.rng.shuffle(indices)

            drinker_ids = set(self.rng.choice(indices, size=num_drinkers, replace=False))
            smoker_ids = set(self.rng.choice(indices, size=num_smokers, replace=False))

            for i in range(count):
                fixed_drinker = i in drinker_ids
                fixed_smoker = i in smoker_ids

                alcohol_resistance = self.rn()
                smoking_resistance = self.rn()

                agents.append(Agent(
                    name=names[name_index],
                    age=age,
                    fixed_drinker=fixed_drinker,
                    fixed_smoker=fixed_smoker,
                    alcohol_resistance=alcohol_resistance,
                    smoking_resistance=smoking_resistance,
                    positions_color=self.colors_domains,
                    root=self.root,
                    agents_count=70,
                    positions=self.positions,
                    activities=self.domain,
                    collisions=self.collisions
                ))

                name_index += 1

        return agents

    def set_time(self):
        self.step += 1
        self.step_current = self.step % self.steps_per_day
        days_elapsed = self.step // self.steps_per_day
        self.date_current = self.start_date + timedelta(days=days_elapsed)

        # Time between 08:00 and 21:00
        steps_per_hour = self.steps_per_day / 13  # From 08:00 to 21:00 = 13 hours
        hour_offset = self.step_current / steps_per_hour
        hour = int(8 + hour_offset)
        minute = int((hour_offset % 1) * 60)

        self.time_current = dt_time(hour % 24, minute)

    def check_breakpoint(self):
        if self.breakpoint_time and self.date_current >= self.breakpoint_time:
            print(self)  # Trigger __str__ method if breakpoint is reached

    # def __repr__(self):
    # return f"{self.step_counter}, '{self.action}'"

    def draw_progress_cursor(self, screen, current_step, max_steps, width, height):
        stick_height = 34
        stick_width = 3
        y_pos = int(height * 0.947)  # Position near the bottom

        # Clamp current_step to avoid overflow
        # current_step = max(0, min(current_step, max_steps))
        current_step = current_step % 2000
        # Calculate x-position as a fraction of width
        x_pos = int((current_step / max_steps) * width * 0.4) + 175

        pygame.draw.rect(screen, (255, 0, 0), (x_pos, y_pos, stick_width, stick_height))
        # print(current_step, x_pos)
        return current_step

    def __str__(self):
        # Ensure the epoch only updates when a full epoch is completed
        current_epoch = (self.step - 1) // self.steps_per_epoch
        date_str = self.date_current.strftime("%Y-%m-%d")
        return f"{date_str} | step current: {self.step_current} | step: {self.step} | epoch:{current_epoch}"

    def plot_positions(self, activity, positions):
        """Plots positions with numbered labels and pair-based background colors using rainbow palette."""
        img = Image.new("RGB", (self.width, self.lenght), "white")
        draw = ImageDraw.Draw(img)

        # Load a high-quality font for sharper text
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=24)  # Adjust size if needed
        except IOError:
            font = ImageFont.load_default()

        # Instelbare marges voor achtergrondvlakken
        horizontal_margin = 10
        vertical_margin = 8

        rainbow_colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]

        for i in range(0, len(positions), 2):
            if i + 1 >= len(positions):
                break

            (x1, y1), (x2, y2) = positions[i], positions[i + 1]

            left = min(x1, x2) - horizontal_margin
            right = max(x1, x2) + horizontal_margin
            top = min(y1, y2) - vertical_margin
            bottom = max(y1, y2) + vertical_margin

            color = rainbow_colors[(i // 2) % len(rainbow_colors)]
            draw.rectangle([left, top, right, bottom], fill=color)

        for i, (x, y) in enumerate(positions):
            draw.text((x, y), str(i + 1), fill="black", font=font, anchor="mm")

        save_path = self.root / "Data" / "Input" / f"{activity}.png"
        img.save(save_path, dpi=(300, 300))

    def run_setup_menu(self):
        input_active = None
        input_fields = {
            "start_step": {"value": "0", "rect": pygame.Rect(100, 100, 200, 32)},
            "start_date": {"value": "2024-01-01", "rect": pygame.Rect(100, 150, 200, 32)},
        }
        age_inputs = {
            age: {"value": str(self.substance_data["alcohol"]["age_counts"][age]),
                  "rect": pygame.Rect(100 + (age - 12) * 80, 250, 70, 32)}
            for age in range(12, 19)
        }

        font = pygame.font.Font(None, 28)
        done = False

        while not done:
            self.screen.fill((30, 30, 30))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    input_active = None
                    for key, field in input_fields.items():
                        if field["rect"].collidepoint(event.pos):
                            input_active = key
                    for age, field in age_inputs.items():
                        if field["rect"].collidepoint(event.pos):
                            input_active = age
                elif event.type == pygame.KEYDOWN and input_active is not None:
                    if event.key == pygame.K_RETURN:
                        input_active = None
                    elif event.key == pygame.K_BACKSPACE:
                        if input_active in input_fields:
                            input_fields[input_active]["value"] = input_fields[input_active]["value"][:-1]
                        else:
                            age_inputs[input_active]["value"] = age_inputs[input_active]["value"][:-1]
                    else:
                        char = event.unicode
                        if input_active in input_fields:
                            input_fields[input_active]["value"] += char
                        elif isinstance(input_active, int):
                            age_inputs[input_active]["value"] += char

            # Draw input boxes
            for key, field in input_fields.items():
                pygame.draw.rect(self.screen, (255, 255, 255), field["rect"], 2)
                text_surface = font.render(field["value"], True, (255, 255, 255))
                self.screen.blit(text_surface, (field["rect"].x + 5, field["rect"].y + 5))

            self.screen.blit(font.render("Start Step:", True, (255, 255, 255)), (10, 100))
            self.screen.blit(font.render("Start Date (YYYY-MM-DD):", True, (255, 255, 255)), (10, 150))
            self.screen.blit(font.render("Agents per Age:", True, (255, 255, 255)), (10, 200))

            for age, field in age_inputs.items():
                pygame.draw.rect(self.screen, (255, 255, 255), field["rect"], 2)
                text_surface = font.render(f"{age}: {field['value']}", True, (255, 255, 255))
                self.screen.blit(text_surface, (field["rect"].x + 5, field["rect"].y + 5))

            # Draw start button
            start_button = pygame.Rect(100, 320, 160, 40)
            pygame.draw.rect(self.screen, (0, 120, 0), start_button)
            self.screen.blit(font.render("Start Simulation", True, (255, 255, 255)), (110, 330))

            if pygame.mouse.get_pressed()[0] and start_button.collidepoint(pygame.mouse.get_pos()):
                # Apply user inputs
                self.start_step = int(input_fields["start_step"]["value"])
                self.step = self.start_step
                self.step_current = self.step % self.steps_per_day
                try:
                    self.start_date = pygame.time.strptime(input_fields["start_date"]["value"], "%Y-%m-%d")
                    self.start_date = time.strptime(input_fields["start_date"]["value"], "%Y-%m-%d")
                    self.start_date = datetime.strptime(input_fields["start_date"]["value"], "%Y-%m-%d").date()
                except:
                    self.start_date = datetime.strptime(input_fields["start_date"]["value"], "%Y-%m-%d").date()

                self.substance_data["alcohol"]["age_counts"] = {
                    age: max(0, int(field["value"])) for age, field in age_inputs.items()
                }
                done = True

            pygame.display.flip()
            self.clock.tick(30)
