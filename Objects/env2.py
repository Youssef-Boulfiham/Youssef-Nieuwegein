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

from archief.Player1 import agents_count


class Env:
    def __init__(self):
        # technical
        self.action_display = False
        self.rng = np.random.default_rng()  # Centrale Mersenne Twister RNG
        self.rn = lambda: round(self.rng.uniform(0.01, 0.99), 5)  # get rn
        self.root = Path(__file__).parent.parent
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
        backgrounds = ["enviroment_background", "enviroment_raster", "enviroment_activity"]
        self.background = pygame.image.load(os.path.join(self.root, "graphics", f"{backgrounds[0]}.png"))
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
        self.domains = ["thuis", "school", "vriend thuis", "vrije tijd"]
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
        # env
        # agent

    def run(self):
        While True:
            get_settings()
            run_simulation()
        return 0

    def get_settings(self):
        return agents_count, epochs, date_start, date_end

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

    def get_agents(self):
        agents = []
        names = list(range(sum(self.substance_data["alcohol"]["age_counts"].values())))
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