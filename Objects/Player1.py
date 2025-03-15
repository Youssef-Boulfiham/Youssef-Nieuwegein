import warnings
import os
import numpy as np
import random
import pandas as pd
import ast

from Pathfinding import AStar


class Agent:
    def __init__(self):
        self.root = "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/"
        self.df = pd.read_csv(
            f'{self.root}/Data/df_player.csv', sep=';',
            dtype=float
        )
        self.name_activity = {}  # Store name-activity mapping
        self.activity_nodes = {
            "thuis school": [(255, 300)], "thuis vriend thuis": [(368, 256)],
            "thuis vrije tijd": [(575, 400)], "school thuis": [(224, 175)],
            "school vriend thuis": [(368, 256)], "school vrije tijd": [(575, 400)],
            "vriend thuis thuis": [(304, 80), (224, 175)], "vriend thuis school": [(335, 400), (255, 300)],
            "vriend thuis vrije tijd": [(575, 400)], "vrije tijd thuis": [(304, 80)],
            "vrije tijd school": [(335, 400)], "vrije tijd vriend thuis": [(464, 255)]
        }
        self.color_positions = self.get_positions()

    def get_positions(self):
        """Load all valid positions per activity."""
        color_positions = {}
        for color in ['red', 'green', 'blue', 'red dark']:
            try:
                file_path = os.path.join(self.root, f"Data/positions/{color}.txt")
                with open(file_path, "r") as file:
                    positions_valid = ast.literal_eval(file.read())
                    color_positions[color] = positions_valid
            except Exception as e:
                warnings.warn(f"{e}", stacklevel=2)
        return color_positions


class Agents:
    def __init__(self, name, agent: Agent):
        self.name = name
        self.activity = "idle"
        self.agent = agent  # Reference the shared Agent instance


class GUI:
    def __init__(self, agent: Agent, agents: list):
        self.agent = agent
        self.agents = agents

    def step(self):
        self.agent.name_activity = {agent.name: agent.activity for agent in self.agents}


# Create a single shared Agent instance
agent = Agent()

# Create child agents that reference the shared Agent
agents = [Agents("Alice", agent), Agents("Bob", agent), Agents("Charlie", agent)]

# Pass to GUI
game = GUI(agent, agents)
game.step()

# Output name-activity mapping
print(game.agent.name_activity)
