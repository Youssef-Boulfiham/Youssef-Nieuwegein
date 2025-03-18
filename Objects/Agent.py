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

    def __init__(self, name, positions_color, root):
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
        self.action = "idle"
        self.activity = random.choice(["school", "vrije tijd"])
        self.position_current = random.choice(self.positions_color[self.activities_colors[self.activity]])[::-1]
        self.path = []
        self.friends = []
        self.friend_request = {}

    def step(self, step_current, positions_friends=None):
        # zo leeg mogelijk houden
        if step_current == 0:
            position_goal, collors_allowed = self.choose_activity()
        elif step_current == 1000:
            # meegeven
            position_goal, collors_allowed = positions_friends, [self.activities_colors[self.activity]]
            self.make_friends()
        elif step_current == 1500:
            # self.action = "substance use"
            position_goal, collors_allowed = self.substance_use()
            pass
        elif len(self.path) == 0:  # idle
            if round(random.uniform(0, 1), 2) < 0.9 and self.activity != "vrije tijd":  # kans op stilstaan
                self.path = [self.position_current] * random.randint(5, 25)  # sta stil
            else:
                position_goal, collors_allowed = self.get_position(), [self.activities_colors[self.activity]]
        if "position_goal" in locals():
            if position_goal is None:
                a = 0
            # noinspection PyUnboundLocalVariable
            self.path = self.Pathfinding.search_path(start=self.position_current,
                                                     end=position_goal,
                                                     collors_allowed=collors_allowed)
        if step_current == 1000:
            self.path += [positions_friends] * (500 - len(self.path))
        if len(self.path) == 0:
            a = 0
        if self.path is None:
            a = 0
        self.position_current = tuple(self.path[0])
        self.path.pop(0)
        # if step_current == 0:  # Let op!: niet efficient: gebruik % 1000 == 0 voor deze duplicate if
        #     return self.name, self.activity

    def choose_activity(self):
        self.action = "traveling"
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
        else:
            position_goal = self.get_position()
        return (position_goal,
                [self.activities_colors[activity_previous],
                 "black",
                 self.activities_colors[self.activity]])

    def make_friends(self):
        self.action = "make friend"  # pictogram
        # """
        # STR: updaten voor picrogtam
        # """
        # ####
        # # input - waar zijn alle andere agents
        # #       - wat doen alle andere agents
        # #       - statistieken
        # ####
        # # loop agents
        # # of not friend amd
        # # friend_requests griend[agent[i]] and
        # # activity_current == "thuis"
        # # Let op!: loop naar elkaar toe
        # #       - sta stil
        # #          # pictogram
        # #
        # self.path = []
        # # Group agents by activity, excluding "thuis"
        #
        # agents_per_activity = defaultdict(list)
        #
        # # Group agents by activity, excluding "thuis" activity
        # for agent, activity in name_activity.items():
        #     if activity != "thuis":
        #         agents_per_activity[activity].append(agent)
        #
        # for activity, agents in agents_per_activity.items():
        #     # If no agents are doing this activity, skip it
        #     if not agents:
        #         continue
        #
        #     agents.sort()  # Sort agents to determine the order
        #
        #     # Get the positions for the activity, handle empty list gracefully
        #     positions = self.positions_friends.get(activity, [])
        #
        #     # Ensure we don't try to assign more positions than available
        #     num_agents = len(agents)
        #     num_positions = len(positions)
        #     if num_agents > num_positions:
        #         print(f"Warning: Not enough positions for {activity}, truncating to available positions.")
        #         agents = agents[:num_positions]
        #     elif num_agents < num_positions:
        #         # In case there are more positions than agents, we can just ignore extra positions
        #         positions = positions[:num_agents]
        #
        #     # Assign positions and handle friend requests
        #     for i, agent in enumerate(agents):
        #         self.path.append(positions[i])
        #
        #         # Only make friend requests if the agent hasn't asked too many times
        #         if self.friend_request.get(agent, 0) < 5 and i > 0:
        #             target_friend = agents[i - 1]  # The one to the left in sorted order
        #
        #             # Random chance to make a friend request or increment the request count
        #             if random.random() < 0.5:
        #                 print(True)
        #                 self.friends.append(target_friend)
        #             else:
        #                 self.friend_request[target_friend] = self.friend_request.get(target_friend, 0) + 1
        #         print(positions[i])
        return (self.get_position(),  # goal
                [self.activities_colors[self.activity]])  # allowed_colors

    def substance_use(self):
        # self.action = "substance use"
        return (self.get_position(),  # goal
                [self.activities_colors[self.activity]])  # allowed_collors

    import random
    import numpy as np

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
        return position_nearby[::-1]

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

    def __str__(self):
        return str(f"{self.action}")
