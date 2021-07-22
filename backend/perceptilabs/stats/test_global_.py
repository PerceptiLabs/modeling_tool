import pytest
import tensorflow as tf
import numpy as np
from unittest.mock import MagicMock

from perceptilabs.stats.loss import LossStats
from perceptilabs.stats.global_ import GlobalStats, GlobalStatsTracker


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


def test_stats_objects_equality():
    loss1 = [[(0.1, True), (0.2, True)]]
    loss2 = [[(0.1, True), (0.2, True)]]
    loss3 = [[(0.1, True), (0.4, True)]]        

    obj1 = GlobalStats(loss1)
    obj2 = GlobalStats(loss2)
    obj3 = GlobalStats(loss3)    
    assert obj1 == obj2 != obj3
    

def test_trackers_are_equal_when_both_are_updated():
    tracker1 = GlobalStatsTracker()
    tracker2 = GlobalStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(
        loss=tf.constant(123.0),        
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    
    
    tracker2.update(
        loss=tf.constant(123.0),
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal():
    tracker1 = GlobalStatsTracker()
    tracker1.update(
        loss=tf.constant(123.0),        
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    data = tracker1.serialize()
    tracker2 = GlobalStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
