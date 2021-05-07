import pytest
import numpy as np
from unittest.mock import MagicMock

from perceptilabs.stats.loss import LossStats
from perceptilabs.stats.global_ import GlobalStats

@pytest.fixture
def loss():
    losses = []

    for epoch in range(3):
        losses.append([])
        
        for _ in range(4):  # Training steps
            losses[epoch].append((0.6, True))

        for _ in range(2):  # Validation steps
            losses[epoch].append((0.4, False))

    loss_stats = LossStats(losses)
    return loss_stats


def test_global_stats_get_end_results_is_not_empty(loss):
    global_stats = GlobalStats(loss)
    end_results = global_stats.get_end_results()
    assert end_results['Global_Loss']['training'] == 0.6
    assert end_results['Global_Loss']['validation'] == 0.4
