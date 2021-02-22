from dataclasses import dataclass
from collections import defaultdict
import copy
from typing import Dict, List
import numpy as np
import tensorflow as tf

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.trainer.stats.base import TrainingStatsTracker


@dataclass(frozen=True)
class GradientStats:
    minimum_series: Dict[str, List[float]]
    average_series: Dict[str, List[float]]
    maximum_series: Dict[str, List[float]]

    def get_minimum_by_layer_id(self, layer_id):
        """ Get the series of minumum gradients of this layer """ 
        return self.minimum_series[layer_id]
    
    def get_average_by_layer_id(self, layer_id):
        """ Get the series of average gradients of this layer """         
        return self.average_series[layer_id]
    
    def get_maximum_by_layer_id(self, layer_id):
        """ Get the series of maximum gradients of this layer """                 
        return self.maximum_series[layer_id]

    
class GradientStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._minimum_gradient = defaultdict(list)
        self._average_gradient = defaultdict(list)
        self._maximum_gradient = defaultdict(list)
        self._stats = None
    
    def update(self, **kwargs):
        """ Compute the gradients for each layer

        E.g., compute the smallest element of the weights and biases respectively. Then plot the smallest of these over time.
        Is there a more intuitive way to plot the gradients???
        """
        self._stats = None  # Invalidate any existing results
        gradients_by_layer = kwargs['gradients_by_layer']

        for layer_id in gradients_by_layer.keys():
            grad_weight = gradients_by_layer[layer_id]['weights']

            min_element_of_weight = tf.reduce_min(grad_weight)
            max_element_of_weight = tf.reduce_max(grad_weight)            
            avg_element_of_weight = tf.reduce_mean(grad_weight)
            
            grad_bias = gradients_by_layer[layer_id]['bias']            
            min_element_of_bias = tf.reduce_min(grad_bias)
            max_element_of_bias = tf.reduce_max(grad_bias)            
            avg_element_of_bias = tf.reduce_mean(grad_bias)

            minimum = tf.minimum(min_element_of_bias, min_element_of_weight)
            maximum = tf.maximum(min_element_of_bias, min_element_of_weight)            
            average = (avg_element_of_bias + avg_element_of_weight) / 2.0

            self._minimum_gradient[layer_id].append(minimum.numpy())
            self._average_gradient[layer_id].append(maximum.numpy())
            self._maximum_gradient[layer_id].append(average.numpy())

    def save(self):
        """ Save the tracked values into a TrainingStats object """
        if self._stats is None:  # Avoid recomputing
            self._stats = GradientStats(
                minimum_series=copy.deepcopy(self._minimum_gradient),
                average_series=copy.deepcopy(self._average_gradient),
                maximum_series=copy.deepcopy(self._maximum_gradient)            
            )
        return self._stats
