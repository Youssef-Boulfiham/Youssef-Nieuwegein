from Objects.GUI import GUI
from Objects.Player import Player

player = Player(position_start=(400,100))

if __name__ == "__main__":
    game = GUI(player)