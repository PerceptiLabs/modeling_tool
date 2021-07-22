import pytest
import numpy as np
import tensorflow as tf
import sklearn
from sklearn.metrics import r2_score
from perceptilabs.stats.r_squared import RSquaredStatsTracker, RSquaredStats


def get_r_squared(predictions_batch, targets_batch):
    return r2_score(targets_batch, predictions_batch)


@pytest.fixture
def y_pred():
    yield tf.constant(
        [
            [0.3, 0.6, 0.9],
            [0.3, 0.6, 0.9]      
        ]        
    )

    
@pytest.fixture    
def y_true():
    yield tf.constant(
        [
            [0.4, 1.0, 1.0],
            [0.4, 1.0, 1.0]         
        ]        
    )

@pytest.fixture
def loss(y_true, y_pred):
    yield tf.reduce_sum(tf.square(y_true - y_pred))


def test_r_squared_binary(y_pred, y_true, loss):
    expected_r_squared = get_r_squared(y_pred, y_true)

    tracker = RSquaredStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, loss=loss, epochs_completed=0, steps_completed=0, is_training=False)
    stats = tracker.save()

    actual_r_squared = stats.get_r_squared_for_latest_step()
    assert actual_r_squared == expected_r_squared


def test_stats_objects_are_equal_when_args_are_equal():
    obj1 = RSquaredStats(r_squared_values=([12.0, 13.0, 14.0]))
    obj2 = RSquaredStats(r_squared_values=([12.0, 13.0, 14.0]))
    obj3 = RSquaredStats(r_squared_values=([12.0, 13.0, 14.3])) 
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated(y_pred, y_true, loss):
    tracker1 = RSquaredStatsTracker()
    tracker2 = RSquaredStatsTracker()    
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

    
def test_serialized_trackers_are_equal(y_pred, y_true, loss):
    tracker1 = RSquaredStatsTracker()
    tracker1.update(
        predictions_batch=y_pred, targets_batch=y_true, loss=loss,
        epochs_completed=0, is_training=False, steps_completed=0
    )
    data = tracker1.serialize()
    tracker2 = RSquaredStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
