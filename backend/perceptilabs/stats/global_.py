import numpy as np

from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import TrainingStats, TrainingStatsTracker
from perceptilabs.stats.loss import LossStatsTracker



class GlobalStats(TrainingStats):
    def __init__(self, loss=None):
        self._loss = loss
        
    def get_data_objects(self):
        # TODO: docs
        
        training_loss_over_steps = self._loss.get_loss_over_steps_in_latest_epoch(phase='training')
        validation_loss_over_steps = self._loss.get_loss_over_steps_in_latest_epoch(phase='validation')
        
        validation_loss_over_steps = training_loss_over_steps + validation_loss_over_steps  # The frontend plots the training loss last, so this gives the effect that the validation curve is a continuation of the training curve.
        
        loss_over_steps = create_data_object(
            [validation_loss_over_steps, training_loss_over_steps],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        training_loss_over_epochs = self._loss.get_average_loss_over_epochs(phase='training')
        validation_loss_over_epochs = self._loss.get_average_loss_over_epochs(phase='validation')
        loss_over_epochs = create_data_object(
            [validation_loss_over_epochs, training_loss_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        data_objects = {
            'Loss': {
                'OverSteps': loss_over_steps,
                'OverEpochs': loss_over_epochs
            }
        }
        return data_objects
    

class GlobalStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._loss_tracker = LossStatsTracker()
        
    def update(self, **kwargs):
        self._loss_tracker.update(**kwargs)        
            
    def save(self):
        """ Save the tracked values into a TrainingStats object """
        return GlobalStats(loss=self._loss_tracker.save())
        
