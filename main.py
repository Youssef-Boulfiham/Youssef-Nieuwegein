from Objects.GUI import GUI
from Objects.Player import Player
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')


if __name__ == "__main__":
    date_start = datetime(2024, 1, 1)
    date_end = datetime(2025, 1, 1)
    steps_max = 1000 * 12 * 60
    number_of_players = 25
    players = [Player() for _ in range(number_of_players)]
    game = GUI(players, date_start, date_end, steps_max)
