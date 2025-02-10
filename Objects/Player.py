import time
import numpy as np
import random


class Player:

    def __init__(self, camera):
        self.camera = camera
        self.position_current = [100, 100]
        self.position_next = [120, 120]
        self.id = 0
        self.last_move_time = time.time()  # Initialize the last move time
        self.borders = np.loadtxt("Objects/array.txt", dtype=int)  # Load the borders map from a text file
        self.directions = np.array([[0, 0], [-8, 0], [8, 0], [0, -8], [0, 8]])
        self.popup_text = None  # Text for popup above the player


    def step(self):
        directions_ = self.position_current + self.directions
        directions = []
        for x, y in directions_:
            if 0 <= x < self.borders.shape[0] and 0 <= y < self.borders.shape[1]:
                if self.borders[y, x]:
                    directions.append([x, y])
                else:
                    print("border", x, y)
        self.position_current = random.choice(directions)
        return 0

    def set_popup(self, text):
        self.popup_text = text

    def clear_popup(self):
        self.popup_text = None

    def __str__(self):
        return f"Player Position: {self.position_current}"


# Example usage:
camera = None  # Assuming camera is defined elsewhere
player = Player(camera)
print(player.step())  # Test the step function
