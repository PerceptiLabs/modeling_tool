import numpy as np

from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import TrainingStats


class ImageOutputStats(TrainingStats):
    def __init__(self, iou=None, predictions=None, targets=None):
        self._iou = iou
        self._predictions = predictions
        self._targets = targets

    def _get_average_sample(self, type_='prediction'):
        batch = self._predictions if type_ == 'prediction' else self._targets
        average = np.average(batch, axis=0)
        return average

    def _get_arbitrary_sample(self, type_='prediction'):
        batch = self._predictions if type_ == 'prediction' else self._targets
        sample = batch[0]
        return sample

    def get_data_objects(self):
        # TODO: docs
        iou_over_steps, iou_over_epochs = self._get_dataobj_iou()

        pred_value = self._get_arbitrary_sample(type_='prediction')
        target_value = self._get_arbitrary_sample(type_='target')
        pred_vs_target_obj = create_data_object(
            [pred_value, target_value],
            name_list=['Prediction', 'Ground Truth']
        )

        pred_batch_average = self._get_average_sample(type_='prediction')
        target_batch_average = self._get_average_sample(type_='target')
        avg_pred_vs_target_obj = create_data_object(
            [pred_batch_average, target_batch_average],
            name_list=['Prediction', 'Ground Truth']
        )
        
        data_objects = {
            'IoU': {  # TODO: rename to IOU when frontend is updated
                'OverSteps': iou_over_steps,
                'OverEpochs': iou_over_epochs
            },
            'PvG': {
                'Sample': pred_vs_target_obj,
                'BatchAverage': avg_pred_vs_target_obj
            },
            'ViewBox': {
                'Output': create_data_object([target_value])
            }
        }
        return data_objects

    def _get_dataobj_iou(self):
        training_iou_over_steps = self._iou.get_iou_over_steps_in_latest_epoch(phase='training')
        validation_iou_over_steps = self._iou.get_iou_over_steps_in_latest_epoch(phase='validation')
        
        validation_iou_over_steps = training_iou_over_steps + validation_iou_over_steps  # The frontend plots the training iou last, so this gives the effect that the validation curve is a continuation of the training curve.
        
        dataobj_iou_over_steps = create_data_object(
            [validation_iou_over_steps, training_iou_over_steps],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )

        training_iou_over_epochs = self._iou.get_average_iou_over_epochs(phase='training')
        validation_iou_over_epochs = self._iou.get_average_iou_over_epochs(phase='validation')
        
        dataobj_iou_over_epochs = create_data_object(
            [validation_iou_over_epochs, training_iou_over_epochs],
            type_list=['line', 'line'],
            name_list=['Validation', 'Training']
        )        
        return dataobj_iou_over_steps, dataobj_iou_over_epochs
        
