from typing import Tuple
import tensorflow as tf

from perceptilabs.trainer.stats.base import TrainingStatsTracker
from perceptilabs.trainer.stats.utils import return_on_failure


class PredictionMatrix:
    def __init__(self, correct, incorrect):
        self.correct = correct
        self.incorrect = incorrect

    @property
    def total(self):
        return self.correct + self.incorrect


class AccuracyStats:
    def __init__(self, prediction_matrices=None):
        self.prediction_matrices = prediction_matrices or ()
    
    @return_on_failure(0.0)
    def get_average_accuracy_for_epoch(self, epoch, phase='training'):
        """ Average accuracy of an epoch """
        correct, total = 0, 0
        for matrix, is_training in self.prediction_matrices[epoch]:
            if (
                    (is_training and phase in ['both', 'training']) or
                    (not is_training and phase in ['both', 'validation'])
            ):
                correct += matrix.correct
                total += matrix.total
        return correct/total

    @return_on_failure(0.0)
    def get_average_accuracy_over_epochs(self, phase='training'):
        """ Average accuracy as a series over all epochs """        
        accuracies = [
            self.get_average_accuracy_for_epoch(epoch, phase=phase)
            for epoch in range(len(self.prediction_matrices))
        ]
        return accuracies

    @return_on_failure(0.0)    
    def get_accuracy_for_step(self, epoch, step):
        """ Accuracy of a step """        
        matrix, _ = self.prediction_matrices[epoch][step]
        return matrix.correct/matrix.total

    def get_accuracy_for_latest_step(self):
        """ Accuracy of the latest a step """        
        return self.get_accuracy_for_step(-1, -1)    

    @return_on_failure([0.0])    
    def get_accuracy_over_steps(self, epoch, phase='training'):
        """ Accuracy as a series over all steps in an epoch """                
        accuracies = []
        for step in range(len(self.prediction_matrices[epoch])):
            _, is_training = self.prediction_matrices[epoch][step]
            
            if (
                    (is_training and phase in ['both', 'training']) or
                    (not is_training and phase in ['both', 'validation'])
            ):
                acc = self.get_accuracy_for_step(epoch, step)
                accuracies.append(acc)
                
        return accuracies

    def get_accuracy_over_steps_in_latest_epoch(self, phase='training'):
        """ Accuracy as a series over all steps in the latest epoch """                        
        return self.get_accuracy_over_steps(
            epoch=len(self.prediction_matrices)-1,
            phase=phase
        )


class AccuracyStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._prediction_matrices = []  # A list of list. Outer list is per epoch, inner list is per step within that epoch

    def update(self, **kwargs):
        self._store_prediction_matrix(
            kwargs['predictions_batch'], kwargs['targets_batch'],
            kwargs['epochs_completed'], kwargs['steps_completed'],
            kwargs['is_training']
        )
        
    def _store_prediction_matrix(self, predictions_batch, targets_batch, epochs_completed, steps_completed, is_training):
        if len(self._prediction_matrices) <= epochs_completed:
            self._prediction_matrices.append(list())  # Create list to hold steps for epoch.
        
        correct_predictions = tf.equal(
            tf.argmax(predictions_batch, -1), tf.argmax(targets_batch, -1)
        )
        num_correct = tf.math.count_nonzero(correct_predictions).numpy()
        num_incorrect = len(predictions_batch) - num_correct

        matrix = PredictionMatrix(correct=num_correct, incorrect=num_incorrect)
        self._prediction_matrices[epochs_completed].append((matrix, is_training))

    def save(self):
        """ Save the tracked values into a TrainingStats object """

        # Convert to a tuple of tuples to make it immutable.
        pred_matrices = tuple([  
            tuple(step_matrices)
            for step_matrices in self._prediction_matrices
        ])
        return AccuracyStats(pred_matrices)
    
