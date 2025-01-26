import time
import numpy as np
import random

class Player:

    def __init__(self, camera):
        self.camera = camera
        self.position_current = [100, 100]
        self.position_next = [120, 120]
        self.id = 0
        self.speed = 32
        self.last_move_time = time.time()  # Initialize the last move time
        self.borders = np.loadtxt("Objects/array.txt", dtype=int)  # Load the borders map from a text file

    def step(self):
        # List of possible directions: (dx, dy) where dx is change in x and dy is change in y
        directions = [
            (0, 0),  # Stand still
            (-1, 0), # Left
            (1, 0),  # Right
            (0, -1), # Up
            (0, 1),  # Down
        ]
        
        # Check for all directions and store valid ones
        valid_directions = []
        
        for dx, dy in directions:
            # Calculate potential next position
            next_position = [self.position_current[0] + dx, self.position_current[1] + dy]
            
            # Check if the next position is within bounds and not blocked (value != 1)
            if 0 <= next_position[0] < self.borders.shape[0] and 0 <= next_position[1] < self.borders.shape[1]:
                if self.borders[next_position[0], next_position[1]] != 1:  # Position is not blocked
                    valid_directions.append((dx, dy))

        # If there are valid directions, choose one randomly and update position
        if valid_directions:
            chosen_direction = random.choice(valid_directions)
            self.position_current[0] += chosen_direction[0]
            self.position_current[1] += chosen_direction[1]

        # Update position_next to the new position
        self.position_next = self.position_current.copy()

        return self.position_current

    def __str__(self):
        return f"Player Position: {self.position_current}"
