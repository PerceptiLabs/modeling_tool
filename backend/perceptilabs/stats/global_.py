import numpy as np

from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import TrainingStats, TrainingStatsTracker
from perceptilabs.stats.loss import LossStatsTracker


class GlobalStats(TrainingStats):
    def __init__(self, loss=None):
        self._loss = loss

    @property
    def loss(self):
        return self._loss

    def __eq__(self, other):
        return self.loss == other.loss

    def get_data_objects(self):
        training_loss_over_steps, validation_loss_over_steps = self.get_loss_over_steps_in_latest_epoch()
        # The frontend plots the training loss last, so this gives the effect that the validation curve is a continuation of the training curve.
        validation_loss_over_steps = training_loss_over_steps + validation_loss_over_steps

        loss_over_steps = create_data_object(
            [validation_loss_over_steps, training_loss_over_steps],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        training_loss_over_epochs, validation_loss_over_epochs = self.get_loss_over_epochs()

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

    def get_loss_over_steps_in_latest_epoch(self):
        """
        returns lists of training and validation losses from latest epoch
        """
        training_loss_over_steps = self._loss.get_loss_over_steps_in_latest_epoch(
            phase='training')
        validation_loss_over_steps = self._loss.get_loss_over_steps_in_latest_epoch(
            phase='validation')
        return training_loss_over_steps, validation_loss_over_steps

    def get_loss_over_epochs(self):
        """
        returns lists of training and validation losses over all epochs.
        """
        training_loss_over_epochs = self._loss.get_loss_over_epochs(
            phase='training')
        validation_loss_over_epochs = self._loss.get_loss_over_epochs(
            phase='validation')
        return training_loss_over_epochs, validation_loss_over_epochs

    def get_end_results(self):
        """
        Returns the global metrics from final epoch for results summary after training ends.
        """
        loss = dict()
        training_loss_over_steps, validation_loss_over_steps = self.get_loss_over_steps_in_latest_epoch()

        loss['training'] = training_loss_over_steps[-1] if len(training_loss_over_steps) > 0 else 0.0
        loss['validation'] = validation_loss_over_steps[-1] if len(validation_loss_over_steps) > 0 else 0.0

        return {'Global_Loss':loss}
    

class GlobalStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._loss_tracker = LossStatsTracker()

    def update(self, **kwargs):
        self._loss_tracker.update(**kwargs)

    def save(self):
        """ Save the tracked values into a TrainingStats object """
        return GlobalStats(loss=self._loss_tracker.save())

    @property
    def loss_tracker(self):
        return self._loss_tracker

    def __eq__(self, other):
        return self.loss_tracker == other.loss_tracker
    

