from typing import Tuple

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.trainer.stats.base import TrainingStatsTracker
from perceptilabs.trainer.stats.accuracy import AccuracyStatsTracker, AccuracyStats
from perceptilabs.trainer.stats.loss import LossStatsTracker, LossStats
from perceptilabs.trainer.stats.utils import return_on_failure



class CategoricalOutputStats:
    def __init__(self, accuracy=None, losses=None):
        self.accuracy = accuracy
        self.losses = losses or []

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
        self._accuracy_tracker = AccuracyStatsTracker()
        self._loss_tracker = LossStatsTracker()  

    def update(self, **kwargs):
        self._accuracy_tracker.update(**kwargs)
        self._loss_tracker.update(**kwargs)
        
    def save(self):
        """ Save the tracked values into a TrainingStats object """

        accuracy = self._accuracy_tracker.save()
        loss = self._loss_tracker.save()
        
        return CategoricalOutputStats(accuracy, loss)

