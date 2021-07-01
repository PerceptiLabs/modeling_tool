
from typing import Tuple
import tensorflow as tf
import sklearn
from sklearn.metrics import r2_score
from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.utils import return_on_failure

class RSquaredStats:
    def __init__(self, r_squared_values=None):
        self.r_squared_values = r_squared_values or ()

    @return_on_failure(0.0)    
    def get_r_squared_for_step(self, epoch, step):
        """ R Squared of a step/batch """         # TODO: rename step/steps -> batch/batches everywhere?
        r_squared, _ = self.r_squared_values[epoch][step]
        return r_squared

    @return_on_failure(0.0)        
    def get_r_squared_for_latest_step(self, phase='both'): 
        """ R Squared of the latest a step """
        r_squared_list = self.get_r_squared_over_steps_in_latest_epoch(phase=phase)
        return r_squared_list[-1]

    @return_on_failure([0.0])    
    def get_r_squared_over_steps(self, epoch, phase='training'):
        """ R Squared as a series over all steps in an epoch """                
        r_squared_values = []
        for step in range(len(self.r_squared_values[epoch])):
            _, is_training = self.r_squared_values[epoch][step]
            
            if (
                    (is_training and phase in ['both', 'training']) or
                    (not is_training and phase in ['both', 'validation'])
            ):
                r_squared_value = self.get_r_squared_for_step(epoch, step)
                r_squared_values.append(r_squared_value)
                
        return r_squared_values

    def get_r_squared_over_steps_in_latest_epoch(self, phase='training'):
        """ R Squared as a series over all steps in the latest epoch """                        
        r_squared_values = self.get_r_squared_over_steps(
            epoch=len(self.r_squared_values)-1,
            phase=phase
        )
        return r_squared_values

    @return_on_failure(0.0)
    def get_average_r_squared_for_epoch(self, epoch, phase='training'):
        """ Average R Squared of an epoch """

        r_squared_values = self.get_r_squared_over_steps(epoch, phase=phase)
        average = sum(r_squared_values) / len(r_squared_values)
        return average

    @return_on_failure(0.0)
    def get_r_squared_over_epochs(self, phase='training'):
        """ Average R Squared over all epochs epoch """

        averages = []
        for epoch in range(len(self.r_squared_values)):       
            average = self.get_average_r_squared_for_epoch(epoch, phase=phase)
            averages.append(average)
                
        return averages

class RSquaredStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._r_squared_values = []  # A list of list. Outer list is per epoch, inner list is per step within that epoch

    def update(self, **kwargs):
        self._store_r_squared_values(kwargs['predictions_batch'], kwargs['targets_batch'],
            kwargs['loss'], kwargs['epochs_completed'], kwargs['steps_completed'],
            kwargs['is_training'],
        )

    def _store_r_squared_values(self, predictions_batch, targets_batch, loss, epochs_completed, steps_completed, is_training):
        if len(self._r_squared_values) <= epochs_completed:
            self._r_squared_values.append(list())  # Create list to hold steps for epoch.

        if len(targets_batch.shape) == 1 or len(predictions_batch.shape) == 1:
            targets_batch = tf.reshape(targets_batch, (-1,1))
            predictions_batch = tf.reshape(predictions_batch, (-1,1))
            
        r_squared = r2_score(targets_batch, predictions_batch)
        self._r_squared_values[epochs_completed].append((r_squared, is_training))        
        
    def save(self):
        """ Save the tracked values into a TrainingStats object """
        
        # Convert to a tuple of tuples to make it immutable.
        r_squared_values = tuple([  
            tuple(epoch_r_squared_values)
            for epoch_r_squared_values in self._r_squared_values
        ])
        return RSquaredStats(r_squared_values)