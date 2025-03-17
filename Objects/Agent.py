import os
import numpy as np
import random
import pandas as pd
# noinspection PyUnresolvedReferences
from Objects.Pathfinding import AStar
# from Pathfinding import AStar
import ast


class Agent:

    def __init__(self, name, color_positions, root):
        self.root = root
        #
        self.df = pd.read_csv(f'{self.root}/Data/df_player.csv', sep=';', dtype=float)
        self.name = name
        self.position_current = (250, 100)
        self.action = "idle"
        self.activity = "thuis"
        self.path = []
        self.friends = []
        self.friend_request = {}
        #
        self.Pathfinding = AStar()
        self.color_positions = color_positions
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

    def step(self, step_current):
        if step_current == 0:
            self.action = "traveling"
            position_goal, collors_allowed = self.choose_activity()
        elif step_current == 1000:
            # position_goal, collors_allowed = self.make_friend()
            self.action = "make friend"  # pictogram
            position_goal, collors_allowed = self.make_friends()
        elif step_current == 1500:
            # self.action = "substance use"
            position_goal, collors_allowed = self.substance_use()
            pass
        elif len(self.path) == 0:  # idle
            if round(random.uniform(0, 1), 2) < 0.9 and self.activity != "vrije tijd":  # kans op stilstaan
                self.path = [self.position_current] * random.randint(5, 25)
            else:
                position_goal, collors_allowed = self.get_position(), [self.activities_colors[self.activity]]
        # noinspection PyUnboundLocalVariable
        if "position_goal" in locals():
            # noinspection PyUnboundLocalVariable
            self.path = self.Pathfinding.search_path(start=self.position_current,
                                                     end=position_goal,
                                                     collors_allowed=collors_allowed)
        if len(self.path) == 0:
            a= 0
        self.position_current = tuple(self.path[0])
        self.path.pop(0)

    def choose_activity(self):
        ### F=
        self.path = []
        activities = self.df.iloc[0, 7:].to_dict()
        activity_names = list(activities.keys())
        activity_probs = np.array(list(activities.values()))
        activity_probs /= activity_probs.sum()
        cumsum_activities = np.cumsum(activity_probs)
        random_number = np.random.rand()
        chosen_index = np.searchsorted(cumsum_activities, random_number)
        activity_previous = self.activity  # onthou vorige activiteit
        self.activity = activity_names[chosen_index]  # ga naar volgende activiteit
        ###
        # kies voor dichtsbijzijnde positie of willekeurig
        # als andere activiteit, loop dan naar ingang van volgende activiteit
        if self.activity != activity_previous:
            position_goal = random.choice(self.activity_nodes[f"{activity_previous} {self.activity}"])
        # als zelfde activiteit, loop naar willeukeurige positie in activiteitsgebied
        else: position_goal = self.get_position()
        return (position_goal,
                [self.activities_colors[activity_previous],
                 "black",
                 self.activities_colors[self.activity]])
    
    def make_friends(self):
        """

        :return:
        """
        # loop agents

        # of not friend amd
        # friend_requests griend[agent[i]] and
        # activity_current == "thuis"

        # Let op!: loop naar elkaar toe
        #       - sta stil
        #          # pictogram
        #

        n = None
        start_x=352
        end_x=240
        start_y=384
        # y_values = [start_y - (i * (start_y // (n - 1))) for i in range(n)]
        # partitions = [(start_x, y, end_x, y) for y in y_values]
        return (self.get_position(),
                [self.activities_colors[self.activity]])

    def substance_use(self):
        return (self.get_position(),
                [self.activities_colors[self.activity]])

    def get_position(self):
        """Geeft een valide positie IN HUIDIGE ACTIVITEIT:
            - 1e keus: positie in de buurt,
            - 2e keus: als te ver of activiteit vrije tijd dan willekeurig."""
        color_current = self.activities_colors[self.activity]
        # hussel lijst zodat niet steeds dezelfde (,de eerste,) positie word gekozen.
        positions = np.random.permutation(self.color_positions[color_current])
        # zoek een plaats in de buurt
        positions_nearby = [pos for pos in positions
                            if abs(pos[0] - self.position_current[0]) <= 100 and
                            abs(pos[1] - self.position_current[1]) <= 100]  # Let op!: BUG: isoleert
        # als er geen positie in de buurt is of activiteit is vrije tijd
        if not positions_nearby or color_current == "green":
            return random.choice(self.color_positions[color_current])[::-1]
        return random.choice(positions_nearby)[::-1]

    def set_positions(self):
        """Load all valid coordinates per activity."""
        color_positions = {}
        for color in ['red', 'green', 'blue', 'red dark']:
            try:
                file_path = os.path.join(self.root, f"Data/coordinates/{color}.txt")
                with open(file_path, "r") as file:
                    positions_valid = ast.literal_eval(file.read())
                    color_positions[color] = positions_valid
            except Exception:
                continue
        self.color_positions = color_positions

    def __str__(self):
        return str(f"{self.action}")

