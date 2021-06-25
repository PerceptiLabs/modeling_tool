import pytest
import numpy as np
import tensorflow as tf
import sklearn
from sklearn.metrics import r2_score
from perceptilabs.stats.r_squared import RSquaredStatsTracker


def get_r_squared(predictions_batch, targets_batch):
    return r2_score(targets_batch, predictions_batch)


def test_r_squared_binary():
    y_pred = tf.constant(
        [
            [0.3, 0.6, 0.9],
            [0.3, 0.6, 0.9]      
        ]        
    )
    y_true = tf.constant(
        [
            [0.4, 1.0, 1.0],
            [0.4, 1.0, 1.0]         
        ]        
    )

    loss = (tf.reduce_sum(tf.square(y_true - y_pred)))
    expected_r_squared = get_r_squared(y_pred, y_true)

    tracker = RSquaredStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, loss=loss, epochs_completed=0, steps_completed=0, is_training=False)
    stats = tracker.save()

    actual_r_squared = stats.get_r_squared_for_latest_step()
    assert actual_r_squared == expected_r_squared
    