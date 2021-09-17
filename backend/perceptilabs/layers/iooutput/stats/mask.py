import numpy as np
import cv2
import math

import tensorflow as tf
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.accuracy import AccuracyStatsTracker
from perceptilabs.stats.loss import LossStatsTracker
from perceptilabs.stats.iou import IouStatsTracker
from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import OutputStats

from perceptilabs.stats.base import PreviewStats


class MaskOutputStats(OutputStats):
    def __init__(self, iou=None, predictions=None, targets=None, loss=None, inputs=None):
        self._iou = iou
        self._predictions = predictions
        self._targets = targets
        self._loss = loss
        self._inputs = inputs

    @property
    def loss(self):
        return self._loss

    @property
    def iou(self):
        return self._iou

    @property
    def predictions(self):
        return self._predictions

    @property
    def targets(self):
        return self._targets

    @property
    def inputs(self):
        return self._inputs

    def __eq__(self, other):
        return (
            self.loss == other.loss and
            self.iou == other.iou and
            np.all(self.predictions == other.predictions) and
            np.all(self.targets == other.targets) and
            np.all(self.inputs == other.inputs)
        )

    def _get_average_sample(self, type_='prediction'):
        batch = self._predictions if type_ == 'prediction' else self._targets
        average = np.average(batch, axis=0)
        return average

    def _get_arbitrary_sample(self, type_='prediction'):
        """always return last sample of the batch
        """
        if type_ == 'prediction':
            batch = self._predictions
        elif type_ == 'target':
            batch = self._targets
        elif type_ == 'input':
            batch = self._inputs
            batch = list(batch.values())[0].numpy() #works only if there is one input layer
        sample = batch[-1]
        return sample

    def get_data_objects(self):
        # TODO: docs
        _, iou_over_epochs = self._get_dataobj_iou()
        loss_over_epochs = self._get_dataobj_loss()

        pred_value = self._get_arbitrary_sample(type_='prediction')
        target_value = self._get_arbitrary_sample(type_='target')
        input_image = self._get_arbitrary_sample(type_='input')

        #overlaying predicted segmentation on input image
        # done in the similar way as in testcore
        predicted_segmentation = np.argmax(pred_value, axis=2)

        fig, axs = plt.subplots(1, 1, figsize=(3,3))
        axs.pcolormesh(np.squeeze(np.mean(input_image, axis=-1)), cmap=plt.get_cmap('gray'))
        axs.pcolormesh(predicted_segmentation, cmap=plt.get_cmap('Spectral'), alpha=0.2)
        axs.axis('off')
        axs.grid(False)
        plt.gca().invert_yaxis()
        plt.tight_layout(pad=0, w_pad=0, h_pad=0)
        fig.canvas.draw()
        data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        overlayed_image = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        data_obj_overlayed_image = create_data_object([overlayed_image], subsample_ratio=1)

        data_objects = {
            'IoUAndLoss': {
                'LossOverEpochs': loss_over_epochs,
                'IoUOverEpochs': iou_over_epochs
            },
            'PvGAndImage': {
                'Sample': data_obj_overlayed_image,
                'Prediction': create_data_object([pred_value],['mask'])
            },
            'ViewBox': {
                'Output': create_data_object([target_value],['mask'])
            }
        }
        return data_objects

    def _get_dataobj_loss(self):
        training_loss_over_epochs, validation_loss_over_epochs = self.get_loss_over_epochs()

        if len(training_loss_over_epochs) > 1 and len(validation_loss_over_epochs) > 1:
            dataobj_loss_over_epochs = create_data_object(
                [validation_loss_over_epochs, training_loss_over_epochs],
                type_list=['line', 'line'],
                name_list=['Validation', 'Training']
            )
        else:
             dataobj_loss_over_epochs = create_data_object(
                [validation_loss_over_epochs, training_loss_over_epochs],
                type_list=['scatter', 'scatter'],
                name_list=['Validation', 'Training']
            )

        return dataobj_loss_over_epochs

    def _get_dataobj_iou(self):
        training_iou_over_steps = self._iou.get_iou_over_steps_in_latest_epoch(phase='training')
        validation_iou_over_steps = self._iou.get_iou_over_steps_in_latest_epoch(phase='validation')

        training_iou_over_epochs, validation_iou_over_epochs = self.get_iou_over_epochs()

        validation_iou_over_steps = training_iou_over_steps + validation_iou_over_steps  # The frontend plots the training iou last, so this gives the effect that the validation curve is a continuation of the training curve.

        if len(validation_iou_over_steps) > 1 and len(training_iou_over_steps) > 1:

            dataobj_iou_over_steps = create_data_object(
                [validation_iou_over_steps, training_iou_over_steps],
                type_list=['line', 'line'],
                name_list=['Validation', 'Training']
            )
        else:
            dataobj_iou_over_steps = create_data_object(
                [validation_iou_over_steps, training_iou_over_steps],
                type_list=['scatter', 'scatter'],
                name_list=['Validation', 'Training']
            )

        if len(validation_iou_over_epochs) > 1 and len(training_iou_over_epochs) > 1:

            dataobj_iou_over_epochs = create_data_object(
                [validation_iou_over_epochs, training_iou_over_epochs],
                type_list=['line', 'line'],
                name_list=['Validation', 'Training']
            )

        else:
            dataobj_iou_over_epochs = create_data_object(
                [validation_iou_over_epochs, training_iou_over_epochs],
                type_list=['scatter', 'scatter'],
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
        training_loss_over_epochs = self._loss.get_loss_over_epochs(
            phase='training')
        validation_loss_over_epochs = self._loss.get_loss_over_epochs(
            phase='validation')
        return training_loss_over_epochs, validation_loss_over_epochs

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


class MaskOutputStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._loss_tracker = LossStatsTracker()
        self._iou_tracker = IouStatsTracker()
        self._predictions = tf.constant([0.0])
        self._targets = tf.constant([0.0])
        self._inputs = tf.constant([0.0])

    def update(self, **kwargs):
        self._loss_tracker.update(**kwargs)
        self._iou_tracker.update(**kwargs)
        self._predictions = kwargs['predictions_batch']
        self._targets = kwargs['targets_batch']
        self._inputs = kwargs['inputs_batch']

    def save(self):
        """ Save the tracked values into a TrainingStats object """
        return MaskOutputStats(
            loss=self._loss_tracker.save(),
            iou=self._iou_tracker.save(),
            predictions=self._predictions.numpy(),
            targets=self._targets.numpy(),
            inputs=self._inputs,
        )

    @property
    def loss_tracker(self):
        return self._loss_tracker

    @property
    def iou_tracker(self):
        return self._iou_tracker

    @property
    def predictions(self):
        return self._predictions

    @property
    def targets(self):
        return self._targets

    @property
    def inputs(self):
        return self._inputs


    def __eq__(self, other):
        return (
            self.loss_tracker == other.loss_tracker and
            self.iou_tracker == other.iou_tracker and
            np.all(self.predictions == other.predictions) and
            np.all(self.targets == other.targets) and
            np.all(self.inputs == other.inputs)
        )


class MaskPreviewStats(PreviewStats):

    def get_preview_content(self, sample):
        sample_array = np.asarray(sample)
        sample_layer_shape = sample_array.shape
        layer_sample_data_points = int(np.prod(sample_layer_shape))
        sample_data = [sample_array]
        type_list = ['mask']
        return sample_data, sample_layer_shape, layer_sample_data_points, type_list

