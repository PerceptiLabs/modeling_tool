
from typing import Tuple
import tensorflow as tf
import sklearn
from sklearn.metrics import mean_absolute_error
from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.utils import return_on_failure

class MeanAbsoluteErrorStats:
    def __init__(self, losses=None):
        self.losses = losses or ()

    def __eq__(self, other):
        return self.losses == other.losses

    @return_on_failure(0.0)    
    def get_loss_for_step(self, epoch, step):
        """ Mean Absolute Error of a step/batch """         # TODO: rename step/steps -> batch/batches everywhere?
        loss, _ = self.losses[epoch][step]
        return loss

    @return_on_failure(0.0)        
    def get_loss_for_latest_step(self, phase='both'): 
        """ Mean Absolute Error of the latest a step """
        loss_list = self.get_loss_over_steps_in_latest_epoch(phase=phase)
        return loss_list[-1]

    @return_on_failure([0.0])    
    def get_loss_over_steps(self, epoch, phase='training'):
        """ Mean Absolute Error as a series over all steps in an epoch """                
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
        """ Mean Absolute Error as a series over all steps in the latest epoch """                        
        losses = self.get_loss_over_steps(
            epoch=len(self.losses)-1,
            phase=phase
        )
        return losses

    @return_on_failure(0.0)
    def get_average_loss_for_epoch(self, epoch, phase='training'):
        """ Average Mean Absolute Error of an epoch """

        losses = self.get_loss_over_steps(epoch, phase=phase)
        average = sum(losses) / len(losses)
        return average

    @return_on_failure(0.0)
    def get_loss_over_epochs(self, phase='training'):
        """ Average Mean Absolute Error over all epochs epoch """

        averages = []
        for epoch in range(len(self.losses)):       
            average = self.get_average_loss_for_epoch(epoch, phase=phase)
            averages.append(average)
                
        return averages

    
class MeanAbsoluteErrorStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._loss_values = []  # A list of list. Outer list is per epoch, inner list is per step within that epoch

    def update(self, **kwargs):
        self._store_loss_values(
            kwargs['predictions_batch'], kwargs['targets_batch'],
            kwargs['loss'], kwargs['epochs_completed'], kwargs['steps_completed'],
            kwargs['is_training'],
        )

    def _store_loss_values(self, predictions_batch, targets_batch, loss, epochs_completed, steps_completed, is_training):
        if len(self._loss_values) <= epochs_completed:
            self._loss_values.append(list())  # Create list to hold steps for epoch.

        absolute_error = mean_absolute_error(targets_batch, predictions_batch)
        self._loss_values[epochs_completed].append((absolute_error, is_training))        
        
    def save(self):
        """ Save the tracked values into a TrainingStats object """
        
        # Convert to a tuple of tuples to make it immutable.
        loss_values = tuple([  
            tuple(epoch_loss_values)
            for epoch_loss_values in self._loss_values
        ])
        return MeanAbsoluteErrorStats(loss_values)

    @property
    def loss_values(self):
        return self._loss_values

    def __eq__(self, other):
        return self.loss_values == other.loss_values
