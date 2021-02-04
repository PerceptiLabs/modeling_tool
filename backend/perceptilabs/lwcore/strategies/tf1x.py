import itertools
import logging

import numpy as np
import tensorflow as tf

from perceptilabs.lwcore.results import LayerResults
from perceptilabs.lwcore.strategies.base import JinjaLayerStrategy, TrainingStrategy
from perceptilabs.layers.utils import resolve_checkpoint_path
from perceptilabs.lwcore.utils import exception_to_error
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class Tf1xInnerStrategy(JinjaLayerStrategy):
    def _run_internal(self, layer_spec, graph_spec, layer_class, input_results, line_offset=None):
        with tf.Graph().as_default() as graph:
            try:
                layer_instance = layer_class()
            except Exception as e:
                error = exception_to_error(layer_spec.id_, layer_spec.type_, e, line_offset=line_offset)
                logger.debug(f"Layer {layer_spec.id_} raised an error when instantiating layer class")
                return self.get_default(strategy_error=error)                    
            input_tensors = {}

            for conn_spec in layer_spec.backward_connections:
                input_layer_result = input_results[conn_spec.src_id]

                sample = input_layer_result.sample
                if isinstance(sample, dict):
                    if sample.get('output') is None:
                        return self.get_default()
                if sample is None:
                    return self.get_default()

                if conn_spec.dst_var in input_tensors:
                    raise RuntimeError(f"Destination variable '{conn_spec.dst_var}' already set! Possible duplicate.")

                if conn_spec.src_var not in sample:
                    logger.warning(f"Source variable '{conn_spec.src_var}' missing in input results. Using default!")
                    return self.get_default()

                y = sample[conn_spec.src_var]
                y_batch = np.array([y]) # we generally work with batches of data
                input_tensors[conn_spec.dst_var] = tf.constant(y_batch)
                
            try:
                output_tensor = layer_instance(input_tensors)
            except Exception as e:
                error = exception_to_error(layer_spec.id_, layer_spec.type_, e, line_offset=line_offset)
                logger.debug(f"Layer {layer_spec.id_} raised an error in __call__" + str(e))
                return self.get_default(strategy_error=error)                    
                
            with tf.Session(config=tf.ConfigProto(device_count={'GPU': 0})) as sess:
                return self._run_tensorflow_ops(sess, layer_spec.id_, layer_spec.type_, layer_instance, output_tensor, input_tensors, layer_spec, line_offset)

    def _run_tensorflow_ops(self, sess, layer_id, layer_type, layer_instance, output_tensor, input_tensor, layer_spec, line_offset):
        sess.run(tf.global_variables_initializer())
        self._trained = False
        if tf.version.VERSION.startswith('1.15'):
            self._restore_checkpoint(layer_spec, sess)
        else:
            logger.warning(f"Checkpoint restore only works with TensorFlow 1.15. Current version is {tf.version.VERSION}")
        try:
            variables = layer_instance.variables.copy()
            sample_tensors = layer_instance.get_sample()
            outputs = {
                key: value[0] # Drop batch dimension
                for key, value in sess.run(sample_tensors).items()
            }            
        except Exception as e:
            error = exception_to_error(layer_id, layer_type, e, line_offset=line_offset)
            logger.debug(f"Layer {layer_id} raised an error on sess.run")            
            return self.get_default(strategy_error=error)


        shapes = {name: np.atleast_1d(value).shape for name, value in outputs.items()}
        
        results = LayerResults(
            sample=outputs,
            out_shape=shapes,
            variables=variables,
            columns=[],
            code_error=None,
            instantiation_error=None,
            strategy_error=None,
            trained = self._trained       
        )
        return results
        
    def _restore_checkpoint(self, spec, sess):
        spec = spec.to_dict()
        if spec['checkpoint']['load_checkpoint']:
            layer_name = spec['Type'] + '_' + spec['Name'].replace(' ', '_')
            if 'checkpoint' in spec:
                from tensorflow.python.training.tracking.base import Trackable
                export_directory = resolve_checkpoint_path(spec)
                trackable_variables = {}
                trackable_variables.update({x.name: x for x in tf.trainable_variables() if isinstance(x, Trackable)})
                trackable_variables.update({k: v for k, v in locals().items() if isinstance(v, Trackable) and
                                            not isinstance(v, tf.python.data.ops.iterator_ops.Iterator)}) # TODO: Iterators based on 'stateful functions' cannot be serialized.
                checkpoint = tf.train.Checkpoint(**trackable_variables)
                path = tf.train.latest_checkpoint(export_directory)
                # we verify for variables in checkpoints before enabling 'trained' status on each layer separately. we verify names and shapes of variables
                if path is not None:
                    checkpoint_variables = tf.train.list_variables(path)
                    for xt, xc in itertools.product(trackable_variables, checkpoint_variables):
                        if layer_name in xt and layer_name in xc[0]:
                            if trackable_variables[xt].shape == xc[1]:     # checking for variable shapes
                                self._trained = True
                                status = checkpoint.restore(path)
                                status.run_restore_ops(session=sess)
                                break
                            

class Tf1xTrainingStrategy(TrainingStrategy):
    def _create_graph_and_run(self, layer_spec, graph_spec, line_offset):
        """ Create the graph object and run it """
        with tf.Graph().as_default() as tfgraph:
            graph = self._create_graph(graph_spec)  
            if graph is not None:
                sample, shape, variables, strategy_error = self._run_training_layer(graph, layer_spec, line_offset)
            else:
                sample = shape = {'output': None}
                variables = {}                
                strategy_error = None

        return sample, shape, variables, strategy_error

    
