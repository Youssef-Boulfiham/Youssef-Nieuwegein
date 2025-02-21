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
        self.nodes = []
        #! dit worden nodes
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
        data = {
            "ervaren gezondheid": [80],
            "leeftijd": [0.53],
            "geslacht": [0.54],
            "roken": [0.03],
            "alcohol": [0.04],
            "softdrugs": [0.02],
            "harddrugs": [0.01],
            "thuis": [0.3],
            "school": [0.4],
            "vrienden": [0.1],
            "vrije tijd": [0.2]
        }
        df = pd.DataFrame(data)

        # Extract activities and their probabilities
        activities = df.iloc[0, 7:9].to_dict()  # Select only activity columns
        activity_names = list(activities.keys())
        activity_probs = np.array(list(activities.values()))

        # Normalize probabilities to sum to 1
        activity_probs /= activity_probs.sum()

        # Compute cumulative distribution function (CDF)
        cumsum_activities = np.cumsum(activity_probs)

        # Randomly select an activity
        random_number = np.random.rand()  # Random number in [0, 1)

        # Find the first index where random_number is less than the CDF
        chosen_index = np.searchsorted(cumsum_activities, random_number)

        # Output the selected activity
        activity_next = activity_names[chosen_index]
        print(f"Selected activity: {activity_next}")

        self.path += self.Pathfinding.search_path(start=self.position_current,
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
