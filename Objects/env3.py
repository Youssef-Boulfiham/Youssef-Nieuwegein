from pathlib import Path
import itertools
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
    def __init__(self):
        self.random_number_generator = np.random.default_rng()
        self.get_random_number = lambda: round(self.random_number_generator.uniform(0.01, 0.99), 5)
        pygame.init()
        self.root = Path(__file__).parent.parent
        self.backgrounds = ["enviroment_background", "enviroment_grids", "enviroment_domains"]
        self.width_simulation = 500
        self.length_simulation = 700
        self.graph_width = 300
        self.graph_height = 300  # hoogte per grafiek
        self.input_height = 120
        self.padding = 20

        # totaal scherm breedte en hoogte
        self.total_width = self.width_simulation + self.padding + self.graph_width + 2 * self.padding
        self.total_length = self.input_height + self.padding + self.length_simulation + self.padding

        self.screen = pygame.display.set_mode((self.total_width, self.total_length))
        pygame.display.set_caption("Agent technology")
        self.background = self.load_background(self.backgrounds[0])
        self.cursor_position = [self.width_simulation // 2, self.length_simulation // 2]
        self.clock = pygame.time.Clock()
        self.cursor_zooms = [1.0, 2.0, 4.0]
        self.cursor_zoom = 1.0
        self.cursor_size = 10
        self.cursor_step = 10
        self.cursor_color = (255, 0, 0)
        self.cursor_offset = [0, 0]
        self.textbox_color = (181, 101, 29, 128)
        self.pictogram_cache = {}
        self.action_display = False
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
        # env
        self.domains = ["thuis", "school", "vriend thuis", "vrije tijd"]
        self.colors_domains = {"thuis": "red", "vrije tijd": "blue", "school": "green", "vriend thuis": "red dark"}

        # agents
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
        self.collisions = self.set_collision()  # TODO door pasen aan pathfinding
        self.positions = self.get_positions()
        self.agents = self.get_agents()
        self.image_agent = self.generate_agent_image("Agent_front")
        self.image_agent_width, self.image_agent_height = self.image_agent.get_size()
        # stepper en tijd
        self.font = pygame.font.Font(None, 24)
        # self.epochs = epochs
        self.steps_per_day = 4000
        self.step = 0
        self.step_current = 0
        # self.start_date = start_date
        # self.date_current = self.start_date
        self.time_current = dt_time(8, 0)

        # Rects aangepast voor layout met input boven, simulatie links onder input,
        # grafieken rechts van simulatie, grafieken onder elkaar
        self.input_panel_rect = pygame.Rect(0, 0, self.total_width, self.input_height)

        self.sim_panel_rect = pygame.Rect(
            self.padding,
            self.input_height + self.padding,
            self.width_simulation,
            self.length_simulation
        )
        self.graph1_panel_rect = pygame.Rect(
            self.width_simulation + 2 * self.padding,
            self.input_height + self.padding,
            self.graph_width,
            self.graph_height
        )
        self.graph2_panel_rect = pygame.Rect(
            self.width_simulation + 2 * self.padding,
            self.input_height + self.padding + self.graph_height + self.padding,
            self.graph_width,
            self.graph_height
        )

        self.variable1_data = [0] * 100
        self.variable2_data = [0] * 100
        self.max_data_points = 500

        self.mock_friends_made = False
        self.mock_substance_used = False

        self.current_window = 0

        self.action = "vrienden_maken"
        self.domain_agents_names, self.agents_positions_pairs = self.get_positions_pairs()
        self.input_agent_counts = ""  # Bijvoorbeeld: "10,10,10,10,10,10,10"
        self.input_epochs = ""  # Bijvoorbeeld: "4000"
        self.input_start_date = ""  # Bijvoorbeeld: "2025-01-01"
        self.input_end_date = ""  # Bijvoorbeeld: "2025-12-31"
        self.active_input = 1  # 1 = agent counts, 2 = epochs, 3 = start, 4 = end
        self.inputs_active = True
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.input_agent_counts = ""  # bv "10,10,10,10,10,10,10"
        self.input_epochs = ""  # bv "4000"
        self.input_start_date = ""  # bv "2025-01-01"
        self.input_end_date = ""  # bv "2025-12-31"
        self.active_input = 1  # Welk inputveld is actief (1 t/m 4)
        self.inputs_active = True  # Of we in inputmodus zitten of simulatie draaien

        # Startknop rect (positie en grootte)
        self.start_button_rect = pygame.Rect(self.total_width - 150, 10, 120, 40)

        # Variabelen voor start datum etc
        self.start_date = None
        self.end_date = None
        self.epochs = None

        # Fonts
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        print(';')

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if self.inputs_active:
                    self.handle_input_event(event)
                else:
                    self.handle_simulation_controls(event)

            self.screen.fill((50, 50, 50))  # algemene achtergrond

            self.draw_input_panel()  # input bovenaan

            if not self.inputs_active:
                self.draw_background()  # simulatie achtergrond + zoom
                self.draw_cursor()
                self.run_simulation_step()

                self.update_graph_data()
                self.draw_graphs()

            pygame.display.flip()
            self.clock.tick(30)

    def run_simulation_step(self):
        self.step += 1
        self.step_current = self.step % self.steps_per_day
        self.set_time()

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
            self.action = "middelen_gebruiken"
            self.middelen_gebruiken()
        elif self.step_current == 1550:
            self.action_display = True

        for agent in self.agents:
            target = self.agents_positions_pairs.get(agent.name,
                                                     agent.position_current) if self.action == "vrienden_maken" else None
            agent.step(self.action, target)
            self.draw_agent(agent.position_current)
            self.draw_textbox(agent.position_current, text="", action=agent.action)

        self.draw_step_info()
        self.draw_progress_cursor(self.screen, self.step_current, 2000, self.width_simulation, self.length_simulation)

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
            self.random_number_generator.shuffle(indices)
            drinker_ids = set(self.random_number_generator.choice(indices, size=num_drinkers, replace=False))
            smoker_ids = set(self.random_number_generator.choice(indices, size=num_smokers, replace=False))
            for i in range(count):
                fixed_drinker = i in drinker_ids
                fixed_smoker = i in smoker_ids
                alcohol_resistance = self.get_random_number()
                smoking_resistance = self.get_random_number()
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
                    activities=self.domains,
                    collisions=self.collisions
                ))
                name_index += 1
        return agents

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

    def middelen_gebruiken(self):
        for substance in ["alcohol", "roken"]:
            pings = self.get_pings(self.substance_data[substance])
            for age, num_pings in pings.items():
                if num_pings == 0:
                    continue
                fixed_attr = f"fixed_{substance if substance == 'roken' else substance}"
                resistance_attr = f"{substance}_resistance"
                count_attr = f"{substance}_count"  #
                fixed_users = [a for a in self.agents if a.age == age and getattr(a, fixed_attr)]
                sorted_agents = sorted(fixed_users, key=lambda a: getattr(a, resistance_attr))
                candidates = []
                for agent in sorted_agents:
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
                    p=[chance for _, chance in normalized])
                for agent in selected_agents:
                    setattr(agent, count_attr, getattr(agent, count_attr) + 1)
                    agent.action = f"{substance}"
                    # print(f"Agent {agent.name} (age {agent.age}) used {substance}.")

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

    def get_positions(self):
        positions_activity = {}
        for activity in self.domains:
            activity_position = self.collisions[f"['{activity}']"]
            y_groups = defaultdict(list)
            for y in range(self.length_simulation):
                for x in range(0, self.width_simulation):
                    if not activity_position[y][x] and x % 16 == 0 and y % 16 == 0:
                        y_groups[y].append((x, y))  # Let op!: vanaf hier x, y
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

    def set_collision(self):
        """voor pathfinding"""
        domains = [[domain] for domain in self.domains] + \
                  [[domain1, 'black', domain2] for domain1, domain2 in itertools.product(self.domains, repeat=2)]
        colissions = {}
        for activity in domains:
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

    def load_background(self, background_image_file):
        background_image_file_path = self.root / "graphics" / f"{background_image_file}.png"
        if not background_image_file_path.parent.exists():
            background_image_file_path.parent.mkdir(parents=True, exist_ok=True)
        if not background_image_file_path.exists():
            print(f"File '{background_image_file_path}.png' not found. Creating a white background.")
            img = Image.new("RGB", (self.width_simulation, self.length_simulation), (255, 255, 255))
            img.save(background_image_file_path)
        return pygame.image.load(str(background_image_file_path)).convert()

    def move_cursor(self, dx, dy):
        self.cursor_offset[0] -= dx * self.cursor_step / self.cursor_zoom
        self.cursor_offset[1] -= dy * self.cursor_step / self.cursor_zoom
        self.clamp()

    def zoom(self, direction):
        old_zoom = self.cursor_zoom
        if direction == 1 and self.cursor_zoom < max(self.cursor_zooms):
            new_zoom = self.cursor_zooms[self.cursor_zooms.index(self.cursor_zoom) + 1]
        elif direction == -1 and self.cursor_zoom > min(self.cursor_zooms):
            new_zoom = self.cursor_zooms[self.cursor_zooms.index(self.cursor_zoom) - 1]
        else:
            return
        center_screen_x_sim = self.sim_panel_rect.width // 2
        center_screen_y_sim = self.sim_panel_rect.height // 2
        world_x = (center_screen_x_sim + self.cursor_offset[0]) / old_zoom
        world_y = (center_screen_y_sim + self.cursor_offset[1]) / old_zoom
        self.cursor_zoom = new_zoom
        self.cursor_offset[0] = world_x * self.cursor_zoom - center_screen_x_sim
        self.cursor_offset[1] = world_y * self.cursor_zoom - center_screen_y_sim
        self.clamp()
        time.sleep(0.2)

    def clamp(self):
        max_offset_x = max(0, self.width_simulation * self.cursor_zoom - self.width_simulation)
        max_offset_y = max(0, self.length_simulation * self.cursor_zoom - self.length_simulation)
        self.cursor_offset[0] = max(0, min(self.cursor_offset[0], max_offset_x))
        self.cursor_offset[1] = max(0, min(self.cursor_offset[1], max_offset_y))

    def draw_background(self):
        # Schaal achtergrond op basis van zoom
        scaled_width = int(self.width_simulation * self.cursor_zoom)
        scaled_height = int(self.length_simulation * self.cursor_zoom)
        scaled_bg = pygame.transform.scale(self.background, (scaled_width, scaled_height))

        # Positie achtergrond binnen simulatiepaneel, rekening houdend met pan (cursor_offset)
        bg_x = self.sim_panel_rect.x - self.cursor_offset[0]
        bg_y = self.sim_panel_rect.y - self.cursor_offset[1]

        # Clip tekenen binnen simulatiepaneel
        self.screen.set_clip(self.sim_panel_rect)
        self.screen.blit(scaled_bg, (bg_x, bg_y))
        self.screen.set_clip(None)  # Reset clipping

    def draw_cursor(self):
        cursor_rect = pygame.Rect(
            self.sim_panel_rect.x + self.sim_panel_rect.width // 2 - self.cursor_size // 2,
            self.sim_panel_rect.y + self.sim_panel_rect.height // 2 - self.cursor_size // 2,
            self.cursor_size,
            self.cursor_size
        )
        pygame.draw.ellipse(self.screen, self.cursor_color, cursor_rect)

    def draw_agent(self, coordinates):
        scale_factor = self.cursor_zoom

        screen_x = (coordinates[0] * scale_factor) - self.cursor_offset[0]
        screen_y = (coordinates[1] * scale_factor) - self.cursor_offset[1]

        scaled_image = pygame.transform.scale(
            self.image_agent,
            (int(self.image_agent_width * scale_factor), int(self.image_agent_height * scale_factor))
        )

        offset_x = -scaled_image.get_width() // 2
        offset_y = -scaled_image.get_height() // 2

        self.screen.blit(scaled_image, (screen_x + offset_x, screen_y + offset_y))

    def draw_textbox(self, position, text, action):
        text = str(text).strip()
        show_pictogram = self.action_display and bool(action)

        if not text and not show_pictogram:
            return

        text_surface = self.font.render(text, True, (255, 255, 255)) if text else None
        text_width, text_height = text_surface.get_size() if text_surface else (0, 0)

        pictogram_width = 24 if show_pictogram else 0
        pictogram_height = 24

        box_width = text_width + pictogram_width + 4
        box_height = max(text_height + 4, 28)

        screen_x_sim = (position[0] * self.cursor_zoom) - self.cursor_offset[0]
        screen_y_sim = (position[1] * self.cursor_zoom) - self.cursor_offset[1]

        box_x = screen_x_sim - box_width // 2
        box_y = screen_y_sim - 30 - box_height

        if show_pictogram and action not in self.pictogram_cache:
            mock_pictogram_path = self.root / "graphics" / f"mock_{action}.png"
            if not mock_pictogram_path.exists():
                if not mock_pictogram_path.parent.exists():
                    mock_pictogram_path.parent.mkdir(parents=True, exist_ok=True)
                mock_pic_img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
                draw_pic = ImageDraw.Draw(mock_pic_img)
                if action == "alcohol":
                    draw_pic.rectangle([(5, 5), (19, 19)], fill=(255, 0, 0))
                elif action == "roken":
                    draw_pic.ellipse([(5, 5), (19, 19)], fill=(0, 255, 0))
                elif action == "checkmark":
                    draw_pic.line([(5, 12), (10, 18), (19, 5)], fill=(0, 255, 0), width=3)
                elif action == "moving":
                    draw_pic.text((0, 0), "->", fill=(255, 255, 255), font=self.font)
                else:
                    draw_pic.rectangle([(5, 5), (19, 19)], fill=(100, 100, 100))
                mock_pic_img.save(mock_pictogram_path)
            self.pictogram_cache[action] = pygame.transform.scale(
                pygame.image.load(str(mock_pictogram_path)).convert_alpha(),
                (pictogram_width, pictogram_height)
            )

        textbox_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        textbox_surface.fill(self.textbox_color)
        self.screen.blit(textbox_surface, (box_x, box_y))

        text_x = box_x + 2
        if show_pictogram:
            self.screen.blit(self.pictogram_cache[action], (text_x, box_y + (box_height - pictogram_height) // 2))
            text_x += pictogram_width

        if text_surface:
            self.screen.blit(text_surface, (text_x, box_y + (box_height - text_height) // 2))

    def draw_step_info(self):
        time_string = self.time_current.strftime("%H:%M")
        weekday = self.date_current.strftime("%A").lower()
        day = self.date_current.strftime("%d").lstrip("0")
        month = self.date_current.strftime("%B").lower()
        year = self.date_current.strftime("%Y")
        date_line = f"{time_string} {weekday} {day} {month} {year}"

        activity_line = f"Var1: {self.variable1_data[-1] if self.variable1_data else 0} | Var2: {self.variable2_data[-1] if self.variable2_data else 0}"

        step_line = f"step: {self.step_current} / {self.steps_per_day}"

        font = pygame.font.Font(None, 28)
        surfaces = [
            font.render(date_line, True, (255, 255, 255)),
            font.render(activity_line, True, (255, 255, 255)),
            font.render(step_line, True, (255, 255, 255))
        ]

        padding = 10
        line_spacing = 5
        box_x, box_y = 10, 10
        box_width = max(surface.get_width() for surface in surfaces) + 2 * padding
        box_height = sum(surface.get_height() for surface in surfaces) + (len(surfaces) + 1) * padding + (
                len(surfaces) - 1) * line_spacing

        pygame.draw.rect(self.screen, (139, 69, 19), (box_x, box_y, box_width, box_height), border_radius=10)

        y = box_y + padding
        for surface in surfaces:
            self.screen.blit(surface, (box_x + padding, y))
            y += surface.get_height() + line_spacing

    def draw_progress_cursor(self, screen, current_step, max_steps, sim_panel_width, sim_panel_height):
        stick_height = 34
        stick_width = 3
        y_pos = int(sim_panel_height * 0.947)

        current_step_daily = current_step % max_steps
        x_pos_start = 20
        x_pos_end = sim_panel_width - 20
        progress_bar_length = x_pos_end - x_pos_start

        if max_steps > 0:
            x_pos = x_pos_start + int((current_step_daily / max_steps) * progress_bar_length)
        else:
            x_pos = x_pos_start

        pygame.draw.rect(screen, (255, 0, 0), (x_pos, y_pos, stick_width, stick_height))

    def generate_agent_image(self, agent_image_file):
        """
        Generates and saves a 16x16 square agent image if it doesn't already exist.
        """
        agent_image_file_path = self.root / "graphics" / f"{agent_image_file}.png"
        if not agent_image_file_path.exists():
            print(f"File '{agent_image_file_path}' not found. Creating a 16x16 square agent.16x16 square agent image saved")
            if not agent_image_file_path.parent.exists():
                agent_image_file_path.parent.mkdir(parents=True, exist_ok=True)
            agent_img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
            draw_agent = ImageDraw.Draw(agent_img)
            draw_agent.rectangle([(0, 0), (15, 15)], fill=(0, 150, 200))
            agent_img.save(agent_image_file_path)
        return pygame.image.load(str(agent_image_file_path)).convert_alpha()

    def update_graph_data(self):
        last_val1 = self.variable1_data[-1] if self.variable1_data else 0
        last_val2 = self.variable2_data[-1] if self.variable2_data else 0

        self.variable1_data.append(last_val1 + 1)
        if self.step % 2 == 0:
            self.variable2_data.append(last_val2 + 1)
        else:
            self.variable2_data.append(last_val2)

        if len(self.variable1_data) > self.max_data_points:
            self.variable1_data.pop(0)
            self.variable2_data.pop(0)

    def draw_graphs(self):
        # grafiek 1 achtergrond
        pygame.draw.rect(self.screen, (230, 230, 230), self.graph1_panel_rect)
        # teken hier grafiek 1 data binnen graph1_panel_rect

        # grafiek 2 achtergrond
        pygame.draw.rect(self.screen, (230, 230, 230), self.graph2_panel_rect)
        # teken hier grafiek 2 data binnen graph2_panel_rect

    def draw_single_graph(self, rect, data, line_color, title):
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
        title_surface = self.font.render(title, True, (255, 255, 255))
        self.screen.blit(title_surface, (rect.x + rect.width // 2 - title_surface.get_width() // 2, rect.y + 10))
        graph_padding_inner = 30
        graph_rect = pygame.Rect(rect.x + graph_padding_inner, rect.y + graph_padding_inner + 20,
                                 rect.width - (2 * graph_padding_inner), rect.height - (2 * graph_padding_inner) - 20)
        pygame.draw.rect(self.screen, (30, 30, 30), graph_rect, 0)
        if not data:
            return
        max_val = max(data) if data else 1
        if max_val < 5: max_val = 5
        for i in range(0, int(max_val) + 1, max(1, int(max_val // 4))):
            if i > max_val: continue
            y_label = self.font.render(str(i), True, (200, 200, 200))
            y_pos = graph_rect.bottom - (i / max_val) * graph_rect.height
            self.screen.blit(y_label, (graph_rect.x - y_label.get_width() - 5, y_pos - y_label.get_height() // 2))
        num_points = len(data)
        if num_points > 1:
            labels_to_draw = [0, num_points // 2, num_points - 1]
            for idx in labels_to_draw:
                x_label = self.font.render(str(idx), True, (200, 200, 200))
                x_pos = graph_rect.x + (idx / (num_points - 1)) * graph_rect.width
                self.screen.blit(x_label, (x_pos - x_label.get_width() // 2, graph_rect.bottom + 5))
        points = []
        for i, value in enumerate(data):
            x = graph_rect.x + (i / (len(data) - 1)) * graph_rect.width if len(
                data) > 1 else graph_rect.x + graph_rect.width / 2
            y = graph_rect.bottom - (value / max_val) * graph_rect.height
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(self.screen, line_color, False, points, 2)
        elif len(points) == 1:
            pygame.draw.circle(self.screen, line_color, points[0], 3)

    def set_time(self):
        self.step += 1
        self.step_current = self.step % self.steps_per_day
        days_elapsed = self.step // self.steps_per_day
        self.date_current = self.start_date + timedelta(days=days_elapsed)

        steps_per_hour = self.steps_per_day / 13
        hour_offset = self.step_current / steps_per_hour
        hour = int(8 + hour_offset)
        minute = int((hour_offset % 1) * 60)
        self.time_current = dt_time(hour % 24, minute)

    def draw_input_screen(self):
        # Scherm vullen
        self.screen.fill((50, 50, 50))

        # Tekst en inputvakken tekenen
        labels = ["Aantal agents (comma separated):", "Aantal epochs (int):", "Startdatum (YYYY-MM-DD):",
                  "Einddatum (YYYY-MM-DD):"]
        inputs = [self.input_agent_counts, self.input_epochs, self.input_start_date, self.input_end_date]

        y_start = 20
        for i, label in enumerate(labels):
            color = (255, 255, 255)
            label_surf = self.small_font.render(label, True, color)
            self.screen.blit(label_surf, (20, y_start + i * 60))

            # input vak tekenen
            input_rect = pygame.Rect(20, y_start + 25 + i * 60, self.total_width - 40, 30)
            pygame.draw.rect(self.screen, (255, 255, 255), input_rect, 2)

            # input tekst
            input_text = self.small_font.render(inputs[i], True, (255, 255, 255))
            self.screen.blit(input_text, (input_rect.x + 5, input_rect.y + 5))

            # achtergrond van actieve input veld
            if self.active_input == i + 1:
                pygame.draw.rect(self.screen, (255, 255, 255), input_rect, 2)

        # Start knop tekenen
        pygame.draw.rect(self.screen, (0, 128, 0), self.start_button_rect)
        start_text = self.font.render("Start simulatie", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(start_text, text_rect)

    def _draw_display_screen(self):
        """Draws the elements for the display screen."""
        self.screen.fill((0, 50, 0))  # Dark green background

        # Display Input 1
        display_text1 = self.font.render(f"Input 1: {self.input1}", True, (255, 255, 255))
        self.screen.blit(display_text1, (50, 100))

        # Display Input 2
        display_text2 = self.font.render(f"Input 2: {self.input2}", True, (255, 255, 255))
        self.screen.blit(display_text2, (50, 200))

        # Optional: Instruction to quit
        quit_instruction = self.small_font.render("Press ESC to quit", True, (150, 150, 150))
        self.screen.blit(quit_instruction, (50, 500))

    def _handle_input_screen_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.active_input < 4:
                    self.active_input += 1
                else:
                    self.current_window = 1  # Start simulatie
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == 1:
                    self.input_agent_counts = self.input_agent_counts[:-1]
                elif self.active_input == 2:
                    self.input_epochs = self.input_epochs[:-1]
                elif self.active_input == 3:
                    self.input_start_date = self.input_start_date[:-1]
                elif self.active_input == 4:
                    self.input_end_date = self.input_end_date[:-1]
            else:
                if self.active_input == 1:
                    self.input_agent_counts += event.unicode
                elif self.active_input == 2:
                    self.input_epochs += event.unicode
                elif self.active_input == 3:
                    self.input_start_date += event.unicode
                elif self.active_input == 4:
                    self.input_end_date += event.unicode

    def set_agents_actions_false(self):
        for agent in self.agents:
            agent.action = False

    def plot_positions(self, activity, positions):
        """Plots positions with numbered labels and pair-based background colors using rainbow palette."""
        img = Image.new("RGB", (self.width_simulation, self.length_simulation), "white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=24)  # Adjust size if needed
        except IOError:
            font = ImageFont.load_default()
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

    def handle_input_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button_rect.collidepoint(event.pos):
                self.try_start_simulation()

    def handle_simulation_controls(self, event):
        # Hier kun je toetsen of muis events verwerken die tijdens simulatie gelden
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Esc keert terug naar input scherm om aanpassingen te doen
                self.inputs_active = True

    def gather_input(self):
        # Achtergrond voor inputveld
        input_bg_color = (50, 50, 50)
        input_rect_height = 40
        padding = 10

        # Clear input gebied boven simulatie
        input_area_rect = pygame.Rect(0, 0, self.total_width, input_rect_height * 4 + padding * 5)
        pygame.draw.rect(self.screen, (30, 30, 30), input_area_rect)

        # Labels en tekst invoer per veld
        labels = ["Agent Counts (comma-separated):", "Epochs (steps per day):", "Start Date (YYYY-MM-DD):", "End Date (YYYY-MM-DD):"]
        inputs = [self.input_agent_counts, self.input_epochs, self.input_start_date, self.input_end_date]

        for i, (label, text) in enumerate(zip(labels, inputs)):
            y = padding + i * (input_rect_height + padding)

            # Label
            label_surface = self.small_font.render(label, True, (200, 200, 200))
            self.screen.blit(label_surface, (padding, y))

            # Input box achtergrond
            box_rect = pygame.Rect(300, y, 400, input_rect_height)
            pygame.draw.rect(self.screen, input_bg_color, box_rect)

            # Tekst in input box
            input_surface = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(input_surface, (box_rect.x + 5, box_rect.y + 8))

            # Optioneel: teken een kader om de actieve input
            if self.active_input == i + 1:
                pygame.draw.rect(self.screen, (255, 255, 0), box_rect, 2)

    def try_start_simulation(self):
        # Default waarden instellen
        default_agent_counts = [10, 10, 10, 10, 10, 10, 10]
        default_epochs = 4000
        default_start_date = datetime.strptime("2025-01-01", "%Y-%m-%d").date()
        default_end_date = datetime.strptime("2025-12-31", "%Y-%m-%d").date()

        # Agent counts
        if self.input_agent_counts.strip() == "":
            counts = default_agent_counts
        else:
            try:
                counts = [int(x.strip()) for x in self.input_agent_counts.split(",") if x.strip() != ""]
                if not counts:
                    counts = default_agent_counts
            except Exception:
                counts = default_agent_counts

        # Epochs
        if self.input_epochs.strip() == "":
            epochs = default_epochs
        else:
            try:
                epochs = int(self.input_epochs)
            except Exception:
                epochs = default_epochs

        # Start datum
        if self.input_start_date.strip() == "":
            start_date = default_start_date
        else:
            try:
                start_date = datetime.strptime(self.input_start_date, "%Y-%m-%d").date()
            except Exception:
                start_date = default_start_date

        # Eind datum
        if self.input_end_date.strip() == "":
            end_date = default_end_date
        else:
            try:
                end_date = datetime.strptime(self.input_end_date, "%Y-%m-%d").date()
            except Exception:
                end_date = default_end_date

        if start_date > end_date:
            # Wissel om, of vul default in
            start_date, end_date = default_start_date, default_end_date

        # Zet alles in self
        self.agent_counts = counts
        self.epochs = epochs
        self.start_date = start_date
        self.end_date = end_date

        print(f"Simulatie start met {counts} agents, {epochs} epochs, van {start_date} tot {end_date}")

        # Zet inputs niet meer actief, start simulatie
        self.inputs_active = False
        return True

    def draw_input_panel(self):
        # teken achtergrond inputpaneel
        pygame.draw.rect(self.screen, (200, 200, 200), self.input_panel_rect)

        # tekstlabels en inputvelden, bijvoorbeeld:
        font = self.small_font
        x = self.input_panel_rect.x + 10
        y = self.input_panel_rect.y + 10

        self.screen.blit(font.render("Agent counts (bijv. 10,10,10...):", True, (0,0,0)), (x, y))
        # hier teken je ook input box of tekst met self.input_agent_counts ernaast

        self.screen.blit(font.render("Epochs:", True, (0,0,0)), (x, y + 30))
        # en input_epochs veld tekenen

        self.screen.blit(font.render("Start date (YYYY-MM-DD):", True, (0,0,0)), (x+250, y))
        # input_start_date tekenen

        self.screen.blit(font.render("End date (YYYY-MM-DD):", True, (0,0,0)), (x+250, y + 30))
        # input_end_date tekenen

        # Start knop (een rechthoek met tekst)
        start_button_rect = pygame.Rect(self.input_panel_rect.right - 120, self.input_panel_rect.y + 20, 100, 40)
        pygame.draw.rect(self.screen, (0, 120, 0), start_button_rect)
        self.screen.blit(font.render("Start", True, (255, 255, 255)), (start_button_rect.x + 20, start_button_rect.y + 10))

        # Sla deze rect op om muisklik op knop te detecteren
        self.start_button_rect = start_button_rect


a = Env()
a.run()
