# TODO: (1) create flask server for running in remote process. (2) dynamic imports (3) more descriptive errors.

import os
import ast
from abc import abstractmethod, ABC
import traceback
import logging
import copy
import json
import time
import networkx as nx
import requests
import importlib
import threading
from collections import namedtuple
import tensorflow as tf
import numpy as np
from tempfile import NamedTemporaryFile


from perceptilabs.layers.utils import resolve_checkpoint_path
from perceptilabs.utils import stringify, add_line_numbering
from perceptilabs.issues import UserlandError
from perceptilabs.core_new.layers import BaseLayer, DataLayer, DataReinforce, DataSupervised, DataRandom, InnerLayer, Tf1xLayer, TrainingRandom, TrainingSupervised, TrainingReinforce, TrainingLayer, ClassificationLayer, ObjectDetectionLayer, RLLayer
from perceptilabs.graph.splitter import GraphSplitter
from perceptilabs.core_new.graph.utils import get_json_net_topology
from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE
from perceptilabs.script import ScriptFactory
from perceptilabs.core_new.cache2 import LightweightCache
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.logconf import APPLICATION_LOGGER



logger = logging.getLogger(APPLICATION_LOGGER)



LayerResults = namedtuple('LayerResults', ['sample', 'out_shape', 'variables', 'columns', 'code_error', 'instantiation_error', 'strategy_error'])


def exception_to_error(layer_id, layer_type, exception, line_offset=None):
    tb_obj = traceback.TracebackException(
        exception.__class__,
        exception,
        exception.__traceback__
    )

    line_no = None
    if hasattr(tb_obj, 'lineno'):
        line_no = int(tb_obj.lineno)

        if line_offset is not None:
            line_no -= line_offset
    
    message = ''
    #include_following = False
    for counter, line in enumerate(tb_obj.format()):
        #if '_call_with_frames_removed' in line:
        #    include_following = True
        #    continue
        #if counter == 0 or include_following:
        message += line

    error = UserlandError(layer_id, layer_type, line_no, message)
    return error


class BaseStrategy(ABC):
    @abstractmethod
    def run(self, layer_spec, layer_class, input_results):
        raise NotImplementedError

    @staticmethod
    def get_default(code_error=None, instantiation_error=None, strategy_error=None):
        results = LayerResults(
            sample={},
            out_shape={},
            variables={},
            columns=[],
            code_error=code_error,
            instantiation_error=instantiation_error,
            strategy_error=strategy_error
        )                
        return results

    
class DefaultStrategy(BaseStrategy):
    def run(self, layer_spec, layer_class, input_results):    
        return self.get_default()
    

class Tf1xStrategy(BaseStrategy):
    def __init__(self, layer_ids_to_names):
        self._layer_ids_to_names = layer_ids_to_names
    
    def run(self, layer_spec, layer_class, input_results):
        with tf.Graph().as_default() as graph:
            try:
                layer_instance = layer_class()
            except Exception as e:
                error = exception_to_error(layer_spec.id_, layer_spec.type_, e)
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
                error = exception_to_error(layer_spec.id_, layer_spec.type_, e)
                logger.debug(f"Layer {layer_spec.id_} raised an error in __call__" + str(e))
                return self.get_default(strategy_error=error)                    
                
            with tf.Session(config=tf.ConfigProto(device_count={'GPU': 0})) as sess:
                return self._run_internal(sess, layer_spec.id_, layer_spec.type_, layer_instance, output_tensor, input_tensors)

    def _run_internal(self, sess, layer_id, layer_type, layer_instance, output_tensor, layer_spec):
        sess.run(tf.global_variables_initializer())

        if tf.version.VERSION.startswith('1.15'):
            self._restore_checkpoint(layer_spec, sess)
        else:
            logger.warning(f"Checkpoint restore only works with TensorFlow 1.15. Current version is {tf.version.VERSION}")
        try:
            variables = layer_instance.variables.copy()
            outputs = layer_instance.get_sample(sess=sess)
        except Exception as e:
            error = exception_to_error(layer_id, layer_type, e)
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
            strategy_error=None            
        )
        return results
        
    def _restore_checkpoint(self, spec, sess):
        if 'checkpoint' in spec:
            from tensorflow.python.training.tracking.base import Trackable

            export_directory = resolve_checkpoint_path(spec)
            
            trackable_variables = {}
            trackable_variables.update({x.name: x for x in tf.trainable_variables() if isinstance(x, Trackable)})
            trackable_variables.update({k: v for k, v in locals().items() if isinstance(v, Trackable) and
                                        not isinstance(v, tf.python.data.ops.iterator_ops.Iterator)}) # TODO: Iterators based on 'stateful functions' cannot be serialized.
            
            checkpoint = tf.train.Checkpoint(**trackable_variables)

            path = tf.train.latest_checkpoint(export_directory)
            status = checkpoint.restore(path)
            status.run_restore_ops(session=sess)

            
class DataSupervisedStrategy(BaseStrategy):
    def run(self, layer_spec, layer_class, input_results):
        try:
            layer_instance = layer_class()
            columns = layer_instance.columns        
            output = layer_instance.sample
            variables = layer_instance.variables.copy()
        except Exception as e:
            output = {'output': None}
            shape = {'output': None}
            variables = {}
            columns = []
            strategy_error = exception_to_error(layer_spec.id_, layer_spec.type_, e)
            logger.debug(f"Layer {layer_spec.id_} raised an error when calling sample property")                        
        else:
            shape = {name: np.atleast_1d(value).shape for name, value in output.items()}
            strategy_error = None

        results = LayerResults(
            sample=output,
            out_shape=shape,
            variables=variables,
            columns=columns,
            code_error=None,
            instantiation_error=None,
            strategy_error=strategy_error
        )
        return results

    
class DataReinforceStrategy(BaseStrategy):
    def run(self, layer_spec, layer_class, input_results):
        layer_instance = layer_class()
        try:
            y = layer_instance.sample
        except Exception as e:
            y = None
            shape = None
            strategy_error = exception_to_error(layer_spec.id_, layer_spec.type_, e)
            logger.debug(f"Layer {layer_spec.id_} raised an error when calling sample property")                        
        else:
            shape = np.atleast_1d(y).shape
            strategy_error=None

        variables = layer_instance.variables.copy()
        
        results = LayerResults(
            sample=y,
            out_shape=shape,
            variables=variables,
            columns = [],
            code_error=None,
            instantiation_error=None,
            strategy_error=strategy_error
        )
        return results

    
class LightweightCore:
    def __init__(self, issue_handler=None, cache=None):
        self._issue_handler = issue_handler
        self._cache = cache
        self._script_factory = ScriptFactory()
    
    def run(self, graph_spec):
        subgraph_specs = graph_spec.split(GraphSplitter())        
        results = {}        
        for subgraph_spec in subgraph_specs:
            # TODO: it is likely that run_subgraph should run in a new process, e.g., to avoid mixing Tf1x and Tf2x.
            _results = self._run_subgraph(subgraph_spec)
            results.update(_results)

        return results
    
    def _run_subgraph(self, subgraph_spec):
        ordered_ids = subgraph_spec.get_ordered_ids()
        
        self._layer_ids_to_names = {node.id_ : node.name for node in subgraph_spec.nodes}
        
        edges_by_id = subgraph_spec.edges_by_id
        subgraph_spec_dict = subgraph_spec.to_dict()
        properties_map = {layer_id: json.dumps(subgraph_spec_dict[layer_id]) for layer_id in subgraph_spec_dict.keys()}
        cached_results = self._get_cached_results(properties_map, subgraph_spec, edges_by_id)
        self._cached_layer_ids = cached_results.keys()
        code_map, code_errors = self._get_code_from_layers(subgraph_spec) # Other errors are fatal and should be raised

        assert len(ordered_ids) == len(subgraph_spec) == len(code_map) == len(code_errors)
        
        all_results = {}        
        for layer_id in ordered_ids:
            layer_spec = subgraph_spec[layer_id]
            logger.info(f"Getting results for layer {layer_spec}")
            
            if layer_id in cached_results:
                all_results[layer_id] = cached_results.get(layer_id)
            else:
                layer_results = self._compute_layer_results(
                    layer_id, subgraph_spec, layer_spec, code_map[layer_id],
                    code_errors[layer_id], edges_by_id, all_results
                )                
                all_results[layer_id] = layer_results
                self._cache_computed_results(layer_id, layer_results, properties_map, edges_by_id)

        assert len(all_results) == len(subgraph_spec)
        return all_results

    def _compute_layer_results(self, layer_id, graph_spec, layer_spec, code, code_error, edges_by_id, all_results):
        if code is None:
            return BaseStrategy.get_default(code_error=code_error)

        layer_helper = LayerHelper(self._script_factory, layer_spec, graph_spec)
        try:
            layer_class = layer_helper.get_class()
        except Exception as e:
            layer_class = None                                                
            instantiation_error = exception_to_error(layer_spec.id_, layer_spec.type_, e)
            logger.debug(f"Layer {layer_spec.id_} raised an error when executing module " + repr(e))
        else:
            instantiation_error = None

        if layer_class is None:
            return BaseStrategy.get_default(instantiation_error=instantiation_error)            
        
        input_results = {
            from_id: all_results[from_id]
            for (from_id, to_id) in edges_by_id if to_id == layer_spec.id_
        }
        strategy = self._get_layer_strategy(layer_class)
        try:
            results = strategy.run(layer_spec, layer_class, input_results)
        except:
            logger.exception(f"Failed running strategy '{strategy.__class__.__name__}' on layer {layer_spec.id_}")
            raise
        return results

    def _get_layer_strategy(self, layer_obj):
        if issubclass(layer_obj, TrainingLayer):
            strategy = DefaultStrategy()
        elif issubclass(layer_obj, DataSupervised):
            strategy = DataSupervisedStrategy()
        elif issubclass(layer_obj, DataReinforce):
            strategy = DataReinforceStrategy()
        elif issubclass(layer_obj, Tf1xLayer): 
            strategy = Tf1xStrategy(self._layer_ids_to_names)
        else:
            strategy = DefaultStrategy()
        return strategy

    def _cache_computed_results(self, layer_id, layer_results, code_map, edges_by_id):
        if self._cache is not None:
            self._cache.put(layer_id, layer_results, code_map, edges_by_id)

    def _get_cached_results(self, properties_map, graph_spec, edges_by_id):
        if self._cache is None:
            return {}

        results = {}
        for layer_id in graph_spec.layer_ids:
            cached_result = self._cache.get(layer_id, properties_map, edges_by_id)
            if cached_result is not None:
                results[layer_id] = cached_result
        return results
        
    def _get_code_from_layers(self, graph_spec):
        code_map, error_map = {}, {}        
        for layer_id, layer_spec in graph_spec.nodes_by_id.items():
            if layer_id not in self._cached_layer_ids:
                code, error = self._get_layer_code(layer_id, layer_spec, graph_spec)

                code_map[layer_id] = code
                error_map[layer_id] = error
            else:
                code_map[layer_id] = ''
                error_map[layer_id] = ''

        return code_map, error_map

    def _get_layer_code(self, layer_id, layer_spec, graph_spec):
        layer_helper = LayerHelper(self._script_factory, layer_spec, graph_spec)
        try:
            code = layer_helper.get_code(check_syntax=True)
        except SyntaxError as e:
            logger.exception(f"Layer {layer_spec.id_} raised an error when getting layer code") 
            return None, exception_to_error(layer_spec.id_, layer_spec.type_, e)
        except Exception as e:
            logger.warning(f"{type(e).__name__}: {str(e)} | couldn't get code for {layer_spec.id_}. Treating it as not fully specified")
            if logger.isEnabledFor(logging.DEBUG):
                logger.warning("layer spec: \n" + stringify(layer_spec.to_dict()))
            return None, None
        else:
            return code, None

    def _get_layer_class(self, layer_spec, code):        
        is_unix = os.name != 'nt' # Windows has permission issues when deleting tempfiles
        with NamedTemporaryFile('wt', delete=is_unix, suffix='.py') as f:
            f.write(code)
            f.flush()

            spec = importlib.util.spec_from_file_location("my_module", f.name)        
            module = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(module)
            except Exception as e:
                error = exception_to_error(layer_spec.id_, layer_spec.type_, e)
                logger.debug(f"Layer {layer_spec.id_} raised an error when executing module")                                        
                return None, error

            class_name = layer_spec.sanitized_name

            class_object = getattr(module, class_name)
        
        if not is_unix:
            os.remove(f.name)

        return class_object, None
        

class LightweightCoreAdapter:
    """ Compatibility with v1 core """
    def __init__(self, graph_spec, layer_extras_reader, error_handler, issue_handler, cache, data_dict):
        self._graph_spec = graph_spec
        self._error_handler = error_handler
        self._extras_reader = layer_extras_reader
        self._error_handler = error_handler
        self._data_dict = data_dict
        
        self._core = LightweightCore(
            issue_handler=issue_handler,
            cache=cache
        )

    def run(self):
        results = self._core.run(self._graph_spec)
        
        extras_dict = {}
        self._errors_dict = {}                    
        for layer_id, layer_info in results.items():
            self._data_dict[layer_id] = {}

            var_names = []
            for name, value in layer_info.sample.items():
                var_names.append(name)
                self._data_dict[layer_id][name] = value
                
            default_var = 'output'

            first_sample = next(iter(layer_info.sample.values()), None)
            first_shape = np.atleast_1d(first_sample).shape if first_sample is not None else ()
            
            entry = {
                'Sample': first_sample.tolist() if first_sample is not None else None,
                'outShape': list(first_shape) if first_shape is not None else [],
                'inShape': [],
                'action_space': layer_info.variables.get('action_space',''),
                'Variables': var_names,
                'Default_var': default_var,
                'cols': layer_info.columns
            }
            extras_dict[layer_id] = entry

            if layer_info.strategy_error is not None:
                self._errors_dict[layer_id] = layer_info.strategy_error
                
            if layer_info.instantiation_error is not None:
                self._errors_dict[layer_id] = layer_info.instantiation_error
                
            if layer_info.code_error is not None:
                self._errors_dict[layer_id] = layer_info.code_error

        self._extras_reader.set_dict(extras_dict)

    @property
    def error_handler(self):

        class CompatibilityErrorHandler:
            def __init__(self, errors_dict):
                self._dict = errors_dict
                
            def to_dict(self):
                return copy.copy(self._dict)
            
            def __contains__(self, id_):
                return id_ in self._dict
            
            def __getitem__(self, id_):
                return self._dict[id_]
        
        error_handler = CompatibilityErrorHandler(self._errors_dict)        
        return error_handler
            

if __name__ == "__main__":
    import json


    with open('net.json_', 'r') as f:
        dd = json.load(f)

    from perceptilabs.core_new.extras import LayerExtrasReader

    lw = LightweightCore()

    import time
    t0 = time.time()
    
    x = lw.run(dd)

    print('columns', x['1564399775664'].columns)


    import pdb; pdb.set_trace()
    
    #t1 = time.time()
    
    #y = lw.run(dd)    

    #t2 = time.time()



    
    #print('2nd, 1st',t2-t1, t1-t0)
    
        
            




















