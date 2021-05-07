import pytest
import numpy as np
from unittest.mock import MagicMock
import tensorflow as tf
from perceptilabs.stats.iou import IouStats, IouStatsTracker
from perceptilabs.layers.iooutput.stats.image import ImageOutputStats
from perceptilabs.stats.accuracy import AccuracyStats, PredictionMatrix


@pytest.fixture
def accuracy():
    epochs = [
        [
            (PredictionMatrix(correct=10, incorrect=12), True),
            (PredictionMatrix(correct=12, incorrect=9), True),
            (PredictionMatrix(correct=13, incorrect=1), True),
            (PredictionMatrix(correct=14, incorrect=1), False),
            (PredictionMatrix(correct=15, incorrect=5), False),
        ],
        [
            (PredictionMatrix(correct=5, incorrect=9), True),
            (PredictionMatrix(correct=6, incorrect=13), True),
            (PredictionMatrix(correct=1, incorrect=12), True),
            (PredictionMatrix(correct=3, incorrect=11), False),
        ],
    ]
    acc_stats = AccuracyStats(epochs)
    return acc_stats

@pytest.fixture
def iou():
    y_pred = tf.constant(
        [
            [0.3, 0.6, 0.9],
            [0.2, 0.3, 0.4],
            [0.6, 0.2, 0.3]
        ]
    )
    y_true = tf.constant(
        [
            [0.0, 1.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]
        ]
    )
    tracker = IouStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, epochs_completed=0,
                   is_training=False, steps_completed=0, threshold=0.5)
    iou_stats = tracker.save()
    return iou_stats


def test_image_output_stats_get_end_results_is_not_empty(iou, accuracy):
    image_stats = ImageOutputStats(iou=iou)
    end_results = image_stats.get_end_results()
    assert end_results['IOU']['training'] == 0.
    assert end_results['IOU']['validation'] == 0.6
