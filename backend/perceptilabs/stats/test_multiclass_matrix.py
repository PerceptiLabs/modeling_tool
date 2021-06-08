import pytest
import numpy as np
import tensorflow as tf
from perceptilabs.stats.multiclass_matrix import MultiClassMatrixStatsTracker


def compute_multiclass_matrix(y_pred, y_true):
    prediction_matrix = [ [0 for _ in range(len(y_pred))] for _ in range(len(y_pred)) ]
    target_value_indices = np.argmax(y_true, axis=1)
    pred_value_indices = np.argmax(y_pred, axis=1)

    for (target_value_index, pred_value_index) in zip(target_value_indices, pred_value_indices):
        prediction_matrix[target_value_index][pred_value_index] += 1

    return prediction_matrix



def test_confusion_matrix_binary():
    y_pred = tf.constant(
        [
            [0.0, 0.1, 0.4],
            [0.5, 0.1, 0.2],
            [0.2, 0.9, 0.3]            
        ]        
    )
    y_true = tf.constant(
        [
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]            
        ]        
    )


    tracker = MultiClassMatrixStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, epochs_completed=0, is_training=True, steps_completed=0)
    stats = tracker.save()

    expected_prediction_matrix = compute_multiclass_matrix(y_pred, y_true)
    actual_prediction_matrix = stats.get_matrix_for_latest_step().prediction_matrix
    
    assert actual_prediction_matrix == expected_prediction_matrix

def test_confusion_matrix_size():
    y_pred = tf.constant(
        [
            [0.0, 0.1, 0.4],
            [0.5, 0.1, 0.2],
            [0.2, 0.9, 0.3]            
        ]        
    )
    y_true = tf.constant(
        [
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]            
        ]        
    )


    tracker = MultiClassMatrixStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, epochs_completed=0, is_training=True, steps_completed=0)
    stats = tracker.save()

    expected_prediction_matrix = compute_multiclass_matrix(y_pred, y_true)
    actual_prediction_matrix = stats.get_matrices_for_latest_epoch(phase='training')[-1][0].prediction_matrix
    
    assert actual_prediction_matrix == expected_prediction_matrix
    

    
    
