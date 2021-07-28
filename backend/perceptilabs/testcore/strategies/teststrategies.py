
from abc import ABC, abstractmethod
import numpy as np
import tensorflow as tf
import time
from perceptilabs.trainer.losses import dice_coefficient
from perceptilabs.stats.iou import IouStatsTracker, IouStats
class BaseStrategy(ABC):
    @abstractmethod
    def run(self, model_outputs, compatible_output_layers):
        raise NotImplementedError


class ConfusionMatrix(BaseStrategy):

    def run(self, model_outputs, compatible_output_layers):
        confusion_matrices = {}
        for layer in compatible_output_layers:
            labels = [x[layer].numpy() for x in model_outputs['labels']]
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
                                for x in model_outputs['labels']])
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
            'IoU': IouStatsTracker(),
        }
        metrics_tables[layer] = {}
        labels = np.asarray([x[layer].numpy()
                                for x in model_outputs['labels']])
        outputs = np.asarray([x[layer]
                                for x in model_outputs['outputs']])
        metrics['IoU'].update(predictions_batch=outputs, targets_batch=labels, epochs_completed=0, is_training=False, steps_completed=0, threshold=0.5)
        iou_stats = metrics['IoU'].save()
        metrics_tables[layer]['IoU'] = float(iou_stats.get_iou_for_latest_step())
        metrics_tables[layer]['dice_coefficient'] =round(float(dice_coefficient(outputs, labels).numpy()),2) #pytest was failing without the conversions
        return metrics_tables
