import pytest
import numpy as np
from unittest.mock import MagicMock

from perceptilabs.stats.loss import LossStats
from perceptilabs.stats.accuracy import AccuracyStats, PredictionMatrix
from perceptilabs.layers.iooutput.stats.categorical import CategoricalOutputStats


@pytest.fixture
def accuracy():
    epochs = [
        [
            (PredictionMatrix(correct=10, incorrect=12), True),
            (PredictionMatrix(correct=12, incorrect=9), True),
            (PredictionMatrix(correct=13, incorrect=1), True),
            (PredictionMatrix(correct=14, incorrect=1), True),
            (PredictionMatrix(correct=15, incorrect=5), False),
            (PredictionMatrix(correct=15, incorrect=5), False),
        ],
        [
            (PredictionMatrix(correct=10, incorrect=12), True),
            (PredictionMatrix(correct=12, incorrect=9), True),
            (PredictionMatrix(correct=13, incorrect=1), True),
            (PredictionMatrix(correct=14, incorrect=1), True),
            (PredictionMatrix(correct=15, incorrect=5), False),
            (PredictionMatrix(correct=15, incorrect=5), False),
        ],
        [
            (PredictionMatrix(correct=10, incorrect=12), True),
            (PredictionMatrix(correct=12, incorrect=9), True),
            (PredictionMatrix(correct=13, incorrect=1), True),
            (PredictionMatrix(correct=14, incorrect=1), True),
            (PredictionMatrix(correct=15, incorrect=5), False),
            (PredictionMatrix(correct=15, incorrect=5), False),
        ],
    ]
    acc_stats = AccuracyStats(epochs)
    return acc_stats


def test_categorical_output_stats_get_end_results_is_not_empty(accuracy):
    categorical_stats = CategoricalOutputStats(accuracy=accuracy)
    end_results = categorical_stats.get_end_results()
    assert end_results['Accuracy']['training'] == 68.05555555555556
    assert end_results['Accuracy']['validation'] == 75
