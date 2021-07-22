import pytest
import tensorflow as tf
from unittest.mock import MagicMock
import numpy as np

from perceptilabs.stats.accuracy import AccuracyStats, PredictionMatrix
from perceptilabs.layers.iooutput.stats.numerical import NumericalOutputStats, NumericalOutputStatsTracker


def test_stats_objects_are_equal_when_args_are_equal():
    def fn_eq(self, other):
        return self.a == other.a

    def setup(arg1=1, arg2=2, arg3=3, arg4=4, arg5=5):
        r_squared = MagicMock(a=arg1)
        r_squared.__eq__ = fn_eq

        pred = MagicMock(a=arg2)
        pred.__eq__ = fn_eq

        mae = MagicMock(a=arg3)
        mae.__eq__ = fn_eq

        targets = MagicMock(a=arg4)
        targets.__eq__ = fn_eq        

        loss = MagicMock(a=arg5)
        loss.__eq__ = fn_eq

        return NumericalOutputStats(
            r_squared=r_squared, predictions=pred, mae=mae,
            targets=targets, loss=loss
        )
            
    obj1 = setup(arg1=123)
    obj2 = setup(arg1=123)
    obj3 = setup(arg1=500)        
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated():
    tracker1 = NumericalOutputStatsTracker()
    tracker2 = NumericalOutputStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(
        predictions_batch=tf.constant([[0, 0.1, 0.9], [1, 0, 0]]),
        targets_batch=tf.constant([[0, 1, 0], [1, 0, 0]]),
        loss=tf.constant(12),        
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    
    
    tracker2.update(
        predictions_batch=tf.constant([[0, 0.1, 0.9], [1, 0, 0]]),
        targets_batch=tf.constant([[0, 1, 0], [1, 0, 0]]),
        loss=tf.constant(12),        
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal():
    tracker1 = NumericalOutputStatsTracker()
    tracker1.update(
        predictions_batch=tf.constant([[0, 0.1, 0.9], [1, 0, 0]]),
        targets_batch=tf.constant([[0, 1, 0], [1, 0, 0]]),
        loss=tf.constant(12),
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    data = tracker1.serialize()
    tracker2 = NumericalOutputStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
