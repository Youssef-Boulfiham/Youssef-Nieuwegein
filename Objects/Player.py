import time
import numpy as np
import random
import pandas as pd
from Objects.Pathfinding import AStar


# from Pathfinding import AStar


class Player:

    def __init__(self, position_start):
        self.df = pd.read_csv('/Users/youssefboulfiham/PycharmProjects/pythonProject/Youssef-Nieuwegein/Objects/df_player.csv', sep=';')
        self.path = []
        self.position_current = position_start
        self.activity_current = "school"
        self.activities_free = ["school", "thuis"]
        self.nodes = []

        self.activities = {"thuis": [[250, 100]],
                           "school": [[530, 334]],
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
        activity_next = random.choice(self.activities_free)  # volgende activiteit
        position_next = random.choice(self.activities[activity_next])  # eindbestemming
        self.path += self.Pathfinding.search_path(start=self.position_current,  # actuele positie
                                                  goal=self.activities["weg_hart"],
                                                  allowed_colors=[self.activities_[self.activity_current], "black"])
        self.path += self.Pathfinding.search_path(start=self.activities["weg_hart"],
                                                  goal=random.choice(self.activities[activity_next]),
                                                  allowed_colors=["black", self.activities_[activity_next]])
        print(self.activity_current, activity_next)
        print(self.position_current, len(self.path))
        self.activity_current = activity_next

    def step_idle(self):
        directions_ = [list(map(sum, zip(self.position_current, step))) for step in self.step_sizes]
        self.path.append(random.choice(directions_))

    def __str__(self):
        return f"Player Position: {self.position_current}"

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
