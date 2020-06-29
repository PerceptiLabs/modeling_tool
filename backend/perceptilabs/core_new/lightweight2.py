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

from perceptilabs.issues import UserlandError
from perceptilabs.core_new.layers.definitions import resolve_checkpoint_path, TOP_LEVEL_IMPORTS, DEFINITION_TABLE
from perceptilabs.core_new.layers import BaseLayer, DataLayer, DataReinforce, DataSupervised, DataRandom, InnerLayer, Tf1xLayer, TrainingRandom, TrainingSupervised, TrainingReinforce, TrainingLayer, ClassificationLayer, ObjectDetectionLayer, RLLayer
from perceptilabs.core_new.graph.splitter import GraphSplitter
from perceptilabs.core_new.graph.utils import get_json_net_topology
from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE
from perceptilabs.core_new.layers.script import ScriptFactory
from perceptilabs.core_new.cache2 import LightweightCache
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)



LayerResults = namedtuple('LayerResults', ['sample', 'out_shape', 'variables', 'columns', 'code_error', 'instantiation_error', 'strategy_error'])


def simplify_spec(func):
    def inner(self, graph_spec):
        if 'Layers' in graph_spec:
            graph_spec = copy.deepcopy(graph_spec['Layers'])
        return func(self, graph_spec)
    return inner


def exception_to_error(layer_id, layer_type, exception):
    tb_obj = traceback.TracebackException(
        exception.__class__,
        exception,
        exception.__traceback__
    )
    line_no = int(tb_obj.lineno) if hasattr(tb_obj, 'lineno') else None

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
    def run(self, layer_id, layer_type, layer_class, input_results, layer_spec):
        raise NotImplementedError

    @staticmethod
    def get_default(code_error=None, instantiation_error=None, strategy_error=None):
        results = LayerResults(
            sample=None,
            out_shape=None,
            variables={},
            columns=[],
            code_error=code_error,
            instantiation_error=instantiation_error,
            strategy_error=strategy_error
        )                
        return results

    
class DefaultStrategy(BaseStrategy):
    def run(self, layer_id, layer_type, layer_class, input_results, layer_spec):    
        return self.get_default()
    


class Tf1xTempStrategy(BaseStrategy):
    def __init__(self, layer_ids_to_names):
        self._layer_ids_to_names = layer_ids_to_names
    
    def run(self, layer_id, layer_type, layer_class, input_results, layer_spec):
        with tf.Graph().as_default() as graph:
            try:
                layer_instance = layer_class()                
            except Exception as e:
                error = exception_to_error(layer_id, layer_type, e)
                logger.exception(f"Layer {layer_id} raised an error when instantiating layer class")
                return self.get_default(strategy_error=error)                    
            
            input_tensors = {}
            for key, value in input_results.items():
                if value.sample is None:
                    return self.get_default()                    
                y_batch = np.array([value.sample])
                input_tensors[sanitize_layer_name(self._layer_ids_to_names[key])] = tf.constant(y_batch)

            try:
                if len(input_tensors) <= 1:
                    output_tensor = layer_instance(*input_tensors.values())
                elif len(input_tensors) > 1:
                    output_tensor = layer_instance(input_tensors)
            except Exception as e:
                error = exception_to_error(layer_id, layer_type, e)
                logger.exception(f"Layer {layer_id} raised an error in __call__")
                return self.get_default(strategy_error=error)                    
                
            with tf.Session(config=tf.ConfigProto(device_count={'GPU': 0})) as sess:
                return self._run_internal(sess, layer_id, layer_type, layer_instance, output_tensor, input_tensors)

    def _run_internal(self, sess, layer_id, layer_type, layer_instance, output_tensor, layer_spec):
        sess.run(tf.global_variables_initializer())

        if tf.version.VERSION.startswith('1.15'):
            self._restore_checkpoint(layer_spec, sess)
        else:
            logger.warning(f"Checkpoint restore only works with TensorFlow 1.15. Current version is {tf.version.VERSION}")
        try:
            variables = layer_instance.variables.copy()
            y = layer_instance.get_sample(sess=sess)
        except Exception as e:
            error = exception_to_error(layer_id, layer_type, e)
            logger.exception(f"Layer {layer_id} raised an error on sess.run")            
            return self.get_default(strategy_error=error)
        
        results = LayerResults(
            sample=y,
            out_shape=y.shape,
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

class Tf1xStrategy(BaseStrategy):
    def run(self, layer_id, layer_type, layer_class, input_results, layer_spec):
        with tf.Graph().as_default() as graph:
            try:
                layer_instance = layer_class()                
            except Exception as e:
                error = exception_to_error(layer_id, layer_type, e)
                logger.exception(f"Layer {layer_id} raised an error when instantiating layer class")
                return self.get_default(strategy_error=error)                    
            
            input_tensors = {}
            for key, value in input_results.items():
                if value.sample is None:
                    return self.get_default()                    
                y_batch = np.array([value.sample])
                input_tensors[key] = tf.constant(y_batch)

            try:
                output_tensor = layer_instance(*input_tensors.values())
            except Exception as e:
                error = exception_to_error(layer_id, layer_type, e)
                logger.exception(f"Layer {layer_id} raised an error in __call__")
                return self.get_default(strategy_error=error)                    
                
            with tf.Session(config=tf.ConfigProto(device_count={'GPU': 0})) as sess:
                return self._run_internal(sess, layer_id, layer_type, layer_instance, output_tensor, input_tensors)

    def _run_internal(self, sess, layer_id, layer_type, layer_instance, output_tensor, layer_spec):
        sess.run(tf.global_variables_initializer())

        if tf.version.VERSION.startswith('1.15'):
            self._restore_checkpoint(layer_spec, sess)
        else:
            logger.warning(f"Checkpoint restore only works with TensorFlow 1.15. Current version is {tf.version.VERSION}")
        try:
            variables = layer_instance.variables.copy()
            y = layer_instance.get_sample(sess=sess)
        except Exception as e:
            error = exception_to_error(layer_id, layer_type, e)
            logger.exception(f"Layer {layer_id} raised an error on sess.run")            
            return self.get_default(strategy_error=error)
        
        results = LayerResults(
            sample=y,
            out_shape=y.shape,
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
    def run(self, layer_id, layer_type, layer_class, input_results, layer_spec):
        layer_instance = layer_class()
        columns = layer_instance.columns

        try:
            y = layer_instance.sample
        except Exception as e:
            y = None
            shape = None
            strategy_error = exception_to_error(layer_id, layer_type, e)
            logger.exception(f"Layer {layer_id} raised an error when calling sample property")                        
        else:
            shape = np.atleast_1d(y).shape
            strategy_error=None

        variables = layer_instance.variables.copy()
        
        results = LayerResults(
            sample=y,
            out_shape=shape,
            variables=variables,
            columns=columns,
            code_error=None,
            instantiation_error=None,
            strategy_error=strategy_error
        )
        return results

class DataReinforceStrategy(BaseStrategy):
    def run(self, layer_id, layer_type, layer_class, input_results, layer_spec):
        layer_instance = layer_class()
        try:
            y = layer_instance.sample
        except Exception as e:
            y = None
            shape = None
            strategy_error = exception_to_error(layer_id, layer_type, e)
            logger.exception(f"Layer {layer_id} raised an error when calling sample property")                        
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
    
    @simplify_spec
    def run(self, graph_spec):
        layer_ids, edges_by_id = get_json_net_topology(graph_spec)

        # Split the graph (so we can handle 'incomplete' graphs, among other things)
        subgraph_topologies = GraphSplitter().split(layer_ids, edges_by_id)        

        results = {}        
        for layer_ids, edges_by_id in subgraph_topologies:
            subgraph_spec = {
                id_: spec for id_, spec in graph_spec.items() if id_ in layer_ids
            }

            # TODO: it is likely that run_subgraph should run in a new process, e.g., to avoid mixing Tf1x and Tf2x.
            _results = self._run_subgraph(subgraph_spec, layer_ids, edges_by_id)
            results.update(_results)

        return results
    
    def _run_subgraph(self, subgraph_spec, _, edges_by_id):
        ordered_ids = self._get_ordered_ids(subgraph_spec, edges_by_id)
        self._layer_ids_to_names = {id_ : subgraph_spec[id_]['Name'] for id_ in subgraph_spec}
        _, edges_by_id = get_json_net_topology(subgraph_spec)
        properties_map = {layer_id:json.dumps(subgraph_spec[layer_id]) for layer_id in subgraph_spec.keys()}
        cached_results = self._get_cached_results(properties_map, subgraph_spec, edges_by_id)
        self._cached_layer_ids = cached_results.keys()
        code_map, code_errors = self._get_code_from_layers(subgraph_spec) # Other errors are fatal and should be raised

        assert len(ordered_ids) == len(subgraph_spec) == len(code_map) == len(code_errors)
        
        all_results = {}        
        for layer_id in ordered_ids:
            if layer_id in cached_results:
                all_results[layer_id] = cached_results.get(layer_id)
            else:
                layer_results = self._compute_layer_results(
                    layer_id, subgraph_spec[layer_id], code_map[layer_id],
                    code_errors[layer_id], edges_by_id, all_results
                )                
                all_results[layer_id] = layer_results
                self._cache_computed_results(layer_id, layer_results, properties_map, edges_by_id)

        assert len(all_results) == len(subgraph_spec)
        return all_results

    def _compute_layer_results(self, layer_id, layer_spec, code, code_error, edges_by_id, all_results):
        if code is None:
            return BaseStrategy.get_default(code_error=code_error)

        layer_type = layer_spec['Type']
        layer_name = layer_spec['Name']
        layer_class, instantiation_error = self._get_layer_class(layer_id, layer_name, layer_type, code)
        if layer_class is None:
            return BaseStrategy.get_default(instantiation_error=instantiation_error)            
        
        input_results = {from_id: all_results[from_id] for (from_id, to_id) in edges_by_id if to_id == layer_id}

        strategy = self._get_layer_strategy(layer_class)
        results = strategy.run(layer_id, layer_type, layer_class, input_results, layer_spec)
        return results

    def _get_layer_strategy(self, layer_obj):
        if issubclass(layer_obj, TrainingLayer):
            strategy = DefaultStrategy()
        elif issubclass(layer_obj, DataSupervised):
            strategy = DataSupervisedStrategy()
        elif issubclass(layer_obj, DataReinforce):
            strategy = DataReinforceStrategy()
        elif issubclass(layer_obj, Tf1xLayer): 
            strategy = Tf1xTempStrategy(self._layer_ids_to_names)
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
        for layer_id in graph_spec.keys():
            cached_result = self._cache.get(layer_id, properties_map, edges_by_id)
            if cached_result is not None:
                results[layer_id] = cached_result
        return results
        
    def _get_ordered_ids(self, graph_spec, edges_by_id):
        graph = nx.DiGraph()
        graph.add_edges_from(edges_by_id)
        graph.add_nodes_from(id_ for id_ in graph_spec.keys())
        
        final_id = self._get_final_layer_id(graph_spec)
        bfs_tree = list(nx.bfs_tree(graph, final_id, reverse=True))
        ordered_ids = tuple(reversed(bfs_tree))
        return ordered_ids
    
    @simplify_spec
    def _get_final_layer_id(self, graph_spec):
        end_layers = []
        for layer_id, spec in graph_spec.items():
            if len(spec['forward_connections']) == 0:
                end_layers.append(layer_id)
        assert len(end_layers) == 1
        return end_layers[0]

    @simplify_spec
    def _get_code_from_layers(self, graph_spec):
        code_map, error_map = {}, {}        
        for layer_id, spec in graph_spec.items():
            # layer_name = spec['Name']
            if layer_id not in self._cached_layer_ids:
                code, error = self._get_layer_code(layer_id, spec)
                
                code_map[layer_id] = code
                error_map[layer_id] = error
            else:
                code_map[layer_id] = ''
                error_map[layer_id] = ''

        return code_map, error_map


    def _get_layer_code(self, layer_id, layer_spec):
        code = ''
        sf = ScriptFactory()

        # TODO: retrieve imports from script factory
        top_level_imports = TOP_LEVEL_IMPORTS['standard_library'] + \
                            TOP_LEVEL_IMPORTS['third_party'] + \
                            TOP_LEVEL_IMPORTS['perceptilabs']

        for stmt in top_level_imports:
            code += stmt + '\n'

        layer_def = DEFINITION_TABLE.get(layer_spec['Type'])
        for stmt in layer_def.import_statements:
            code += stmt + '\n'
            
        code += '\n'

        layer_name_id = sanitize_layer_name(layer_spec['Name'])
        try:
            if layer_spec['Code'] is None or layer_spec['Code'] == '' or layer_spec['Code'].get('Output') is None:
                code += sf.render_layer_code(layer_name_id, layer_spec['Type'], layer_spec)
            else:
                code += layer_spec['Code'].get('Output')
            ast.parse(code)
        except SyntaxError as e:
            logger.exception(f"Layer {layer_id} raised an error when getting layer code") 
            return None, exception_to_error(layer_id, layer_spec['Type'], e)                                
        except Exception as e:
            logger.warning(f"{str(e)}: couldn't get code for {layer_id}. Treating it as not fully specified")
            if logger.isEnabledFor(logging.DEBUG):
                from perceptilabs.utils import stringify
                logger.warning("layer spec: \n" + stringify(layer_spec))
                
            return None, None
        else:
            return code, None

    def _get_layer_class(self, layer_id, layer_name, layer_type, code):

        is_unix = os.name != 'nt' # Windows has permission issues when deleting tempfiles
        with NamedTemporaryFile('wt', delete=is_unix, suffix='.py') as f:
            f.write(code)
            f.flush()

            spec = importlib.util.spec_from_file_location("my_module", f.name)        
            module = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(module)
            except Exception as e:
                error = exception_to_error(layer_id, layer_type, e)
                logger.exception(f"Layer {layer_id} raised an error when executing module")                                        
                return None, error

            class_name = layer_type + sanitize_layer_name(layer_name)
            class_object = getattr(module, class_name)
        
        if not is_unix:
            os.remove(f.name)

        return class_object, None
        

class LightweightCoreAdapter:
    """ Compatibility with v1 core """
    def __init__(self, graph_dict, layer_extras_reader, error_handler, issue_handler, cache, data_container):
        self._graph_dict = graph_dict
        self._error_handler = error_handler
        self._extras_reader = layer_extras_reader
        self._error_handler = error_handler
        self._data_container = data_container
        
        self._core = LightweightCore(
            issue_handler=issue_handler,
            cache=cache
        )

    def run(self):
        graph_spec = copy.deepcopy(self._graph_dict)
        results = self._core.run(graph_spec)

        extras_dict = {}
        self._errors_dict = {}                    
        for layer_id, layer_info in results.items():
            var_names = ['(sample)']            
            self._data_container.store_value(layer_id, '(sample)', layer_info.sample)
            for name, value in layer_info.variables.items():
                var_names.append(name)
                self._data_container.store_value(layer_id, name, value)
                
            default_var = '(sample)'
            entry = {
                'Sample': layer_info.sample.tolist() if layer_info.sample is not None else None,
                'outShape': [] if layer_info.out_shape is None else list(layer_info.out_shape),
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



    

    
        
            




















