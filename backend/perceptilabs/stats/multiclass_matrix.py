from typing import Tuple
import tensorflow as tf
import numpy as np

from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.utils import return_on_failure

class MultiClassMatrix:
    def __init__(self, prediction_matrix):
        """ A 2-D numpy array where the rows represent the target class and the columns represent the predicted class """
        self.prediction_matrix = prediction_matrix
    
    @property
    def total(self):
        """ Return the total number of predictions in the prediction matrix. Should equal the batch size. """
        return np.sum(self.prediction_matrix)

    def __eq__(self, other):
        return self.prediction_matrix == other.prediction_matrix
    

class MultiClassMatrixStats:
    def __init__(self, prediction_matrices=None):
        self.prediction_matrices = prediction_matrices or ()

    def __eq__(self, other):
        return self.prediction_matrices == other.prediction_matrices
    
    def get_total_matrix_for_latest_epoch(self, phase='training'):
        matrices = self.get_matrices_for_latest_epoch(phase=phase)
        summed_matrix = [ [0 for _ in range(len(matrices[0][0].prediction_matrix))] for _ in range(len(matrices[0][0].prediction_matrix)) ]

        for matrix, _ in matrices:
            for row in range(len(summed_matrix)):
                for col in range(len(summed_matrix)):
                    summed_matrix[row][col] += matrix.prediction_matrix[row][col]
        return summed_matrix

    @return_on_failure(0.0)
    def get_matrices_for_epoch(self, epoch, phase='training'):
        """ Get the n x n prediction matrix this epoch """
        matrices = self.prediction_matrices[epoch]
        return matrices

    def get_matrices_for_latest_epoch(self, phase):
        return self.get_matrices_for_epoch(epoch=len(self.prediction_matrices)-1, phase=phase)

    @return_on_failure(0.0)
    def get_matrix_over_epochs(self, phase='training'):
        """ as a series over all epochs """        
        matrices_over_epochs = [
            self.get_matrix_for_epoch(epoch, phase=phase)
            for epoch in range(len(self.prediction_matrices))
        ]
        return matrices_over_epochs

    @return_on_failure(0.0)    
    def get_matrix_for_step(self, epoch, step):
        """ for a step """        
        matrix, _ = self.prediction_matrices[epoch][step]
        return matrix

    @return_on_failure(0.0)
    def get_matrix_for_latest_step(self, phase='training'):
        matrix = self.get_matrices_for_latest_epoch(phase=phase)[0][0]
        return matrix

    
         
class MultiClassMatrixStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._prediction_matrices = []  # A list of list. Outer list is per epoch, inner list is per step within that epoch

    def update(self, **kwargs):
        self._store_prediction_matrix(
            kwargs['predictions_batch'], kwargs['targets_batch'],
            kwargs['epochs_completed'], kwargs['steps_completed'],
            kwargs['is_training'],
        )

        
    def _store_prediction_matrix(self, predictions_batch, targets_batch, epochs_completed, steps_completed, is_training):
        if len(self._prediction_matrices) <= epochs_completed:
            self._prediction_matrices.append(list())  # Create list to hold steps for epoch.

        self._num_categories = targets_batch.shape[-1]
        prediction_matrix = [ [0 for _ in range(self._num_categories)] for _ in range(self._num_categories) ]

        if targets_batch.shape != predictions_batch.shape:
            targets_batch = np.squeeze(targets_batch)
            predictions_batch = np.squeeze(predictions_batch)

        def count_where():
            if len(targets_batch.shape) > 1:
                target_value_indices = np.argmax(targets_batch, axis=1)
            else:
                target_value_indices = np.argmax(targets_batch)
            if len(predictions_batch.shape) > 1:
                predicted_value_indices = np.argmax(predictions_batch, axis=1)
            else:
                predicted_value_indices = np.argmax(predictions_batch)

            return target_value_indices, predicted_value_indices
        
        
        target_value_indices, predicted_value_indices = count_where()

        if (
                (isinstance(target_value_indices, list) and isinstance(predicted_value_indices, list)) or
                (isinstance(target_value_indices, np.ndarray) and isinstance(predicted_value_indices, np.ndarray))
           ): 
            for (target_value_index, pred_value_index) in zip(target_value_indices, predicted_value_indices):
                prediction_matrix[target_value_index][pred_value_index] += 1
        else:
            prediction_matrix[target_value_indices][predicted_value_indices] += 1

        matrix = MultiClassMatrix(prediction_matrix)
        self._prediction_matrices[epochs_completed].append((matrix, is_training))

    def save(self):
        """ Save the tracked values into a TrainingStats object """

        # Convert to a tuple of tuples to make it immutable.
        pred_matrices = tuple([  
            tuple(step_matrices)
            for step_matrices in self._prediction_matrices
        ])

        return MultiClassMatrixStats(pred_matrices)

    @property
    def prediction_matrices(self):
        return self._prediction_matrices

    def __eq__(self, other):
        return self.prediction_matrices == other.prediction_matrices
 
