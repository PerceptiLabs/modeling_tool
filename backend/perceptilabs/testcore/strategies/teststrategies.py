
from abc import ABC, abstractmethod
import numpy as np
import tensorflow as tf
import time
from perceptilabs.trainer.losses import dice, dice_coefficient, keras_dice_coef
from perceptilabs.stats.iou import IouStatsTracker, IouStats
class BaseStrategy(ABC):
    @abstractmethod
    def run(self, model_outputs, compatible_output_layers):
        raise NotImplementedError


class ConfusionMatrix(BaseStrategy):

    def run(self, model_outputs, compatible_output_layers):
        confusion_matrices = {}
        for layer in compatible_output_layers:
            labels = [x[layer].numpy() for x in model_outputs['targets']]
            outputs = [x[layer] for x in model_outputs['outputs']]
            predictions = [np.argmax(output) for output in outputs]
            targets = [np.argmax(label) for label in labels]
            num_classes = np.asarray(labels).shape[2]  # TODO: get class names
            confusion_matrix = tf.math.confusion_matrix(
                targets, predictions, num_classes=num_classes)
            confusion_matrices[layer] = confusion_matrix
        return confusion_matrices


class MetricsTable(BaseStrategy):

    def run(self, model_outputs, compatible_output_layers):
        metrics_tables = {}
        for layer in compatible_output_layers:
            if compatible_output_layers[layer] == 'image':
                metrics_tables = self._run_image_metrics(layer, model_outputs, metrics_tables)
            elif compatible_output_layers[layer] == 'categorical':
                metrics_tables = self._run_categorical_metrics(layer, model_outputs, metrics_tables)
        return metrics_tables

    def _run_categorical_metrics(self, layer, model_outputs, metrics_tables):
        metrics = {
                'categorical_accuracy': tf.keras.metrics.CategoricalAccuracy(),
                'top_k_categorical_accuracy': tf.keras.metrics.TopKCategoricalAccuracy(k=5),
                'precision': tf.keras.metrics.Precision(),
                'recall': tf.keras.metrics.Recall()
            }

        metrics_tables[layer] = {}
        labels = np.asarray([np.squeeze(x[layer].numpy())
                                for x in model_outputs['targets']])
        outputs = np.asarray([np.squeeze(x[layer])
                                for x in model_outputs['outputs']])
        predictions = np.zeros_like(outputs)
        predictions[np.arange(len(outputs)), outputs.argmax(1)] = 1
        targets = np.zeros_like(labels)
        targets[np.arange(len(labels)), labels.argmax(1)] = 1
        for metric in ['categorical_accuracy', 'top_k_categorical_accuracy']:
            metrics[metric].update_state(labels, outputs)
            metrics_tables[layer][metric] = np.float(
                metrics[metric].result().numpy())
            metrics[metric].reset_states()
        for metric in ['precision', 'recall']:
            metrics[metric].update_state(targets, predictions)
            metrics_tables[layer][metric] = np.float(
                metrics[metric].result().numpy())
            metrics[metric].reset_states()
        return metrics_tables


    def _run_image_metrics(self, layer, model_outputs, metrics_tables):
        metrics = {
            'dice_coefficient': dice_coefficient,
            'keras_dice_coefficient': keras_dice_coef,
            'IoU': IouStatsTracker(),
        }
        metrics_tables[layer] = {}
        targets = np.asarray([x[layer].numpy()
                                for x in model_outputs['targets']])
        outputs = np.asarray([x[layer]
                                for x in model_outputs['outputs']])
        metrics['IoU'].update(predictions_batch=outputs, targets_batch=targets, epochs_completed=0, is_training=False, steps_completed=0, threshold=0.5)
        iou_stats = metrics['IoU'].save()
        metrics_tables[layer]['IoU'] = float(iou_stats.get_iou_for_latest_step())
        metrics_tables[layer]['dice_coefficient'] =round(float(dice_coefficient(outputs, targets).numpy()),2) #pytest was failing without the conversions
        metrics_tables[layer]['keras_dice_coefficient'] =round(float(keras_dice_coef(outputs, targets).numpy()),2) #pytest was failing without the conversions
        return metrics_tables


class OutputVisualization(BaseStrategy):

    def run(self, model_inputs, model_outputs, compatible_output_layers):
        """
        takes all the model outputs and calculates the loss on each sample. Best performing 5 samples and worst performing 5 samples are returned.
        Args:
            model_inputs ([list]): inputs list
            model_outputs ([dict]): contains lists of targets and predictions
            compatible_output_layers ([dict]): dict containing compatible layers and their datatypes
        returns:
            best 5 segmented images and their inputs and original segmentations and the worst 5.
        """
        output_images = {}
        for layer in compatible_output_layers:
            output_images[layer] = {}
            losses = []
            predictions = [x[layer] for x in model_outputs['outputs']]
            targets = [x[layer].numpy() for x in model_outputs['targets']]
            inputs = [list(x.values())[0] for x in model_inputs] #TODO: need to fix this for multi input/output
            for target, prediction  in zip(targets, predictions):
                loss = dice(target, prediction).numpy()
                losses.append(loss)
            sorted_loss_indices = sorted(range(len(losses)), key=lambda i: losses[i])
            n = min(5, int(len(inputs)/2))
            top_n_indices = sorted_loss_indices[-n:]
            bottom_n_indices = sorted_loss_indices[:n]
            selected_indices = bottom_n_indices + top_n_indices
            selected_inputs = [inputs[i] for i in selected_indices]
            selected_targets = [targets[i] for i in selected_indices]
            selected_predictions = [predictions[i] for i in selected_indices]
            selected_losses = [losses[i] for i in selected_indices]

            output_images[layer] = {
                "inputs":selected_inputs,
                "targets":selected_targets,
                "predictions":selected_predictions,
                "losses":selected_losses,
                }
        return output_images