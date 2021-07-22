import pytest
import numpy as np
from unittest.mock import MagicMock
import tensorflow as tf
from perceptilabs.stats.iou import IouStats, IouStatsTracker
from perceptilabs.layers.iooutput.stats.image import ImageOutputStats, ImageOutputStatsTracker
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
def y_pred():
    yield tf.constant(
        [
            [0.3, 0.6, 0.9],
            [0.2, 0.3, 0.4],
            [0.6, 0.2, 0.3]
        ]
    )

    
@pytest.fixture
def y_true():
    yield tf.constant(
        [
            [0.0, 1.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]
        ]
    )

    
@pytest.fixture
def iou(y_pred, y_true):
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


def test_stats_objects_are_equal_when_args_are_equal():
    def fn_eq(self, other):
        return self.a == other.a

    def setup(arg1=1, arg2=2, arg3=3, arg4=4, arg5=5):
        iou = MagicMock(a=arg1)
        iou.__eq__ = fn_eq

        pred = MagicMock(a=arg2)
        pred.__eq__ = fn_eq

        targets = MagicMock(a=arg4)
        targets.__eq__ = fn_eq        

        loss = MagicMock(a=arg5)
        loss.__eq__ = fn_eq

        return ImageOutputStats(
            iou=iou, predictions=pred,
            targets=targets, loss=loss
        )
            
    obj1 = setup(arg1=123)
    obj2 = setup(arg1=123)
    obj3 = setup(arg1=500)        
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated(y_pred, y_true):
    tracker1 = ImageOutputStatsTracker()
    tracker2 = ImageOutputStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(
        predictions_batch=y_pred,
        targets_batch=y_true,
        loss=tf.constant(12),        
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    
    
    tracker2.update(
        predictions_batch=y_pred,
        targets_batch=y_true,
        loss=tf.constant(12),        
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal(y_pred, y_true):
    tracker1 = ImageOutputStatsTracker()
    tracker1.update(
        predictions_batch=y_pred,
        targets_batch=y_true,
        loss=tf.constant(12),
        epochs_completed=0,
        steps_completed=0,
        is_training=True
    )
    data = tracker1.serialize()
    tracker2 = ImageOutputStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
    
