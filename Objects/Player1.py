import pygame
import time
from PIL import Image
import warnings
import sys
import os
import numpy as np
import random
import pandas as pd
# from Objects.Pathfinding import AStar
# noinspection PyUnresolvedReferences
from Pathfinding import AStar
import ast


class Agent:
    def __init__(self, name, color_positions, root):
        self.root = root
        #
        self.df = pd.read_csv(f'{self.root}/Data/df_player.csv', sep=';', dtype=float)
        self.name = name
        self.position_current = (250, 100)
        self.action = "idle"
        self.activity = "thuis"
        self.path = []
        self.friends = []
        self.friend_request = {}
        #
        self.Pathfinding = AStar()
        self.color_positions = color_positions
        self.activity_nodes = {"thuis school": [(255, 300)], "thuis vriend thuis": [(368, 256)],
                               "thuis vrije tijd": [(575, 400)],
                               "school thuis": [(224, 175)], "school vriend thuis": [(368, 256)],
                               "school vrije tijd": [(575, 400)],
                               "vriend thuis thuis": [(304, 80), (224, 175)],
                               "vriend thuis school": [(335, 400), (255, 300)], "vriend thuis vrije tijd": [(575, 400)],
                               "vrije tijd thuis": [(304, 80)], "vrije tijd school": [(335, 400)],
                               "vrije tijd vriend thuis": [(464, 255)]}
        self.activities_colors = {"thuis": "red",
                                  "school": "green",
                                  "vrije tijd": "blue",
                                  "vriend thuis": "red dark"}

    def __str__(self):
        return str(f"{self.action}")


class GUI:
    def __init__(self, agents_count_):
        self.root = "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein"
        self.colors = {"black": (0, 0, 0),
                       "white": (255, 255, 255),
                       "red": (255, 0, 0),
                       "green": (0, 255, 0),
                       "blue": (0, 0, 255),
                       "grey": (128, 128, 128),
                       "brown": (143, 110, 26),
                       "red dark": (155, 0, 0)}
        self.set_collision_sprite()
        self.set_positions_valid()
        positions_color = self.get_positions()
        self.agents = [Agent(i, positions_color, self.root) for i in range(agents_count_)]
        self.name_activity = {}

    def step(self):
        self.name_activity = {agent.name: agent.activity for agent in self.agents}

    def get_positions(self):
        """Load all valid positions per activity."""
        color_positions = {}
        for color in ['red', 'green', 'blue', 'red dark']:
            # noinspection PyBroadException
            try:
                file_path = os.path.join(self.root, f"Data/positions/{color}.txt")
                with open(file_path, "r") as file:
                    positions_valid = ast.literal_eval(file.read())
                    color_positions[color] = positions_valid
            except Exception:
                print(
                    f"\033[93m{f'posities-activiteit-{color} nog niet berekend'}\033[0m \033")
        return color_positions

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
            with open(self.root + f"/Data/positions/{i}.txt", "w") as file:
                file.write(str(positions_valid))


agents_count = 5
game = GUI(agents_count)
game.step()
print(game.name_activity)
