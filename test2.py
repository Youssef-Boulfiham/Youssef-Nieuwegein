import pygame
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from collections import defaultdict
import random
from datetime import timedelta, time as dt_time, datetime
import time


# --- MOCK Agent Class (Simplified for demonstration) ---
class MockAgent:
    def __init__(self, name, start_pos=(0, 0)):
        self.name = name
        self.position_current = list(start_pos)  # Make it mutable
        self.action = False  # Mock action for textbox
        self.friends = []  # Mock friends list
        self.friend_request = {}  # Mock friend request

    def step(self, action, target_position=None):
        if target_position:
            self.position_current[0] += (target_position[0] - self.position_current[0]) * 0.1
            self.position_current[1] += (target_position[1] - self.position_current[1]) * 0.1
            self.position_current[0] = int(self.position_current[0])
            self.position_current[1] = int(self.position[1])
            self.action = "moving"
        else:
            self.position_current[0] += random.randint(-1, 1)
            self.position_current[1] += random.randint(-1, 1)
            self.position_current[0] = max(0, min(self.position_current[0], 500))
            self.position_current[1] = max(0, min(self.position_current[1], 700))
            self.action = "idle"


# --- MOCK Env Class (Adapted from your original) ---
class Env:
    def __init__(self, start_date, epochs, steps_per_day=4000):
        pygame.init()  # Initialize all pygame modules

        # --- IMPORTANT: Adjust self.root based on your actual project structure ---
        # If this script is in `your_project/some_folder/this_script.py`
        # and graphics are in `your_project/graphics/`, then:
        self.root = Path(__file__).parent.parent  # Assuming 'graphics' is one level up from this script

        # --- Define background options and load the first one (for initial dimensions) ---
        self.backgrounds = ["enviroment_background", "enviroment_grids", "enviroment_domains"]
        self.current_background_name = self.backgrounds[0]  # Use the first background

        # We need a temporary load *without* .convert() to get dimensions if background
        # isn't guaranteed to be 500x700 or known.
        # However, for this mock, we assume 500x700 for simplicity and direct calculation.
        # If your actual background images have varying sizes, you'd load temporarily
        # to get their size, THEN calculate total_width/length, THEN set_mode.
        # For now, let's keep it simple assuming a 500x700 simulation base.
        self.sim_width = 500
        self.sim_length = 700

        # Define dimensions for the simulation area and graph areas
        self.graph_width = 300
        self.padding = 20

        self.total_width = self.sim_width + (2 * self.graph_width) + (2 * self.padding)
        self.total_length = self.sim_length

        # --- THIS IS THE CRITICAL CHANGE: SET VIDEO MODE FIRST! ---
        self.screen = pygame.display.set_mode((self.total_width, self.total_length))
        pygame.display.set_caption("Omgeving Simulatie met Grafieken")  # Set caption after screen is ready

        # --- Now load and convert background images ---
        # Generate mock backgrounds if they don't exist
        for bg_name in self.backgrounds:
            path = self.root / "graphics" / f"{bg_name}.png"
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)  # Create graphics directory if missing
            if not path.exists():
                print(f"Generating mock background image: {bg_name}.png...")
                mock_img = Image.new("RGB", (self.sim_width, self.sim_length), (50, 100, 150))  # A blue-ish background
                draw = ImageDraw.Draw(mock_img)
                font_path = "arial.ttf" if os.path.exists("arial.ttf") else None
                try:
                    mock_font = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
                except IOError:
                    mock_font = ImageFont.load_default()
                if "background" in bg_name:
                    draw.text((150, 300), "Main Background", fill=(255, 255, 255), font=mock_font)
                elif "raster" in bg_name:
                    for i in range(0, self.sim_width, 50): draw.line([(i, 0), (i, self.sim_length)], fill=(0, 0, 0),
                                                                     width=1)
                    for i in range(0, self.sim_length, 50): draw.line([(0, i), (self.sim_width, i)], fill=(0, 0, 0),
                                                                      width=1)
                    draw.text((150, 300), "Raster Background", fill=(255, 255, 255), font=mock_font)
                elif "activity" in bg_name:
                    draw.rectangle([(50, 50), (200, 200)], fill=(255, 0, 0))  # Mock 'thuis'
                    draw.rectangle([(300, 400), (450, 600)], fill=(0, 0, 255))  # Mock 'vrije tijd'
                    draw.text((150, 300), "Activity Background", fill=(255, 255, 255), font=mock_font)

                mock_img.save(path)

        # Now, with the screen initialized, it's safe to load and convert
        self.background_image_path = self.root / "graphics" / f"{self.current_background_name}.png"
        self.background = pygame.image.load(str(self.background_image_path)).convert()
        # Removed redundant sim_width/length assignment here as they are assumed to be 500x700
        # self.sim_width, self.sim_length = self.background.get_size() # This is 500x700

        self.cursor_position = [self.sim_width // 2, self.sim_length // 2]
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

        self.agents = [MockAgent(f"Agent_{i}", (random.randint(50, 450), random.randint(50, 650))) for i in range(10)]
        self.image_agent_path = self.root / "graphics" / "mock_agent_front.png"
        if not self.image_agent_path.exists():
            print("Generating mock agent image...")
            if not self.image_agent_path.parent.exists():
                self.image_agent_path.parent.mkdir(parents=True, exist_ok=True)
            agent_img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
            draw_agent = ImageDraw.Draw(agent_img)
            draw_agent.ellipse([(0, 0), (23, 23)], fill=(0, 150, 200))
            agent_img.save(self.image_agent_path)
            print("Mock agent image saved.")
        self.image_agent = pygame.image.load(str(self.image_agent_path)).convert_alpha()  # This also needs screen ready
        self.image_agent_width, self.image_agent_height = self.image_agent.get_size()
        self.font = pygame.font.Font(None, 24)

        self.epochs = epochs
        self.steps_per_day = steps_per_day
        self.step = 0
        self.step_current = 0
        self.start_date = start_date
        self.date_current = start_date
        self.time_current = dt_time(8, 0)

        self.sim_panel_rect = pygame.Rect(0, 0, self.sim_width, self.sim_length)
        self.graph1_panel_rect = pygame.Rect(self.sim_width + self.padding, 0, self.graph_width, self.total_length)
        self.graph2_panel_rect = pygame.Rect(self.sim_width + (2 * self.padding) + self.graph_width, 0,
                                             self.graph_width, self.total_length)

        self.variable1_data = [0] * 100
        self.variable2_data = [0] * 100
        self.max_data_points = 500

        self.mock_friends_made = False
        self.mock_substance_used = False

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
        self.screen.fill((50, 50, 50), rect=self.graph1_panel_rect)
        self.screen.fill((50, 50, 50), rect=self.graph2_panel_rect)

        self.draw_single_graph(self.graph1_panel_rect, self.variable1_data, (0, 200, 255), "Variable 1 Count")
        self.draw_single_graph(self.graph2_panel_rect, self.variable2_data, (255, 100, 0), "Variable 2 Count")

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
        max_offset_x = max(0, self.sim_width * self.cursor_zoom - self.sim_width)
        max_offset_y = max(0, self.sim_length * self.cursor_zoom - self.sim_length)

        self.cursor_offset[0] = max(0, min(self.cursor_offset[0], max_offset_x))
        self.cursor_offset[1] = max(0, min(self.cursor_offset[1], max_offset_y))

    def draw_background(self):
        scaled_bg = pygame.transform.scale(self.background,
                                           (int(self.sim_width * self.cursor_zoom),
                                            int(self.sim_length * self.cursor_zoom)))
        bg_x = -self.cursor_offset[0]
        bg_y = -self.cursor_offset[1]
        self.screen.blit(scaled_bg, (bg_x, bg_y))

    def draw_cursor(self):
        cursor_rect = pygame.Rect(
            self.sim_panel_rect.width // 2 - self.cursor_size // 2,
            self.sim_panel_rect.height // 2 - self.cursor_size // 2,
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

    def set_collision(self):
        return {}

    def get_positions(self):
        return {}

    def get_agents(self):
        return []

    def get_positions_pairs(self):
        return {}, {}

    def vrienden_maken(self):
        if not self.mock_friends_made:
            for agent in self.agents:
                agent.action = "checkmark"
            self.action_display = True
            self.mock_friends_made = True
        else:
            self.action_display = False

    def set_agents_actions_false(self):
        for agent in self.agents:
            agent.action = False

    def middelen_gebruiken(self):
        if not self.mock_substance_used:
            for agent in self.agents:
                if random.random() < 0.3:
                    agent.action = random.choice(["alcohol", "roken"])
            self.action_display = True
            self.mock_substance_used = True
        else:
            self.action_display = False

    def run(self):
        running = True
        while running:
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

            self.screen.fill((0, 0, 0))

            self.draw_background()
            self.draw_cursor()

            self.action = "idle"
            self.set_agents_actions_false()

            if self.step_current < 1000:
                self.action = "activiteit_kiezen"
                self.mock_friends_made = False
                self.mock_substance_used = False
            elif 1000 <= self.step_current < 1250:
                self.action = "vrienden_maken"
                self.vrienden_maken()
            elif 1250 <= self.step_current < 1500:
                self.action_display = False
                self.action = "middelen_gebruiken"
                self.middelen_gebruiken()
            elif 1500 <= self.step_current < 2000:
                self.action_display = False
                self.action = "idle"
            else:
                self.step_current = 0
                self.action = "activiteit_kiezen"

            for agent in self.agents:
                target_pos = None
                if self.action == "vrienden_maken":
                    if agent.name == "Agent_0": target_pos = (200, 300)
                    if agent.name == "Agent_1": target_pos = (210, 310)
                elif self.action == "middelen_gebruiken":
                    if agent.action in ["alcohol", "roken"]: target_pos = (350, 400)

                agent.step(self.action, target_pos)
                self.draw_agent(agent.position_current)
                self.draw_textbox(agent.position_current,
                                  text=f"({int(agent.position_current[0])},{int(agent.position_current[1])})",
                                  action=agent.action if self.action_display else False)

            self.draw_step_info()
            self.draw_progress_cursor(self.screen, self.step_current, self.steps_per_day, self.sim_width,
                                      self.sim_length)

            self.update_graph_data()
            self.draw_graphs()

            self.set_time()

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    # Ensure the 'graphics' directory exists in the parent of the script's directory
    # For example, if your script is in /Users/youssefboulfiham/PycharmProjects/Youssef-Nieuwegein/test2.py
    # Then the 'graphics' folder should be in /Users/youssefboulfiham/PycharmProjects/Youssef-Nieuwegein/graphics/

    start_date = datetime(2024, 1, 1)
    env = Env(start_date=start_date, epochs=10)
    env.run()