
from abc import ABC, abstractmethod
import numpy as np
import tensorflow as tf
import time


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
        metrics = {'categorical_accuracy': tf.keras.metrics.CategoricalAccuracy(),
                   'top_k_categorical_accuracy': tf.keras.metrics.TopKCategoricalAccuracy(k=5),
                   'precision': tf.keras.metrics.Precision(),
                   'recall': tf.keras.metrics.Recall()}
        for layer in compatible_output_layers:
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
