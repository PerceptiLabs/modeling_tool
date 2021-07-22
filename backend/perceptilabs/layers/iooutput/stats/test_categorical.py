import pytest
import tensorflow as tf
from unittest.mock import MagicMock
import numpy as np

from perceptilabs.stats.accuracy import AccuracyStats, PredictionMatrix
from perceptilabs.layers.iooutput.stats.categorical import CategoricalOutputStats, CategoricalOutputStatsTracker


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


def test_stats_objects_are_equal_when_args_are_equal():
    def fn_eq(self, other):
        return self.a == other.a

    def setup(arg1=1, arg2=2, arg3=3, arg4=4, arg5=5):
        acc = MagicMock(a=arg1)
        acc.__eq__ = fn_eq

        pred = MagicMock(a=arg2)
        pred.__eq__ = fn_eq

        multiclass = MagicMock(a=arg3)
        multiclass.__eq__ = fn_eq

        targets = MagicMock(a=arg4)
        targets.__eq__ = fn_eq        

        loss = MagicMock(a=arg5)
        loss.__eq__ = fn_eq

        categories = ['cat', 'dog', 'horse']

        return CategoricalOutputStats(
            accuracy=acc, predictions=pred, multiclass_matrix=multiclass,
            targets=targets, loss=loss, categories=categories
        )
            
    obj1 = setup(arg1=123)
    obj2 = setup(arg1=123)
    obj3 = setup(arg1=500)        
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated():
    postproc = MagicMock()
    postproc.n_categories = 3
    postproc.__call__ = lambda x: tf.constant([b'cat', b'dog', b'horse'])
    
    tracker1 = CategoricalOutputStatsTracker()
    tracker2 = CategoricalOutputStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(
        predictions_batch=tf.constant([[0, 0.1, 0.9], [1, 0, 0]]),
        targets_batch=tf.constant([[0, 1, 0], [1, 0, 0]]),
        loss=tf.constant(12),        
        epochs_completed=0,
        steps_completed=0,
        postprocessing=postproc,        
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
        postprocessing=postproc,        
        is_training=True
    )
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal():
    postproc = MagicMock()
    postproc.n_categories = 3
    postproc.__call__ = lambda x: tf.constant([b'cat', b'dog', b'horse'])
    
    tracker1 = CategoricalOutputStatsTracker()
    tracker1.update(
        predictions_batch=tf.constant([[0, 0.1, 0.9], [1, 0, 0]]),
        targets_batch=tf.constant([[0, 1, 0], [1, 0, 0]]),
        loss=tf.constant(12),
        epochs_completed=0,
        steps_completed=0,
        postprocessing=postproc,
        is_training=True
    )
    data = tracker1.serialize()
    tracker2 = CategoricalOutputStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
