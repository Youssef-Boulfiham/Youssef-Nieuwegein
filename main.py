from Objects.Env import Env
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')


if __name__ == "__main__":
    date_start = datetime(2024, 1, 1)
    date_end = datetime(2026, 1, 1)
    steps_max = 2000 * 365 * 2  # stappen * dagen * jarena
    game = Env(date_start, date_end, steps_max)
