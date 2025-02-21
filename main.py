from Objects.GUI import GUI
from Objects.Player import Player
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'
import matplotlib.pyplot as plt

date_start = datetime(2024, 1, 1)
date_end = datetime(2025, 1, 1)
steps_max = 1000*12*2
player = Player(position_start=(250, 100))

if __name__ == "__main__":
    game = GUI(player, date_start, date_end, steps_max)