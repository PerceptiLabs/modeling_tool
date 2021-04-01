from typing import Tuple
import copy
import numpy as np
import tensorflow as tf

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.trainer.stats.base import TrainingStatsTracker


class PredictionMatrix:
    def __init__(self, correct, incorrect):
        self.correct = correct
        self.incorrect = incorrect

    @property
    def total(self):
        return self.correct + self.incorrect


def return_on_failure(value):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args,**kwargs)
            except:
                return value
        return applicator
    return decorate

    
class CategoricalOutputStats:
    def __init__(self, prediction_matrices=None, losses=None):
        self.prediction_matrices = prediction_matrices or []
        self.losses = losses or []

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

    @return_on_failure(0.0)    
    def get_loss_for_step(self, epoch, step):
        """ Loss of a step/batch """         # TODO: rename step/steps -> batch/batches everywhere?
        loss, _ = self.losses[epoch][step]
        return loss

    @return_on_failure([0.0])    
    def get_loss_over_steps(self, epoch, phase='training'):
        """ Loss as a series over all steps in an epoch """                
        losses = []
        for step in range(len(self.losses[epoch])):
            _, is_training = self.losses[epoch][step]
            
            if (
                    (is_training and phase in ['both', 'training']) or
                    (not is_training and phase in ['both', 'validation'])
            ):
                loss = self.get_loss_for_step(epoch, step)
                losses.append(loss)
                
        return losses

    def get_loss_over_steps_in_latest_epoch(self, phase='training'):
        """ Loss as a series over all steps in the latest epoch """                        
        losses = self.get_loss_over_steps(
            epoch=len(self.losses)-1,
            phase=phase
        )
        return losses

    @return_on_failure(0.0)
    def get_average_loss_for_epoch(self, epoch, phase='training'):
        """ Average loss of an epoch """

        losses = self.get_loss_over_steps(epoch, phase=phase)
        average = sum(losses) / len(losses)
        return average

    @return_on_failure(0.0)
    def get_average_loss_over_epochs(self, phase='training'):
        """ Average loss over all epochs epoch """

        averages = []
        for epoch in range(len(self.losses)):       
            average = self.get_average_loss_for_epoch(epoch, phase=phase)
            averages.append(average)
                
        return averages


class CategoricalOutputStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._prediction_matrices = []  # A list of list. Outer list is per epoch, inner list is per step within that epoch
        self._losses = []  # A list of list. Outer list is per epoch, inner list is per step within that epoch

    def update(self, **kwargs):
        self._store_prediction_matrix(
            kwargs['predictions_batch'], kwargs['targets_batch'],
            kwargs['epochs_completed'], kwargs['steps_completed'],
            kwargs['is_training']
        )
        self._store_losses(kwargs['loss'], kwargs['epochs_completed'], kwargs['steps_completed'], kwargs['is_training'])
        
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

    def _store_losses(self, loss, epochs_completed, steps_completed, is_training):
        if len(self._losses) <= epochs_completed:
            self._losses.append(list())  # Create list to hold steps for epoch.
            
        self._losses[epochs_completed].append((loss.numpy(), is_training))        
        
    def save(self):
        """ Save the tracked values into a TrainingStats object """

        # Convert to a tuple of tuples to make it immutable.
        pred_matrices = tuple([  
            tuple(step_matrices)
            for step_matrices in self._prediction_matrices
        ])
        losses = tuple([  
            tuple(epoch_losses)
            for epoch_losses in self._losses
        ])
        
        return CategoricalOutputStats(pred_matrices, losses)

