import numpy as np
from scipy.stats import linregress


class EpochSlowdownTracker:
    def __init__(self):
        self.times = []

    def add_time(self, t):
        self.times.append(t)

    def get_slowdown_rate(self):
        x = np.arange(len(self.times))
        y = np.array(self.times)

        result = linregress(x, y)
        return result.slope

    def has_slowdown(self, max_rate=0.001):
        rate = self.get_slowdown_rate()
        return rate > max_rate

    @property
    def num_epochs_measured(self):
        return len(self.times)
