import pytest
import numpy as np
import tensorflow as tf
from perceptilabs.stats.iou import IouStatsTracker, ConfusionMatrix, IouStats


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
def threshold():
    yield 0.5
    

def compute_iou(y_pred, y_true, threshold=0.5):
    y_pred_thresholded = np.where(y_pred >= threshold, 1.0, 0.0)
    tp = np.count_nonzero((y_pred_thresholded == 1.0) & (y_true == 1.0))
    fp = np.count_nonzero((y_pred_thresholded == 1.0) & (y_true == 0.0))
    tn = np.count_nonzero((y_pred_thresholded == 0.0) & (y_true == 0.0))
    fn = np.count_nonzero((y_pred_thresholded == 0.0) & (y_true == 1.0))
    iou = tp / (tp + fp + fn)  # ref: https://towardsdatascience.com/evaluating-image-segmentation-models-1e9bb89a001b 
    return iou


def test_iou_binary(y_pred, y_true, threshold):
    expected_iou = compute_iou(y_pred, y_true, threshold=threshold)

    tracker = IouStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, epochs_completed=0, is_training=False, steps_completed=0, threshold=threshold)
    stats = tracker.save()

    actual_iou = stats.get_iou_for_latest_step()
    assert actual_iou == expected_iou
    

def test_stats_objects_are_equal_when_args_are_equal():
    pm1 = [[
        (ConfusionMatrix(tp=10, tn=12, fp=1, fn=2), True),
        (ConfusionMatrix(tp=12, tn=9, fp=1, fn=2), True)
    ]]
    pm2 = [[
        (ConfusionMatrix(tp=10, tn=12, fp=1, fn=2), True),
        (ConfusionMatrix(tp=12, tn=9, fp=1, fn=2), True)
    ]]
    pm3 = [[
        (ConfusionMatrix(tp=10, tn=11, fp=1, fn=2), True),
        (ConfusionMatrix(tp=12, tn=9, fp=1, fn=2), True)
    ]]

    
    obj1 = IouStats(prediction_matrices=pm1)
    obj2 = IouStats(prediction_matrices=pm2)
    obj3 = IouStats(prediction_matrices=pm3)    
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated(y_pred, y_true, threshold):
    tracker1 = IouStatsTracker()
    tracker2 = IouStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(
        predictions_batch=y_pred, targets_batch=y_true,
        epochs_completed=0, is_training=False, steps_completed=0,
        threshold=threshold
    )
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    

    tracker2.update(
        predictions_batch=y_pred, targets_batch=y_true,
        epochs_completed=0, is_training=False, steps_completed=0,
        threshold=threshold
    )
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal(y_pred, y_true, threshold):
    tracker1 = IouStatsTracker()
    tracker1.update(
        predictions_batch=y_pred, targets_batch=y_true,
        epochs_completed=0, is_training=False, steps_completed=0,
        threshold=threshold
    )
    data = tracker1.serialize()
    tracker2 = IouStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
    
