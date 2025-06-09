import itertools
import os
import numpy as np
from collections import defaultdict

rng = np.random.default_rng()
import random
import pandas as pd
# noinspection PyUnresolvedReferences
from Objects.Pathfinding import AStar
# from Pathfinding import AStar
import ast


class Agent:

    def __init__(self, name, age, fixed_drinker, fixed_smoker, alcohol_resistance, smoking_resistance, positions_color, root, agents_count, positions, activities, collisions):
        # self.agents_count = agents_count
        self.positions = positions
        self.root = root
        self.Pathfinding = AStar(collisions)
        self.activities_colors = {"thuis": "red",
                                  "school": "green",
                                  "vrije tijd": "blue",
                                  "vriend thuis": "red dark"}
        self.activities = activities
        self.positions_color = positions_color
        #
        self.df = pd.read_csv(f'{self.root}/Data/Input/df_player.csv', sep=';', dtype=float)
        self.name = name
        self.age = age
        # TODO: volgende is voor middelen gebruiken
        self.fixed_alcohol = fixed_drinker  # Of deze agent altijd drinkt
        self.fixed_roken = fixed_smoker  # Of deze agent altijd rookt
        self.alcohol_resistance = alcohol_resistance  # Weerstand tegen alcoholgebruik
        self.roken_resistance = smoking_resistance  # Weerstand tegen rookgedrag
        self.alcohol_count = 0  # Aantal keren alcohol gebruikt
        self.roken_count = 0  # Aantal keren gerookt

        self.activity = random.choice(self.activities)
        self.position_current = random.choice(self.positions[self.activity])
        self.action = None
        # self.position_current = random.choice(self.positions_color[self.activities_colors[self.activity]])[::-1]
        self.path = []
        self.friends = []
        self.friend_request = self.friend_request = {i: 0 for i in range(agents_count)}

    def step(self, activity, position_end):
        colors_allowed = None

        if activity == "vrienden_maken" and self.activity != "thuis":
            self.vrienden_maken(position_end)
        elif activity in ["activiteit_kiezen"]:
            position_end, colors_allowed = self.activiteit_kiezen() or (None, None)
        elif len(self.path) == 0:
            result = self.idle()
            if result:
                position_end, colors_allowed = result
            else:
                position_end, colors_allowed = self.position_current, f"['{self.activity}']"

        if position_end is not None and colors_allowed is not None:
            self.path += self.Pathfinding.search_path(start=self.position_current,
                                                      end=position_end,
                                                      activity=colors_allowed)

        if len(self.path) == 0:
            a = 0  # If path is empty, handle this case

        self.position_current = tuple(self.path[0])
        self.path.pop(0)

    def idle(self):
        if round(random.uniform(0, 1), 2) < 0.9 and self.activity != "vrije tijd":  # kans
            self.path = [self.position_current] * random.randint(5, 25)  # sta stil
        else:
            return self.get_position(), f"['{self.activity}']"  # random

    def activiteit_kiezen(self):
        self.path = []  # reset
        activities = self.df.iloc[0, 7:].to_dict()
        activity_names = list(activities.keys())
        activity_probs = np.array(list(activities.values()))
        activity_probs /= activity_probs.sum()
        cumsum_activities = np.cumsum(activity_probs)
        chosen_index = np.searchsorted(cumsum_activities, np.random.rand())
        activity_previous = self.activity  # onthoudt vorige activiteit
        self.activity = activity_names[chosen_index]  # ga naar volgende activiteit
        ###
        if self.activity == activity_previous:
            return self.idle()
        else:
            position_end = self.get_position()
            return position_end, f"['{activity_previous}', 'black', '{self.activity}']"

    def vrienden_maken(self, position_end):
        if position_end == None:
            a = 0
        self.path = self.Pathfinding.search_path(start=self.position_current,
                                                 end=position_end,
                                                 activity=f"['{self.activity}']")
        self.path += [position_end] * (450 - len(self.path))

    def middelen_gebruiken(self):
        return (self.get_position(),  # goal
                [self.activities_colors[self.activity]])  # allowed_collors

    def get_position(self):
        """Geeft een valide positie IN HUIDIGE ACTIVITEIT:
            - 1e keus: positie in de buurt,
            - 2e keus: als te ver of activiteit vrije tijd dan willekeurig."""
        positions_activity = self.positions[self.activity]
        # Sorteer op afstand tot huidige positie (zowel x als y)
        positions = sorted(positions_activity,
                           key=lambda pos: abs(pos[0] - self.position_current[0]) +
                                           abs(pos[1] - self.position_current[1]))
        # Bepaal een gewogen keuze, waarbij dichterbij vaker wordt gekozen
        closer_half = positions[:len(positions) // 2]  # Selecteer de eerste helft (dichterbij)
        if closer_half and random.random() < 0.75:  # 75% kans om uit de eerste helft te kiezen
            position_nearby = random.choice(closer_half)
        else:
            position_nearby = random.choice(positions)  # Normale random keuze
        # Als activiteit vrije tijd is; kies volledig willekeurig
        if self.activity == "vrije tijd":
            return random.choice(positions_activity)
        return position_nearby

    def get_positions_friends(self):
        activities = ["school", "vrienden thuis", "vrije tijd"]
        all_positions = {}  # Change this to a dictionary instead of a list
        for activity in activities:
            file_path = os.path.join(self.root, "Data", "Input", "positions_friends", f"{activity}.txt")
            try:
                with open(file_path, "r") as f:
                    positions = ast.literal_eval(f.read())
                    all_positions[activity] = positions
            except FileNotFoundError:
                print(f"\033[93mposities-activiteit-{activity} nog niet berekend\033[0m")
                all_positions[activity] = []
        return all_positions

    def __repr__(self):
        return (f"'{self.name}', {self.age}, {len(self.friends)}, "
                f"{self.position_current}, {len(self.path)}, '{self.activity}', '{self.action}'")

    def __str__(self):
        return str(
            f"{self.name}, {self.age}, resistance=  {self.resistance}, {len(self.friends)}, {self.position_current}, p={len(self.path)}, {self.activity}, {self.action}")