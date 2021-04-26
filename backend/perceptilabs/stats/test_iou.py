import pytest
import numpy as np
import tensorflow as tf
from perceptilabs.stats.iou import IouStatsTracker



def test_iou_binary():
    threshold = 0.5
    
    y_pred = tf.constant(
        [
            [0.3, 0.6, 0.9],
            [0.2, 0.3, 0.4],
            [0.6, 0.2, 0.3]            
        ]        
    )
    y_true = tf.constant(
        [
            [0.0, 1.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]            
        ]        
    )


    # Keras implementation flawed, computing manually: https://github.com/tensorflow/tensorflow/issues/39173
    y_pred_thresholded = np.where(y_pred >= threshold, 1.0, 0.0)
    tp = np.count_nonzero((y_pred_thresholded == 1.0) & (y_true == 1.0))
    fp = np.count_nonzero((y_pred_thresholded == 1.0) & (y_true == 0.0))
    tn = np.count_nonzero((y_pred_thresholded == 0.0) & (y_true == 0.0))
    fn = np.count_nonzero((y_pred_thresholded == 0.0) & (y_true == 1.0))
    expected_iou = tp / (tp + fp + fn)  # ref: https://towardsdatascience.com/evaluating-image-segmentation-models-1e9bb89a001b 

    tracker = IouStatsTracker()
    tracker.update(predictions_batch=y_pred, targets_batch=y_true, epochs_completed=0, is_training=False, steps_completed=0, threshold=threshold)
    stats = tracker.save()

    actual_iou = stats.get_iou_for_latest_step()
    assert actual_iou == expected_iou
    

    
    
