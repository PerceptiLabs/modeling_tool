import pytest
import numpy as np
from perceptilabs.layers.processreshape.stats import ReshapeOutputStats


def test_stats_objects_are_equal_when_args_are_equal():
    outputs1 = np.array([0.5,0.4])
    obj1 = ReshapeOutputStats(outputs1)

    outputs2 = np.array([0.5,0.4])
    obj2 = ReshapeOutputStats(outputs2)

    outputs3 = np.array([0.4,0.4])
    obj3 = ReshapeOutputStats(outputs3)
    assert obj1 == obj2 != obj3
