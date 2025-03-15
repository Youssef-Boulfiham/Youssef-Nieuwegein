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
    def __init__(self):
        self.name_activity = {}
        #
        self.Pathfinding = AStar()
        self.root = "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein"
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
        self.color_positions = self.get_positions()

    def get_positions(self):
        """Load all valid positions per activity."""
        color_positions = {}
        for color in ['red', 'green', 'blue', 'red dark']:
            try:
                file_path = os.path.join(self.agent.root, f"Data/positions/{color}.txt")
                with open(file_path, "r") as file:
                    positions_valid = ast.literal_eval(file.read())
                    color_positions[color] = positions_valid
            except Exception:
                print(
                    f"\033[93m{f'posities-activiteit-{color} nog niet bepaald'}\033[0m \033")
        return color_positions


class Agents:
    def __init__(self, name, agent: Agent):
        self.name = name
        self.position_current = (250, 100)
        self.action = "idle"
        self.activity = "thuis"
        self.agent = agent
        self.path = []
        self.df = pd.read_csv(f'{self.agent.root}/Data/df_player.csv', sep=';', dtype=float)

    def __str__(self):
        return str(f"{self.action}")


class GUI:
    def __init__(self, agent: Agent, agents: list):
        self.agent = agent
        self.agents = agents

    def step(self):
        self.agent.name_activity = {agent.name: agent.activity for agent in self.agents}


agent_ = Agent()
agents_ = [Agents("Alice", agent_), Agents("Bob", agent_), Agents("Charlie", agent_)]
game = GUI(agent_, agents_)
game.step()
print(game.agent.name_activity)  # {'Alice': 'idle', 'Bob': 'idle', 'Charlie': 'idle'}
