from Objects.Env import Env
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')

if __name__ == "__main__":
    date_start = datetime(2024, 1, 1)
    epochs = 3
    steps_per_day = 4000
    env = Env(date_start, epochs, steps_per_day)