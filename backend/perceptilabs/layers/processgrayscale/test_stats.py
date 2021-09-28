import pytest
import numpy as np
from perceptilabs.layers.processgrayscale.stats import GrayscaleOutputStats


def test_stats_objects_are_equal_when_args_are_equal():
    outputs1 = np.array([0.5,0.4])
    obj1 = GrayscaleOutputStats(outputs1)

    outputs2 = np.array([0.5,0.4])
    obj2 = GrayscaleOutputStats(outputs2)

    outputs3 = np.array([0.4,0.4])
    obj3 = GrayscaleOutputStats(outputs3)
    assert obj1 == obj2 != obj3
