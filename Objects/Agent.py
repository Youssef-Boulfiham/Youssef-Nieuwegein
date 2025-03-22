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

    def __init__(self, name, age, positions_color, root, agents_count):
        # self.agents_count = agents_count
        self.root = root
        self.Pathfinding = AStar()
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
        self.positions_color = positions_color
        #
        self.df = pd.read_csv(f'{self.root}/Data/Input/df_player.csv', sep=';', dtype=float)
        self.name = name
        self.age = age
        self.action = None
        self.activity = random.choice(["school", "vrije tijd"])
        self.position_current = random.choice(self.positions_color[self.activities_colors[self.activity]])[::-1]
        self.path = []
        self.friends = []
        self.friend_request = self.friend_request = {i: 0 for i in range(agents_count)}
        self.neighbour = None
        self.a = []

    def step(self, activity, position_end):
        # Initialize colors_allowed to None (position_end is passed as an input)
        colors_allowed = None

        # Handle different activities
        if activity == "vrienden_maken" and self.activity != "thuis":
            # Use the input parameter position_end directly for vrienden_maken
            self.vrienden_maken(position_end)
        elif activity in ["activiteit_kiezen"]:
            position_end, colors_allowed = self.activiteit_kiezen()
        elif len(self.path) == 0:  # idle
            result = self.idle()  # Get the result from idle
            if result:  # Only define position_end and colors_allowed if idle() returns something
                position_end, colors_allowed = result
            else:
                # Fallback: Use current position and color
                position_end, colors_allowed = self.position_current, [self.activities_colors[self.activity]]

        # Make sure position_end and colors_allowed are defined before using them
        if position_end is not None and colors_allowed is not None:
            self.path += self.Pathfinding.search_path(start=self.position_current,
                                                      end=position_end,
                                                      collors_allowed=colors_allowed)

        if len(self.path) == 0:
            a = 0  # If path is empty, handle this case

        self.position_current = tuple(self.path[0])
        self.path.pop(0)

    def idle(self):
        if round(random.uniform(0, 1), 2) < 0.9 and self.activity != "vrije tijd":  # kans
            self.path = [self.position_current] * random.randint(5, 25)  # sta stil
        else:
            return self.get_position(), [self.activities_colors[self.activity]]  # random

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
        # kies voor dichtsbijzijnde positie of willekeurig
        # als andere activiteit, loop dan naar ingang van volgende activiteit
        if self.activity != activity_previous:
            position_end = random.choice(self.activity_nodes[f"{activity_previous} {self.activity}"])
        # als zelfde activiteit, loop naar willeukeurige positie in activiteitsgebied
        else:
            position_end = self.get_position()
        return (position_end,
                [self.activities_colors[activity_previous],
                 "black",
                 self.activities_colors[self.activity]])

    def vrienden_maken(self, position_end):
        if position_end == None:
            a=0
        self.path = self.Pathfinding.search_path(start=self.position_current,
                                                 end=position_end,
                                                 collors_allowed=[self.activities_colors[self.activity]])
        self.path += [position_end] * (500 - len(self.path))

    def middelen_gebruiken(self):
        return (self.get_position(),  # goal
                [self.activities_colors[self.activity]])  # allowed_collors

    def get_position(self):
        """Geeft een valide positie IN HUIDIGE ACTIVITEIT:
            - 1e keus: positie in de buurt,
            - 2e keus: als te ver of activiteit vrije tijd dan willekeurig."""
        color_current = self.activities_colors[self.activity]
        # Hussel lijst zodat niet steeds dezelfde positie wordt gekozen.
        positions = rng.permutation(self.positions_color[color_current])
        # Sorteer op afstand tot huidige positie (zowel x als y)
        positions = sorted(positions,
                           key=lambda pos: abs(pos[0] - self.position_current[0]) + abs(
                               pos[1] - self.position_current[1]))
        # Bepaal een gewogen keuze, waarbij dichterbij vaker wordt gekozen
        closer_half = positions[:len(positions) // 2]  # Selecteer de eerste helft (dichterbij)
        if closer_half and random.random() < 0.75:  # 75% kans om uit de eerste helft te kiezen
            position_nearby = random.choice(closer_half)
        else:
            position_nearby = random.choice(positions)  # Normale random keuze
        # Als activiteit 'green' is, kies volledig willekeurig
        if color_current == "green":
            return random.choice(self.positions_color[color_current])[::-1]
        return list(position_nearby[::-1])

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
            f"{self.name}, {self.age}, {len(self.friends)}, {self.position_current}, {len(self.path)}, {self.activity}, {self.action}")
