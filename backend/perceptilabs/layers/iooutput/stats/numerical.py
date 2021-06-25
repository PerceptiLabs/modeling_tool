import numpy as np

from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import OutputStats


class NumericalOutputStats(OutputStats):
    def __init__(self, loss=None, r_squared=None, mae=None, predictions=None, targets=None):
        self._loss = loss
        self._r_squared = r_squared
        self._mae = mae
        self._predictions = predictions
        self._targets = targets

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

        dataobj_mae_over_steps = create_data_object(
            [validation_mae_over_epochs, training_mae_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        return dataobj_mae_over_steps

    def _get_dataobj_loss(self):
        training_loss_over_epochs, validation_loss_over_epochs = self.get_loss_over_epochs()

        dataobj_loss_over_steps = create_data_object(
            [validation_loss_over_epochs, training_loss_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        return dataobj_loss_over_steps

    def _get_dataobj_r_squared(self):
        training_r_sq_over_epochs, validation_r_sq_over_epochs = self.get_r_sq_over_epochs()
        dataobj_loss_over_steps = create_data_object(
            [validation_r_sq_over_epochs, training_r_sq_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )
        return dataobj_loss_over_steps


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
