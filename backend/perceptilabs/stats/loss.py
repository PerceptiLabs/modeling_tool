from typing import Tuple

from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.utils import return_on_failure


class LossStats:
    def __init__(self, losses=None):
        self.losses = losses or ()

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

    
class LossStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._losses = []  # A list of list. Outer list is per epoch, inner list is per step within that epoch

    def update(self, **kwargs):
        self._store_losses(kwargs['loss'], kwargs['epochs_completed'], kwargs['steps_completed'], kwargs['is_training'])
        
    def _store_losses(self, loss, epochs_completed, steps_completed, is_training):
        if len(self._losses) <= epochs_completed:
            self._losses.append(list())  # Create list to hold steps for epoch.
            
        self._losses[epochs_completed].append((loss.numpy(), is_training))        
        
    def save(self):
        """ Save the tracked values into a TrainingStats object """
        
        # Convert to a tuple of tuples to make it immutable.
        losses = tuple([  
            tuple(epoch_losses)
            for epoch_losses in self._losses
        ])
        return LossStats(losses)

