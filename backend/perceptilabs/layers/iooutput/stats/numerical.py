import numpy as np
import tensorflow as tf

from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.loss import LossStatsTracker
from perceptilabs.stats.r_squared import RSquaredStatsTracker
from perceptilabs.stats.mae import MeanAbsoluteErrorStatsTracker
from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import OutputStats


class NumericalOutputStats(OutputStats):
    def __init__(self, loss=None, r_squared=None, mae=None, predictions=None, targets=None):
        self._loss = loss
        self._r_squared = r_squared
        self._mae = mae
        self._predictions = predictions
        self._targets = targets

    @property
    def loss(self):
        return self._loss

    @property
    def r_squared(self):
        return self._r_squared

    @property
    def predictions(self):
        return self._predictions

    @property
    def mae(self):
        return self._mae

    @property
    def targets(self):
        return self._targets
    
    def __eq__(self, other):
        return (
            self.loss == other.loss and
            self.r_squared == other.r_squared and
            self.mae == other.mae and
            np.all(self.predictions == other.predictions) and            
            np.all(self.targets == other.targets)             
        )

    def _get_average_sample(self, type_='prediction'):
        batch = self._predictions if type_ == 'prediction' else self._targets
        average = np.average(batch, axis=0)
        return average

    def _get_arbitrary_sample(self, type_='prediction'):
        """
            always return last sample of the batch
        """
        batch = self._predictions if type_ == 'prediction' else self._targets
        sample = batch[-1]
        return sample

    def get_data_objects(self):
        """
            Gets the data objects for categorical outputs. There are graphs for loss over all epochs, 
            mean absolute error over epochs, a PvG bar graph, and R squared over epochs.

        """
        r_sq_over_epochs = self._get_dataobj_r_squared()
        loss_over_epochs = self._get_dataobj_loss()
        mae_over_epochs = self._get_dataobj_mae()

        pred_value = self._get_arbitrary_sample(type_='prediction')
        target_value = self._get_arbitrary_sample(type_='target')
        pred_vs_target_obj = create_data_object(
            [pred_value, target_value],
            name_list=['Prediction', 'Ground Truth']
        )

        data_objects = {
            'LossAndRSquared': {
                'LossOverEpochs':loss_over_epochs,
                'RSquaredOverEpochs': r_sq_over_epochs
            },
            'PvGAndMAE': {
                'MAEOverEpochs': mae_over_epochs,
                'Sample': pred_vs_target_obj,
            },
            'ViewBox': {
                'Output': create_data_object([target_value])
            }
        }
        return data_objects

    def _get_dataobj_mae(self):
        training_mae_over_epochs, validation_mae_over_epochs = self.get_mae_over_epochs()

        if len(training_mae_over_epochs) > 1 and len(validation_mae_over_epochs) > 1:
            dataobj_mae_over_steps = create_data_object(
                [validation_mae_over_epochs, training_mae_over_epochs],
                type_list=['line', 'line'],
                name_list=['Validation', 'Training']
            )
        else:
            dataobj_mae_over_steps = create_data_object(
                [validation_mae_over_epochs, training_mae_over_epochs],
                type_list=['scatter', 'scatter'],
                name_list=['Validation', 'Training']
            )

        return dataobj_mae_over_steps

    def _get_dataobj_loss(self):
        training_loss_over_epochs, validation_loss_over_epochs = self.get_loss_over_epochs()

        if len(training_loss_over_epochs) > 1 and len(validation_loss_over_epochs) > 1:
            dataobj_loss_over_steps = create_data_object(
                [validation_loss_over_epochs, training_loss_over_epochs],
                type_list=['line', 'line'],
                name_list=['Validation', 'Training']
            )
        else:
            dataobj_loss_over_steps = create_data_object(
                [validation_loss_over_epochs, training_loss_over_epochs],
                type_list=['scatter', 'scatter'],
                name_list=['Validation', 'Training']
            )

        return dataobj_loss_over_steps

    def _get_dataobj_r_squared(self):
        training_r_sq_over_epochs, validation_r_sq_over_epochs = self.get_r_sq_over_epochs()

        if len(training_r_sq_over_epochs) > 1 and len(validation_r_sq_over_epochs) > 1:
            dataobj_r_sq_over_steps = create_data_object(
                [validation_r_sq_over_epochs, training_r_sq_over_epochs],
                type_list=['line', 'line'],
                name_list=['Validation', 'Training']
            )
        else:
            dataobj_r_sq_over_steps = create_data_object(
                [validation_r_sq_over_epochs, training_r_sq_over_epochs],
                type_list=['scatter', 'scatter'],
                name_list=['Validation', 'Training']
            )

        return dataobj_r_sq_over_steps


    def get_summary(self):
        """ Gets the stats summary for this layer 

        Returns:
            A dictionary with the final training/validation loss and accuracy
        """        
        return {
            'loss_training': self._loss.get_loss_for_latest_step(phase='training'),
            'loss_validation': self._loss.get_loss_for_latest_step(phase='validation'),
        }

    def get_mae_over_epochs(self):
        """
        Returns lists of mean absolute errors from all epochs.
        """
        training_mae_over_epochs = self._mae.get_loss_over_epochs(
            phase='training')
        validation_mae_over_epochs = self._mae.get_loss_over_epochs(
            phase='validation')
        return training_mae_over_epochs, validation_mae_over_epochs

    def get_r_sq_over_epochs(self):
        """
        Returns lists of r squared values from all epochs.
        """
        training_r_sq_over_epochs = self._r_squared.get_r_squared_over_epochs(
            phase='training')
        validation_r_sq_over_epochs = self._r_squared.get_r_squared_over_epochs(
            phase='validation')
        return training_r_sq_over_epochs, validation_r_sq_over_epochs

    def get_loss_over_epochs(self):
        """
        Returns lists of losses from all epochs.
        """
        training_loss_over_epochs = self._loss.get_loss_over_epochs(
            phase='training')
        validation_loss_over_epochs = self._loss.get_loss_over_epochs(
            phase='validation')
        return training_loss_over_epochs, validation_loss_over_epochs

    def get_end_results(self):
        """
        Returns accuracy from final epoch for results summary after training ends.
        """
        training_r_sq_over_epochs, validation_r_sq_over_epochs = self.get_r_sq_over_epochs()
        r_sq = {
            'training': training_r_sq_over_epochs[-1],
            'validation': validation_r_sq_over_epochs[-1]
        }
        return {'R Squared':r_sq}


class NumericalOutputStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._datatype = 'numerical'
        self._loss_tracker = LossStatsTracker()            
        self._r_squared_tracker = RSquaredStatsTracker()
        self._mae_tracker = MeanAbsoluteErrorStatsTracker()
        self._predictions = tf.constant([0.0])
        self._targets = tf.constant([0.0])

    def update(self, **kwargs):
        self._loss_tracker.update(**kwargs)
        self._r_squared_tracker.update(**kwargs)
        self._mae_tracker.update(**kwargs)
        self._predictions = kwargs['predictions_batch']
        self._targets = kwargs['targets_batch']
            
    def save(self):
        """ Save the tracked values into a TrainingStats object """
        return NumericalOutputStats(
            loss=self._loss_tracker.save(),                                
            r_squared=self._r_squared_tracker.save(),
            mae=self._mae_tracker.save(),
            predictions=self._predictions.numpy(),
            targets=self._targets.numpy()                
        )
    
    @property
    def loss_tracker(self):
        return self._loss_tracker

    @property
    def r_squared_tracker(self):
        return self._r_squared_tracker

    @property
    def mae_tracker(self):
        return self._mae_tracker

    @property
    def predictions(self):
        return self._predictions

    @property
    def targets(self):
        return self._targets
    
    def __eq__(self, other):
        return (
            self.loss_tracker == other.loss_tracker and
            self.r_squared_tracker == other.r_squared_tracker and
            self.mae_tracker == other.mae_tracker and
            np.all(self.predictions == other.predictions) and            
            np.all(self.targets == other.targets)             
        )
