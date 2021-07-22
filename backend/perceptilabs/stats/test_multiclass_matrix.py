import pytest
import numpy as np
import tensorflow as tf
from perceptilabs.stats.multiclass_matrix import (
    MultiClassMatrixStatsTracker,
    MultiClassMatrixStats,
    MultiClassMatrix
)


def compute_multiclass_matrix(y_pred, y_true):
    prediction_matrix = [ [0 for _ in range(len(y_pred))] for _ in range(len(y_pred)) ]
    target_value_indices = np.argmax(y_true, axis=1)
    pred_value_indices = np.argmax(y_pred, axis=1)

    for (target_value_index, pred_value_index) in zip(target_value_indices, pred_value_indices):
        prediction_matrix[target_value_index][pred_value_index] += 1

    return prediction_matrix


@pytest.fixture
def y_pred():
    yield tf.constant(
        [
            [0.0, 0.1, 0.4],
            [0.5, 0.1, 0.2],
            [0.2, 0.9, 0.3]            
        ]        
    )

    
@pytest.fixture
def y_true():
    yield tf.constant(
        [
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]            
        ]        
    )


def test_confusion_matrix_binary(y_pred, y_true):
    tracker = MultiClassMatrixStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, epochs_completed=0, is_training=True, steps_completed=0)
    stats = tracker.save()

    expected_prediction_matrix = compute_multiclass_matrix(y_pred, y_true)
    actual_prediction_matrix = stats.get_matrix_for_latest_step().prediction_matrix
    
    assert actual_prediction_matrix == expected_prediction_matrix

    
def test_confusion_matrix_size(y_pred, y_true):
    tracker = MultiClassMatrixStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, epochs_completed=0, is_training=True, steps_completed=0)
    stats = tracker.save()

    expected_prediction_matrix = compute_multiclass_matrix(y_pred, y_true)
    actual_prediction_matrix = stats.get_matrices_for_latest_epoch(phase='training')[-1][0].prediction_matrix
    
    assert actual_prediction_matrix == expected_prediction_matrix
    

def test_stats_objects_are_equal_when_args_are_equal():
    pm1 = MultiClassMatrix([
        [0, 1],
        [2, 3]
    ])
    obj1 = MultiClassMatrixStats(prediction_matrices=[pm1])
    
    pm2 = MultiClassMatrix([
        [0, 1],
        [2, 3]
    ])
    obj2 = MultiClassMatrixStats(prediction_matrices=[pm2])
    
    pm3 = MultiClassMatrix([
        [0, 1],
        [7, 3]
    ])
    obj3 = MultiClassMatrixStats(prediction_matrices=[pm3])    
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated(y_pred, y_true):
    tracker1 = MultiClassMatrixStatsTracker()
    tracker2 = MultiClassMatrixStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(
        predictions_batch=y_pred, targets_batch=y_true,
        epochs_completed=0, is_training=False, steps_completed=0,
    )
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    

    tracker2.update(
        predictions_batch=y_pred, targets_batch=y_true,
        epochs_completed=0, is_training=False, steps_completed=0,
    )
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal(y_pred, y_true):
    tracker1 = MultiClassMatrixStatsTracker()
    tracker1.update(
        predictions_batch=y_pred, targets_batch=y_true,
        epochs_completed=0, is_training=False, steps_completed=0,
    )
    data = tracker1.serialize()
    tracker2 = MultiClassMatrixStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
