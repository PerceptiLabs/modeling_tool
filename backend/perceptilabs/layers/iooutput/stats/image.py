import numpy as np
import cv2
import math

from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import OutputStats


class ImageOutputStats(OutputStats):
    def __init__(self, iou=None, predictions=None, targets=None, loss=None):
        self._iou = iou
        self._predictions = predictions
        self._targets = targets
        self._loss = loss

    def _get_average_sample(self, type_='prediction'):
        batch = self._predictions if type_ == 'prediction' else self._targets
        average = np.average(batch, axis=0)
        return average

    def _get_arbitrary_sample(self, type_='prediction'):
        """always return last sample of the batch
        """
        batch = self._predictions if type_ == 'prediction' else self._targets
        sample = batch[-1]
        return sample

    def get_data_objects(self):
        # TODO: docs
        _, iou_over_epochs = self._get_dataobj_iou()
        loss_over_epochs = self._get_dataobj_loss()

        pred_value = self._get_arbitrary_sample(type_='prediction')
        target_value = self._get_arbitrary_sample(type_='target')

        if pred_value.shape[-1] <= 1:
            # Add color channels to the grayscale predictions and targets so they can be overlayed with each other
            pred_value_rgb = cv2.cvtColor(pred_value, cv2.COLOR_GRAY2RGB)
            target_value_rgb = cv2.cvtColor(target_value, cv2.COLOR_GRAY2RGB)
            white_lo = np.array([10,10,10])
            white = np.array([255,255,255])
            
            mask = cv2.inRange(target_value_rgb, white_lo, white)

            target_value_rgb[mask>0] = (255,0,0)
            
            blended = cv2.addWeighted(pred_value_rgb, 0.9, target_value_rgb, 0.1, 0)
            data_obj_overlayed_image = create_data_object([blended], normalize=False)

        else:
            overlayed_image = cv2.addWeighted(target_value, 0.7, pred_value, 0.3, 0)

            data_obj_overlayed_image = create_data_object([overlayed_image])
        
        data_objects = {
            'IoUAndLoss': { 
                'LossOverEpochs': loss_over_epochs,
                'IoUOverEpochs': iou_over_epochs
            },
            'PvGAndImage': {
                'Sample': data_obj_overlayed_image,
                'Prediction': create_data_object([pred_value])
            },
            'ViewBox': {
                'Output': create_data_object([target_value])
            }
        }
        return data_objects

    def _get_dataobj_loss(self):
        training_loss_over_epochs, validation_loss_over_epochs = self.get_loss_over_epochs()

        dataobj_loss_over_epochs = create_data_object(
            [validation_loss_over_epochs, training_loss_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        return dataobj_loss_over_epochs

    def _get_dataobj_iou(self):
        training_iou_over_steps = self._iou.get_iou_over_steps_in_latest_epoch(phase='training')
        validation_iou_over_steps = self._iou.get_iou_over_steps_in_latest_epoch(phase='validation')
        
        validation_iou_over_steps = training_iou_over_steps + validation_iou_over_steps  # The frontend plots the training iou last, so this gives the effect that the validation curve is a continuation of the training curve.
        
        dataobj_iou_over_steps = create_data_object(
            [validation_iou_over_steps, training_iou_over_steps],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        training_iou_over_epochs, validation_iou_over_epochs = self.get_iou_over_epochs()
        
        dataobj_iou_over_epochs = create_data_object(
            [validation_iou_over_epochs, training_iou_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )        
        return dataobj_iou_over_steps, dataobj_iou_over_epochs
        
    def get_summary(self):
        """ Gets the stats summary for this layer 

        Returns:
            A dictionary with the final training/validation loss and iou
        """        
        return {
            'loss_training': self._loss.get_loss_for_latest_step(phase='training'),
            'loss_validation': self._loss.get_loss_for_latest_step(phase='validation'),
            'iou_training': self._iou.get_iou_for_latest_step(phase='training'),
            'iou_validation': self._iou.get_iou_for_latest_step(phase='validation')
        }

    def get_iou_over_epochs(self):
        """
        Returns lists of iou from all epochs.
        """
        training_iou_over_epochs = self._iou.get_iou_over_epochs(
            phase='training')
        validation_iou_over_epochs = self._iou.get_iou_over_epochs(
            phase='validation')
        return training_iou_over_epochs, validation_iou_over_epochs

    def get_loss_over_epochs(self):
        """
        Returns lists of iou from all epochs.
        """
        training_iou_over_epochs = self._iou.get_iou_over_epochs(
            phase='training')
        validation_iou_over_epochs = self._iou.get_iou_over_epochs(
            phase='validation')
        return training_iou_over_epochs, validation_iou_over_epochs
        
    def get_end_results(self):
        """
        Returns IOU from final epoch for results summary after training ends.
        """
        training_iou_over_epochs, validation_iou_over_epochs = self.get_iou_over_epochs()
        iou = {
            'training': training_iou_over_epochs[-1],
            'validation': validation_iou_over_epochs[-1],
        }
        return {'IOU': iou}
