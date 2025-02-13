import time
import numpy as np
import random

from Objects.Pathfinding import AStar


class Player:

    def __init__(self, position_start):
        self.activity_current = "home"
        self.activity_next = "school"
        self.position_current = position_start
        self.path = []
        self.pathfinding = AStar()
        self.message = "Hello World!"
        self.step_sizes = [[0, 1], [1, 0], [-1, 0], [0, -1]]

    def step(self, step_counter):

        """
        activiteit_next = thuis
        activiteit_next = school

        - na iedere 400 stappen
            - ga naar de dichtsbijzjnde weg tussen bruin en zwart


        """
        colors = ["blue", "green"]
        if not step_counter % 400:
            # find path to the road
            self.path += self.pathfinding.search_path(self.position_current,
                                                      (670, 150),
                                                      colors)
            # find path to the school
            self.path += self.pathfinding.search_path(self.path[-1],
                                                      )
            print(step_counter, len(self.path))
        if not len(self.path):
            self.step_idle()
        # print(self.path[0])
        self.position_current = tuple(self.path[0])
        self.path.pop(0)

    def step_idle(self):
        directions_ = [list(map(sum, zip(self.position_current, step))) for step in self.step_sizes]

        directions = []
        # for x, y in directions_:
        #     if 0 <= x < self.pathfinding.collisions.shape[0] and 0 <= y < self.pathfinding.collisions.shape[1]:
        #         if self.pathfinding.collisions[x, y]:
        #             directions.append([x, y])
        #         else:
        #             print("border", x, y)
        self.path.append(random.choice(directions_))
        # self.path += random.choice(directions_.tolist())

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
