import logging

import numpy as np
import tensorflow as tf

from perceptilabs.lwcore.results import LayerResults
from perceptilabs.lwcore.strategies.base import BaseStrategy
from perceptilabs.lwcore.utils import exception_to_error

from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class Tf2xInnerStrategy(BaseStrategy):
    def run(self, layer_spec, layer_class, input_results, line_offset=None):
        """ Returns a LayerResults obj. containing shapes and previews for a layer

        Args:
            layer_spec: describes the layer configuration
            layer_class: a class implementing the layer
            input_results: a dict with LayerResults from other layers in the same graph
            line_offset: used to map line numbers of the executed code to the line numbers visible to the user.
        Returns:
            an instance of LayerResults 
        """
        try:
            layer_instance = self._instantiate_layer(layer_class, layer_spec.name)
            input_tensors, has_missing_inputs = self._get_input_tensors(layer_spec, input_results)

            if has_missing_inputs:
                return self.get_default_results()            

            results = self._make_results(layer_instance, input_tensors, layer_spec.name)
            return results
        except Exception as e:
            error = exception_to_error(layer_spec.id_, layer_spec.type_, e, line_offset=line_offset)
            return self.get_default_results(strategy_error=error)

    def _make_results(self, layer_instance, input_tensors, layer_name):
        """ Evaluate the tensors of a layer and put them in the results struct """
        try:
            _ = layer_instance(input_tensors) # Note: we use the SAMPLE tensors and NOT the actual OUTPUT tensors
            sample_tensors = layer_instance.get_sample()
            outputs = {
                key: tensor.numpy()[0] # Drop batch dimension
                for key, tensor in sample_tensors.items()
            }
            variables = layer_instance.variables.copy()            
        except Exception as e:
            logger.debug(f"Layer {layer_name} raised an error on sess.run")
            raise
        else:
            shapes = {name: np.atleast_1d(value).shape for name, value in outputs.items()}
        
            results = LayerResults(
                sample=outputs,
                out_shape=shapes,
                variables=variables,
                columns=[],
                code_error=None,
                instantiation_error=None,
                strategy_error=None,
                trained=False # TODO(anton.k): Fix when implementing checkpoint loading
            )
            return results

    def _get_input_tensors(self, layer_spec, input_results):
        """ Transforms LayerResults of input layers into tf.Tensors """
        input_tensors = {}

        for conn_spec in layer_spec.backward_connections:
            input_result = input_results[conn_spec.src_id]

            if self._is_incomplete_sample(input_result.sample, conn_spec.src_var):
                return {}, True

            y = input_result.sample[conn_spec.src_var]
            y_batch = np.array([y]) # we generally work with batches of data
            input_tensors[conn_spec.dst_var] = tf.constant(y_batch)

        return input_tensors, False            

    def _is_incomplete_sample(self, sample, source_var):
        """ Returns false if some required variable is missing """
        return sample is None or source_var not in sample    

    def _instantiate_layer(self, layer_class, layer_name):
        """ Instantiate class and log errors """
        try:
            layer_instance = layer_class()
        except Exception as e:
            logger.debug(f"Layer {layer_name} raised an error when instantiating layer class")
            raise
        else:
            return layer_instance
            
        

