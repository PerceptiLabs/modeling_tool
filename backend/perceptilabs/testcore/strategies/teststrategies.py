
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
            num_classes = np.asarray(labels).shape[2]  #TODO: get class names
            confusion_matrix = tf.math.confusion_matrix(targets, predictions, num_classes=num_classes)
            confusion_matrices[layer] = confusion_matrix
        return confusion_matrices