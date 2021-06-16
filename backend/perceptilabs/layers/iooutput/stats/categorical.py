import numpy as np

from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import OutputStats


class CategoricalOutputStats(OutputStats):
    def __init__(self, accuracy=None, predictions=None, multiclass_matrix=None, targets=None, loss=None):
        self._loss = loss
        self._accuracy = accuracy
        self._predictions = predictions
        self._multiclass_matrix = multiclass_matrix
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
            Acc over epochs, and a bar chart representing confusion matrix metrics in their total quantity
            at the latest epoch. 

        """
        acc_over_epochs = self._get_dataobj_accuracy()
        loss_over_epochs = self._get_dataobj_loss()
        conf_mtx_latest_epoch = self._get_data_obj_confusion_matrix()

        pred_value = self._get_arbitrary_sample(type_='prediction')
        target_value = self._get_arbitrary_sample(type_='target')
        pred_vs_target_obj = create_data_object(
            [pred_value, target_value],
            name_list=['Prediction', 'Ground Truth']
        )
        
        data_objects = {
            'LossAndAccuracy': {
                'LossOverEpochs':loss_over_epochs,
                'AccOverEpochs': acc_over_epochs
            },
            'PvGAndConfusionMatrix': {
                'Sample': pred_vs_target_obj,
                'LastEpoch': conf_mtx_latest_epoch,
            },
            'ViewBox': {
                'Output': create_data_object([target_value])
            }
        }
        return data_objects

    def _get_dataobj_loss(self):
        training_loss_over_epochs, validation_loss_over_epochs = self.get_loss_over_epochs()

        dataobj_loss_over_steps = create_data_object(
            [validation_loss_over_epochs, training_loss_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        return dataobj_loss_over_steps

    def _get_dataobj_accuracy(self):
        training_acc_over_steps = self._accuracy.get_accuracy_over_steps_in_latest_epoch(phase='training')
        validation_acc_over_steps = self._accuracy.get_accuracy_over_steps_in_latest_epoch(phase='validation')
        
        validation_acc_over_steps = training_acc_over_steps + validation_acc_over_steps  # The frontend plots the training accuracy last, so this gives the effect that the validation curve is a continuation of the training curve.
    

        training_acc_over_epochs, validation_acc_over_epochs = self.get_accuracy_over_epochs()
            
        dataobj_acc_over_epochs = create_data_object(
            [validation_acc_over_epochs, training_acc_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )        
        return dataobj_acc_over_epochs

    def _get_data_obj_confusion_matrix(self):
        summed_matrix = self._multiclass_matrix.get_total_matrix_for_latest_epoch(phase='training')
        dataobj_cm_in_latest_epoch = create_data_object(
            [       
                summed_matrix
            ],
            type_list=['bar_detailed']
        )

        return dataobj_cm_in_latest_epoch

    def get_summary(self):
        """ Gets the stats summary for this layer 

        Returns:
            A dictionary with the final training/validation loss and accuracy
        """        
        return {
            'loss_training': self._loss.get_loss_for_latest_step(phase='training'),
            'loss_validation': self._loss.get_loss_for_latest_step(phase='validation'),
            'accuracy_training': self._accuracy.get_accuracy_for_latest_step(phase='training'),
            'accuracy_validation': self._accuracy.get_accuracy_for_latest_step(phase='validation')
        }

    def get_accuracy_over_epochs(self):
        """
        Returns lists of accuracies from all epochs.
        """
        training_acc_over_epochs = self._accuracy.get_accuracy_over_epochs(
            phase='training')
        validation_acc_over_epochs = self._accuracy.get_accuracy_over_epochs(
            phase='validation')
        return training_acc_over_epochs, validation_acc_over_epochs

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
        # TODO: have separate metrics for numerical outputs such as R squared instead of accuracy
        #TODO: Create separate class for Numerical outputs just like CategoricalOutputStats
        training_acc_over_epochs, validation_acc_over_epochs = self.get_accuracy_over_epochs()
        accuracy = {
            'training': training_acc_over_epochs[-1]*100,
            'validation': validation_acc_over_epochs[-1]*100,
        }
        return {'Accuracy':accuracy}
