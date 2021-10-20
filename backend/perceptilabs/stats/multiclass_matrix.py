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

    def get_precision_over_epochs(self, phase='training'):
        summed_matrices = self.get_total_matrices_for_all_epochs(phase=phase)
        num_categories = len(summed_matrices[0])
        num_epochs = len(summed_matrices) if sum(sum(np.array(summed_matrices[-1]))) > 0 else len(summed_matrices) - 1
        precision = np.zeros((num_categories, num_epochs))
        for epoch, summed_matrix in enumerate(summed_matrices):
            for i in range(num_categories):
                if epoch == num_epochs:
                    continue
                sum_ = sum(summed_matrix[i])
                if sum_ > 0:
                    precision[i,epoch] = summed_matrix[i][i]/sum_
                else:
                    precision[i,epoch] = 0
        return precision
        
    def get_recall_over_epochs(self, phase='training'):
        summed_matrices = self.get_total_matrices_for_all_epochs(phase=phase)
        num_categories = len(summed_matrices[0])
        num_epochs = len(summed_matrices) if sum(sum(np.array(summed_matrices[-1]))) > 0 else len(summed_matrices) - 1
        recall = np.zeros((num_categories, num_epochs))
        for epoch, summed_matrix in enumerate(summed_matrices):
            summed_matrix = np.array(summed_matrix)
            for i in range(num_categories):
                if epoch == num_epochs:
                    continue
                sum_ = sum(summed_matrix[:,i])
                if sum_ > 0:
                    recall[i,epoch] = summed_matrix[i,i]/sum_
                else:
                    recall[i,epoch] = 0
        return recall
        
    def get_f1_over_epochs(self, precision_over_epochs, recall_over_epochs):
        f1_over_epochs = np.zeros(precision_over_epochs.shape)
        for index, _ in np.ndenumerate(f1_over_epochs):
            if precision_over_epochs[index] == 0 or recall_over_epochs[index] == 0:
                f1_over_epochs[index] = 0.
            else:
                f1_over_epochs[index] = 2*precision_over_epochs[index]*recall_over_epochs[index]/(recall_over_epochs[index] + precision_over_epochs[index])
        return f1_over_epochs
        
    def get_total_matrix_for_latest_epoch(self, phase='training'):
        epoch = len(self.prediction_matrices)-1
        summed_matrix = self.get_total_matrix_for_given_epoch(epoch=epoch, phase=phase)
        return summed_matrix

    def get_total_matrices_for_all_epochs(self, phase='training'):
        summed_matrices = []
        for epoch in range(len(self.prediction_matrices)):
            summed_matrix = self.get_total_matrix_for_given_epoch(epoch=epoch, phase=phase)
            summed_matrices.append(summed_matrix)
        return summed_matrices

    def get_total_matrix_for_given_epoch(self, epoch=0, phase='training'):
        matrices = self.get_matrices_for_epoch(epoch)
        summed_matrix = [ [0 for _ in range(len(matrices[0][0].prediction_matrix))] for _ in range(len(matrices[0][0].prediction_matrix)) ]
        
        for matrix, phase_ in matrices:
            if (phase_ and phase =='training') or (not phase_ and phase != 'training'):
                for row in range(len(summed_matrix)):
                    for col in range(len(summed_matrix)):
                        summed_matrix[row][col] += matrix.prediction_matrix[row][col]
        return summed_matrix

    def get_matrices_for_latest_epoch(self):
        return self.get_matrices_for_epoch(epoch=len(self.prediction_matrices)-1)

    @return_on_failure(0.0)
    def get_matrices_for_epoch(self, epoch):
        """ Get the n x n prediction matrix this epoch """
        matrices = self.prediction_matrices[epoch]
        return matrices

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
        matrix = self.get_matrices_for_latest_epoch()[0][0]
        return matrix

    def get_phase_for_latest_step(self):
        current_phase = self.get_matrices_for_latest_epoch()[-1][1]
        phase = 'training' if current_phase is True else 'validation'
        return phase
        
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

