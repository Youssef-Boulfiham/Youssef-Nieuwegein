from Objects.GUI import GUI
from Objects.Player import Player
from datetime import datetime

date_start = datetime(2022, 1, 1)
date_end = datetime(2028, 1, 1)
steps_max = 600000
player = Player(position_start=(530, 334))

if __name__ == "__main__":
    game = GUI(player, date_start, date_end, steps_max)