from Objects.GUI import GUI
from Objects.Player import Player

player = Player(position_start=(530, 334))

if __name__ == "__main__":
    game = GUI(player)