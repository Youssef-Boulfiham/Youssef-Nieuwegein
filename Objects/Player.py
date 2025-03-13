import numpy as np
import random
import pandas as pd
from Objects.Pathfinding import AStar
# from Pathfinding import AStar
import ast

class Player:

    def __init__(self):
        self.root = "/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/"

        self.df = pd.read_csv(
            '/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/Objects/df_player.csv', sep=';',
            dtype=float)
        self.path = []
        self.activity_current = "thuis"
        self.Pathfinding = AStar()
        self.activities_colors = {"thuis": "red",
                                  "school": "blue",
                                  "vrije tijd": "green",
                                  "vriend thuis": "red dark"}
        self.position_current = (250, 100)
        self.nodes = []
        self.prompt = ""

    def step(self, activity_next=False):
        if activity_next:
            self.set_activity_next()
        if not len(self.path):
            self.step_idle()
        self.position_current = tuple(self.path[0])
        self.path.pop(0)

    def get_position_valid(self):
        file = self.root + f"Data/positions/{self.activities_colors[self.activity_current]}.txt"
        with open(file, "r") as file:
            positions_valid = ast.literal_eval(file.read())
            return random.choice(positions_valid)[::-1]

    def set_activity_next(self):
        self.path = []
        activities = self.df.iloc[0, 7:].to_dict()
        activity_names = list(activities.keys())
        activity_probs = np.array(list(activities.values()))
        activity_probs /= activity_probs.sum()
        cumsum_activities = np.cumsum(activity_probs)
        random_number = np.random.rand()
        chosen_index = np.searchsorted(cumsum_activities, random_number)
        activity_previous = self.activity_current
        self.activity_current = activity_names[chosen_index]
        self.path += self.Pathfinding.search_path(start=self.position_current,
                                                  goal=self.get_position_valid(),
                                                  allowed_colors=[self.activities_colors[activity_previous],
                                                                  "black",
                                                                  self.activities_colors[self.activity_current]])


    def step_idle(self):
        allowed_colors = [self.activities_colors[self.activity_current]]
        random_point = self.get_position_valid()
        self.path = self.Pathfinding.search_path(start=self.position_current,
                                                 goal=random_point,
                                                 allowed_colors=allowed_colors)

    def __str__(self):
        return str(f"{self.activity_current, len(self.path)}")
