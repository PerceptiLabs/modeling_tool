import pytest
import numpy as np
import tensorflow as tf
import sklearn
from sklearn.metrics import mean_absolute_error
from perceptilabs.stats.mae import MeanAbsoluteErrorStatsTracker, MeanAbsoluteErrorStats


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


def test_stats_objects_are_equal_when_args_are_equal():
    obj1 = MeanAbsoluteErrorStats(losses=([12.0, 13.0, 14.0]))
    obj2 = MeanAbsoluteErrorStats(losses=([12.0, 13.0, 14.0]))
    obj3 = MeanAbsoluteErrorStats(losses=([12.0, 13.0, 14.3])) 
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated():
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
    loss = tf.reduce_sum(tf.square(y_true - y_pred))

    tracker1 = MeanAbsoluteErrorStatsTracker()
    tracker2 = MeanAbsoluteErrorStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(
        predictions_batch=y_pred, targets_batch=y_true, loss=loss,
        epochs_completed=0, is_training=False, steps_completed=0
    )
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    

    tracker2.update(
        predictions_batch=y_pred, targets_batch=y_true, loss=loss,
        epochs_completed=0, is_training=False, steps_completed=0
    )
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal():
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
    loss = tf.reduce_sum(tf.square(y_true - y_pred))
    
    tracker1 = MeanAbsoluteErrorStatsTracker()
    tracker1.update(
        predictions_batch=y_pred, targets_batch=y_true, loss=loss,
        epochs_completed=0, is_training=False, steps_completed=0
    )
    data = tracker1.serialize()
    tracker2 = MeanAbsoluteErrorStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
    
    
