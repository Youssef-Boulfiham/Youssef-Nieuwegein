from Objects.GUI import GUI
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')


if __name__ == "__main__":
    date_start = datetime(2024, 1, 1)
    date_end = datetime(2025, 1, 1)
    steps_max = 2000 * 12 * 60
    agents_count = 24
    game = GUI(agents_count, date_start, date_end, steps_max)
