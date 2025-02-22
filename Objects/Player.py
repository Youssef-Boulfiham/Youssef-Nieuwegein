import numpy as np
import random
import pandas as pd
from Objects.Pathfinding import AStar
# from Pathfinding import AStar


class Player:

    def __init__(self, position_start):
        self.df = pd.read_csv(
            '/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/Objects/df_player.csv', sep=';',
            dtype=float)
        self.path = []
        self.position_current = position_start
        self.activity_current = "thuis"
        self.nodes = []
        self.activities_coordinates = {"thuis": [[250, 100]],
                                       "school": [[600, 400]],
                                       "vriend thuis": [[380, 250]]}#,
                                       # "vrije tijd": [[]]}
        self.activities_colors = {"thuis": "red",
                                  "school": "blue",
                                  "back_alley": "",
                                  "vrije tijd": "groen",
                                  "vriend thuis": "red dark"}
        self.Pathfinding = AStar()
        self.prompt = ""

    def step(self):
        if not len(self.path):
            self.step_idle()
        self.position_current = tuple(self.path[0])
        self.path.pop(0)

    def set_activity_next(self):
        activities = self.df.iloc[0, 7:10].to_dict()
        activity_names = list(activities.keys())
        activity_probs = np.array(list(activities.values()))
        activity_probs /= activity_probs.sum()
        cumsum_activities = np.cumsum(activity_probs)
        random_number = np.random.rand()
        chosen_index = np.searchsorted(cumsum_activities, random_number)
        activity_next = activity_names[chosen_index]
        self.path += self.Pathfinding.search_path(start=self.position_current,
                                                  goal=random.choice(self.activities_coordinates[activity_next]),
                                                  allowed_colors=[self.activities_colors[self.activity_current],
                                                                  "black",
                                                                  self.activities_colors[activity_next]])
        self.activity_current = activity_next

    def get_random_point_in_activity_zone(self, allowed_colors):
        self.Pathfinding.get_collision_layer(allowed_colors)
        collisions = np.loadtxt(f"{allowed_colors}.txt", dtype=int)
        height, width = collisions.shape
        while True:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if collisions[y, x] == 0:
                return y, x

    def step_idle(self):
        allowed_colors = [self.activities_colors[self.activity_current]]
        random_point = self.get_random_point_in_activity_zone(allowed_colors)
        self.path = self.Pathfinding.search_path(start=self.position_current,
                                                 goal=random_point,
                                                 allowed_colors=allowed_colors)

    def __str__(self):
        return str(f"{self.activity_current, len(self.path)}")
