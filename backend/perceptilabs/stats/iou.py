# NOTE: current implementation only supports binary segmentation.

from typing import Tuple
import tensorflow as tf

from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.utils import return_on_failure


class ConfusionMatrix:
    def __init__(self, tp, tn, fp, fn):
        self.tp = tp
        self.tn = tn
        self.fp = fp
        self.fn = fn

    def __eq__(self, other):
        return (
            self.tp == other.tp and
            self.tn == other.tn and
            self.fp == other.fp and
            self.fn == other.fn
        )

        
class IouStats:
    def __init__(self, prediction_matrices=None):
        self.prediction_matrices = prediction_matrices or ()

    def __eq__(self, other):
        return self.prediction_matrices == other.prediction_matrices
    
    @return_on_failure(0.0)
    def get_average_iou_for_epoch(self, epoch, phase='training'):
        """ Average iou of an epoch """
        intersection, union = 0, 0
        for matrix, is_training in self.prediction_matrices[epoch]:
            if (
                    (is_training and phase in ['both', 'training']) or
                    (not is_training and phase in ['both', 'validation'])
            ):
                intersection += matrix.tp  # intersection: both y_pred and y_true are positive
                union += (matrix.tp + matrix.fp + matrix.fn)  # union: y_pred or y_true is positive
        return intersection/union

    @return_on_failure(0.0)
    def get_iou_over_epochs(self, phase='training'):
        """ Average iou as a series over all epochs """        
        accuracies = [
            self.get_average_iou_for_epoch(epoch, phase=phase)
            for epoch in range(len(self.prediction_matrices))
        ]
        return accuracies

    @return_on_failure(0.0)    
    def get_iou_for_step(self, epoch, step):
        """ Iou of a step """        
        matrix, _ = self.prediction_matrices[epoch][step]
        return matrix.tp/(matrix.tp + matrix.fp + matrix.fn)

    @return_on_failure([0.0])    
    def get_iou_over_steps(self, epoch, phase='training'):
        """ Iou as a series over all steps in an epoch """                
        accuracies = []
        for step in range(len(self.prediction_matrices[epoch])):
            _, is_training = self.prediction_matrices[epoch][step]
            
            if (
                    (is_training and phase in ['both', 'training']) or
                    (not is_training and phase in ['both', 'validation'])
            ):
                acc = self.get_iou_for_step(epoch, step)
                accuracies.append(acc)
                
        return accuracies

    def get_iou_over_steps_in_latest_epoch(self, phase='training'):
        """ Iou as a series over all steps in the latest epoch """
        return self.get_iou_over_steps(
            epoch=len(self.prediction_matrices)-1,
            phase=phase
        )

    @return_on_failure(0.0)        
    def get_iou_for_latest_step(self, phase='both'):  
        """ IoU of the latest a step """
        iou_list = self.get_iou_over_steps_in_latest_epoch(phase=phase)
        return iou_list[-1]

    
class IouStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._prediction_matrices = []  # A list of list. Outer list is per epoch, inner list is per step within that epoch

    def update(self, **kwargs):
        self._store_prediction_matrix(
            kwargs['predictions_batch'], kwargs['targets_batch'],
            kwargs['epochs_completed'], kwargs['steps_completed'],
            kwargs['is_training'],
            kwargs.get('threshold', 0.5)
        )
        
    def _store_prediction_matrix(self, predictions_batch, targets_batch, epochs_completed, steps_completed, is_training, threshold):
        if len(self._prediction_matrices) <= epochs_completed:
            self._prediction_matrices.append(list())  # Create list to hold steps for epoch.

        thresholded_batch = tf.where(predictions_batch >= threshold, 1.0, 0.0)  # Convert to positive(1.0)/negative(0.0) so we can compute the confusion matrix

        def count_where(prediction, target):
            """ Count how many times prediction and targets both match their specified values. E.g., how many times were both true at the same time? """
            matches = tf.math.logical_and(
                tf.math.equal(thresholded_batch, prediction),
                tf.math.equal(targets_batch, target)
            )            
            count = tf.math.count_nonzero(matches).numpy()
            return count
        
        # Confusion matrix
        tp = count_where(prediction=1.0, target=1.0)
        fp = count_where(prediction=1.0, target=0.0)
        tn = count_where(prediction=0.0, target=0.0)
        fn = count_where(prediction=0.0, target=1.0)

        matrix = ConfusionMatrix(tp=tp, fp=fp, tn=tn, fn=fn)
        self._prediction_matrices[epochs_completed].append((matrix, is_training))

    def save(self):
        """ Save the tracked values into a TrainingStats object """

        # Convert to a tuple of tuples to make it immutable.
        pred_matrices = tuple([  
            tuple(step_matrices)
            for step_matrices in self._prediction_matrices
        ])
        return IouStats(pred_matrices)
    
    @property
    def prediction_matrices(self):
        return self._prediction_matrices
    
    def __eq__(self, other):
        return self.prediction_matrices == other.prediction_matrices
        
