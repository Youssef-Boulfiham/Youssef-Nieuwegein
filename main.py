from Objects.Env import Env
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')

if __name__ == "__main__":
    date_start = datetime(2025, 1, 1)
    epochs = 3
    # steps_per_day = 1000
    # steps_per_day = 1
    # env = Env(date_start, epochs, steps_per_day)
    env = Env(date_start, epochs)
