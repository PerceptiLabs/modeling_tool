import logging
import hashlib

import numpy as np
import tensorflow as tf
from tensorflow.python.training.tracking.data_structures import ListWrapper
from perceptilabs.lwcore.results import LayerResults
from perceptilabs.lwcore.strategies.base import JinjaLayerStrategy
from perceptilabs.lwcore.utils import exception_to_error


logger = logging.getLogger(__name__)


class Tf2xInnerStrategy(JinjaLayerStrategy):
    def _run_internal(
        self,
        layer_spec,
        graph_spec,
        layer_class,
        input_results,
        random_number_generator,
        line_offset=None,
    ):
        """Returns a LayerResults obj. containing shapes and previews for a layer

        Args:
            layer_spec: describes the layer configuration
            graph_spec: graph spec
            layer_class: corresponds to layer spec
            input_results: a dict with LayerResults from other layers in the same graph
            line_offset: used to map line numbers of the executed code to the line numbers visible to the user.
        Returns:
            an instance of LayerResults
        """
        try:
            layer_instance = self._instantiate_layer(
                layer_class, layer_spec.name, random_number_generator
            )
            input_tensors, has_missing_inputs = self._get_input_tensors(
                layer_spec, input_results
            )

            if has_missing_inputs:
                return self.get_default_results()

            results = self._make_results(layer_instance, input_tensors, layer_spec.name)
            return results
        except Exception as e:
            error = exception_to_error(
                layer_spec.id_, layer_spec.type_, e, line_offset=line_offset
            )
            return self.get_default_results(strategy_error=error)

    def _make_results(self, layer_instance, input_tensors, layer_name):
        """Evaluate the tensors of a layer and put them in the results struct"""

        try:
            _ = layer_instance(
                input_tensors
            )  # Note: we use the SAMPLE tensors and NOT the actual OUTPUT tensors
            sample_tensors = layer_instance.get_sample()
            self._print_weights_hash_if_exist(layer_name, layer_instance)

            outputs = {
                key: tensor.numpy()[0]  # Drop batch dimension
                for key, tensor in sample_tensors.items()
            }
            variables = layer_instance.variables.copy()
        except Exception as e:
            logger.debug(f"Layer {layer_name} raised an error on sess.run")
            raise
        else:
            shapes = {
                name: np.atleast_1d(value).shape for name, value in outputs.items()
            }

            results = LayerResults(
                sample=outputs,
                out_shape=shapes,
                variables=variables,
                columns=[],
                code_error=None,
                instantiation_error=None,
                strategy_error=None,
                trained=False,  # TODO(anton.k): Fix when implementing checkpoint loading
            )
            return results

    def _print_weights_hash_if_exist(self, layer_name, layer_instance):
        hasher = hashlib.md5()
        if layer_instance.trainable_variables:
            for key, value in layer_instance.trainable_variables.items():
                hasher.update(key.encode())
                if isinstance(value, ListWrapper):
                    value = value[-1]
                hasher.update(value.numpy().tobytes())

            logger.info(f"Weights hash for {layer_name}: {hasher.hexdigest()}")

    def _get_input_tensors(self, layer_spec, input_results):
        """Transforms LayerResults of input layers into tf.Tensors"""
        input_tensors = {}

        for conn_spec in layer_spec.backward_connections:
            input_result = input_results[conn_spec.src_id]

            if self._is_incomplete_sample(input_result.sample, conn_spec.src_var):
                return {}, True

            y = input_result.sample[conn_spec.src_var]
            y_batch = np.array([y])  # we generally work with batches of data
            input_tensors[conn_spec.dst_var] = tf.constant(y_batch)

        return input_tensors, False

    def _is_incomplete_sample(self, sample, source_var):
        """Returns false if some required variable is missing"""
        return sample is None or source_var not in sample

    def _instantiate_layer(self, layer_class, layer_name, random_number_generator):
        """Instantiate class and log errors"""
        if random_number_generator:
            seed = random_number_generator.uniform(
                shape=(), minval=None, maxval=None, dtype=tf.int32
            ).numpy()
            tf.random.set_seed(seed)
            logger.info(
                f"TensorFlow random seed set to {seed} before instantiating layer {layer_name}"
            )
        else:
            logger.info(
                f"TensorFlow random seed not set before instantiating layer {layer_name}"
            )

        try:
            layer_instance = layer_class()
        except Exception as e:
            logger.debug(
                f"Layer {layer_name} raised an error when instantiating layer class"
            )
            raise
        else:
            return layer_instance
