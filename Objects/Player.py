import time
import numpy as np
import random
import pandas as pd
from Objects.Pathfinding import AStar
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


# from Pathfinding import AStar


class Player:

    def __init__(self, position_start):
        self.df = pd.read_csv('/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/Objects/df_player.csv', sep=';', dtype=float)
        self.path = []
        self.position_current = position_start
        self.activity_current = "thuis"
        self.nodes = []
        #! dit worden nodes
        self.activities = {"thuis": [[250, 100]],
                           "school": [[600, 400]],
                           # "vrienden": [[]],
                           # "vrije tijd": [[]],
                           "weg_hart": [320, 90]}
        self.activities_ = {"thuis": "red",
                            "school": "blue",
                            "weg_hart": "black",
                            "vrije tijd": "groen"}
        self.Pathfinding = AStar()
        self.step_sizes = [[0, 1], [1, 0], [-1, 0], [0, -1]]
        self.prompt = ""

    def step(self):
        if not len(self.path):
            self.step_idle()
        self.position_current = tuple(self.path[0])
        self.path.pop(0)

    def set_activity_next(self):
        activities = self.df.iloc[0, 7:9].to_dict()
        activity_names = list(activities.keys())
        activity_probs = np.array(list(activities.values()))
        activity_probs /= activity_probs.sum()
        cumsum_activities = np.cumsum(activity_probs)
        random_number = np.random.rand()
        chosen_index = np.searchsorted(cumsum_activities, random_number)
        activity_next = activity_names[chosen_index]
        self.path += self.Pathfinding.search_path(start=self.position_current,
                                                  goal=self.activities["weg_hart"],
                                                  allowed_colors=[self.activities_[self.activity_current], "black"])
        self.path += self.Pathfinding.search_path(start=self.activities["weg_hart"],
                                                  goal=random.choice(self.activities[activity_next]),
                                                  allowed_colors=["black", self.activities_[activity_next]])
        self.activity_current = activity_next

    def get_random_point_in_activity_zone(self, allowed_colors):
        self.Pathfinding.get_collision_layer(allowed_colors)
        collisions = np.loadtxt(f"{allowed_colors}.txt", dtype=int)
        print(collisions.shape)
        height, width = collisions.shape
        while True:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if collisions[y, x] == 0:
                return y, x

    def step_idle(self):
        allowed_colors = [self.activities_[self.activity_current]]
        random_point = self.get_random_point_in_activity_zone(allowed_colors)
        print(self.position_current, random_point, allowed_colors)
        self.path = self.Pathfinding.search_path(start=self.position_current,
                                                 goal=random_point,
                                                 allowed_colors=allowed_colors)

    # def step_idle(self):
    #     directions_ = [list(map(sum, zip(self.position_current, step))) for step in self.step_sizes]
    #     self.path.append(random.choice(directions_))

    def __str__(self):
        return f"{self.activity_current, len(self.path)}"

# def step_idle(self):
#     directions_ = self.position_current + self.directions
#     directions = []
#     for x, y in directions_:
#         if 0 <= x < self.borders.shape[0] and 0 <= y < self.borders.shape[1]:
#             if self.borders[y, x]:
#                 directions.append([x, y])
#             else:
#                 print("border", x, y)
#     self.position_current = random.choice(directions)
#     return 0
