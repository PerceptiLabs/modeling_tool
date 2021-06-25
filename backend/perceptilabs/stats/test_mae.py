import pytest
import numpy as np
import tensorflow as tf
import sklearn
from sklearn.metrics import mean_absolute_error
from perceptilabs.stats.mae import MeanAbsoluteErrorStatsTracker


def get_mae(predictions_batch, targets_batch):
    return mean_absolute_error(targets_batch, predictions_batch)


def test_mae_binary():
    y_pred = tf.constant(
        [
            [0.3, 0.6, 0.9]          
        ]        
    )
    y_true = tf.constant(
        [
            [0.4, 1.0, 1.0]          
        ]        
    )

    loss = (tf.reduce_sum(tf.square(y_true - y_pred)))
    expected_mae = get_mae(y_pred, y_true)

    tracker = MeanAbsoluteErrorStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, loss=loss, epochs_completed=0, steps_completed=0, is_training=False)
    stats = tracker.save()

    actual_mae = stats.get_loss_for_latest_step()
    assert actual_mae == expected_mae
    