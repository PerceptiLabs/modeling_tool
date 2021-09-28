import pytest
import numpy as np
from perceptilabs.layers.mathmerge.stats import MergeOutputStats


def test_stats_objects_are_equal_when_args_are_equal():
    outputs1 = np.array([0.5,0.4])
    obj1 = MergeOutputStats(outputs1)

    outputs2 = np.array([0.5,0.4])
    obj2 = MergeOutputStats(outputs2)

    outputs3 = np.array([0.4,0.4])
    obj3 = MergeOutputStats(outputs3)
    assert obj1 == obj2 != obj3
