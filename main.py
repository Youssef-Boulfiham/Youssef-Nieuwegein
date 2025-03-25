from Objects.Env import Env
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')


if __name__ == "__main__":
    date_start = datetime(2024, 1, 1)
    date_end = datetime(2026, 1, 1)
    steps_max = 2000 * 365 * 2  # stappen * dagen * jaren
    agents_count = 24
    game = Env(agents_count, date_start, date_end, steps_max)
