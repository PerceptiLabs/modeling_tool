3# TODO: (1) create flask server for running in remote process. (2) dynamic imports (3) more descriptive errors.

import traceback
import logging
import copy
import json
import time
import networkx as nx
import requests
import importlib
import threading
from flask import Flask, request, jsonify
from collections import namedtuple
import tensorflow as tf
from tensorflow.python.training.tracking.base import Trackable
        
from perceptilabs.issues import UserlandError
from perceptilabs.core_new.layers.definitions import resolve_checkpoint_path
from perceptilabs.core_new.layers import BaseLayer, DataLayer, InnerLayer, Tf1xLayer, TrainingLayer, ClassificationLayer
from perceptilabs.core_new.graph.splitter import GraphSplitter
from perceptilabs.core_new.graph.utils import get_json_net_topology
from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE
from perceptilabs.core_new.layers.script import ScriptFactory
from perceptilabs.core_new.cache2 import LightweightCache


log = logging.getLogger(__name__)

LayerInfo = namedtuple('LayerInfo', ['sample', 'out_shape', 'in_shape', 'variables', 'default_var'])


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
    include_remainder = False
    for counter, line in enumerate(tb_obj.format()):
        if '<string>' in line:
            include_remainder = True
        if counter == 0 or include_remainder:
            message += line
            
    error = UserlandError(layer_id, layer_type, line_no, message)
    return error


class Tf1xStrategy:
    def run(self, graph_spec, ordered_ids, layer_instances, layer_infos):
        output_tensors, errors1 = self._get_output_tensors(graph_spec, ordered_ids, layer_instances, layer_infos)
        results, errors2 = self._create_results(graph_spec, output_tensors, ordered_ids, layer_instances, layer_infos)        
        return results, {**errors1, **errors2}

    def _create_results(self, graph_spec, output_tensors, ordered_ids, layer_instances, layer_infos):
        sess = tf.Session()

        sess.run(tf.global_variables_initializer())
        self._restore_checkpoint(graph_spec, sess)
        outputs = sess.run(output_tensors)

        errors = {}        
        results = {}
        for layer_id in ordered_ids:
            # Find the default variable (the one that matches output tensor...)
            default_var = None

            if layer_id in layer_infos:
                results[layer_id] = layer_infos[layer_id]
            else:
            
                var_names = list(layer_instances[layer_id].variables.keys() if layer_instances[layer_id] is not None else [])
                for var_name in var_names:
                    if layer_instances[layer_id].variables[var_name] is output_tensors[layer_id]:
                        default_var = var_name
                        break                

                output = outputs.get(layer_id, None)
                results[layer_id] = LayerInfo(
                    sample=output,
                    out_shape=np.atleast_2d(output).shape[1:] if output is not None else None,
                    in_shape=None,
                    variables=var_names,
                    default_var=default_var
                )
        return results, errors

    def _restore_checkpoint(self, graph_spec, sess):
        export_directory = None
        for spec in graph_spec.values():
            export_directory = resolve_checkpoint_path(spec)                    
            
        if export_directory is not None:
            trackable_variables = {}
            trackable_variables.update({x.name: x for x in tf.trainable_variables() if isinstance(x, Trackable)})
            trackable_variables.update({k: v for k, v in locals().items() if isinstance(v, Trackable) and not isinstance(v, tf.python.data.ops.iterator_ops.Iterator)}) # TODO: Iterators based on 'stateful functions' cannot be serialized.
            checkpoint = tf.train.Checkpoint(**trackable_variables)

            path = tf.train.latest_checkpoint(export_directory)
            status = checkpoint.restore(path)
            status.assert_consumed().run_restore_ops(session=sess)

    def _add_output_tensors_from_instance(self, layer_id, layer_spec, layer, output_tensors, errors):
        layer_type = layer_spec[layer_id]
        if isinstance(layer, TrainingLayer):
            pass
        elif isinstance(layer, DataLayer):
            try:
                y = tf.constant(layer.sample)            
                output_tensors[layer_id] = y
            except Exception as e:
                errors[layer_id] = exception_to_error(layer_id, layer_type, e)                    
        elif isinstance(layer, InnerLayer):
            bw_cons = [input_id for input_id, _ in layer_spec['backward_connections']]
            
            args = {}
            for input_id in bw_cons:
                if input_id in output_tensors:
                    args[input_id] = output_tensors[input_id]

            if len(args) == len(bw_cons):
                try:
                    y = layer(*args.values())
                    output_tensors[layer_id] = y
                except Exception as e:
                    # 'userland runtime errors'
                    errors[layer_id] = exception_to_error(layer_id, layer_type, e)
            else:
                log.debug(f'Layer {layer_id} expected inputs from layers {bw_cons}, got {list(args.keys())}. Skipping.')
        else:
            errors[layer_id] = 'unknown type ' + str(type(layer))

    
    def _get_output_tensors(self, graph_spec, ordered_ids, layer_instances, layer_infos):
        errors = {}
        output_tensors = {}
        for layer_id in ordered_ids:
            if layer_id in layer_infos:
                if layer_infos[layer_id].sample is None:
                    continue
                y = tf.constant(layer_infos[layer_id].sample)            
                output_tensors[layer_id] = y
            elif layer_id in layer_instances:
                if layer_instances[layer_id] is None:
                    continue                
                self._add_output_tensors_from_instance(
                    layer_id,
                    graph_spec[layer_id],
                    layer_instances[layer_id],
                    output_tensors,
                    errors
                )
        return output_tensors, errors
    
    
class LightweightCore:
    def __init__(self, issue_handler=None, cache=None):
        self._issue_handler = issue_handler
        self._cache = cache

    @simplify_spec
    def run(self, graph_spec):
        layer_ids, edges_by_id = get_json_net_topology(graph_spec)

        # Split the graph (among other things, so we can handle 'incomplete' graphs)
        subgraph_topologies = GraphSplitter().split(layer_ids, edges_by_id)        

        results = {}
        instance_errors = {}
        strategy_errors = {}
        
        for layer_ids, edges_by_id in subgraph_topologies:
            subgraph_spec = {
                id_: spec for id_, spec in graph_spec.items() if id_ in layer_ids
            }

            # TODO: it is likely that run_subgraph should run in a new process, e.g., to avoid mixing Tf1x and Tf2x.
            _results, _instance_errors, _strategy_errors = self._run_subgraph(subgraph_spec, layer_ids, edges_by_id)
            results.update(_results)
            instance_errors.update(_instance_errors)
            strategy_errors.update(_strategy_errors)            
            
        return results, instance_errors, strategy_errors

    def _run_subgraph(self, subgraph_spec, layer_ids, edges_by_id):
        graph = nx.DiGraph()
        graph.add_edges_from(edges_by_id)
        graph.add_nodes_from(layer_ids)
        
        final_id = self._get_final_layer_id(subgraph_spec)
        bfs_tree = list(nx.bfs_tree(graph, final_id, reverse=True))
        ordered_ids = tuple(reversed(bfs_tree))

        code_map, code_errors = self._get_code_from_layers(subgraph_spec)
        _, edges_by_id = get_json_net_topology(subgraph_spec)
        layer_instances, layer_infos, instance_errors = self._get_layer_instances_and_info(code_map, subgraph_spec, edges_by_id)
                
        strategy = self._get_subgraph_strategy(subgraph_spec)
        results, strategy_errors = strategy.run(subgraph_spec, ordered_ids, layer_instances, layer_infos)

        if self._cache is not None:
            for layer_id, layer_info in results.items():
                self._cache.put(layer_id, layer_info, code_map, edges_by_id)
        
        return results, instance_errors, strategy_errors

    @simplify_spec
    def _get_final_layer_id(self, graph_spec):
        end_layers = []
        for layer_id, spec in graph_spec.items():
            if len(spec['forward_connections']) == 0:
                end_layers.append(layer_id)
        assert len(end_layers) == 1
        return end_layers[0]

    def _get_subgraph_strategy(self, subgraph_spec):
        return Tf1xStrategy() # That's all for now...

    @simplify_spec
    def _get_code_from_layers(self, graph_spec):
        code_map, error_map = {}, {}        
        for layer_id, spec in graph_spec.items():
            code, error = self._get_layer_code(layer_id, spec)
            
            code_map[layer_id] = code or ''
            if error is not None:
                error_map[layer_id] = error

        return code_map, error_map

    def _get_layer_instances_and_info(self, code_map, graph_spec, edges_by_id):
        instances, infos, errors = {}, {}, {}
        for layer_id, code in code_map.items():
            layer_type = graph_spec[layer_id]['Type']
            
            if code is None:
                instances[layer_id] = None
                log.debug(f"Code for layer {layer_id} [{layer_type}] was none. Skipping.")                            
                continue

            if self._cache is not None:
                layer_info = self._cache.get(layer_id, code_map, edges_by_id)
                if layer_info is not None:
                    infos[layer_id] = layer_info
                    log.debug(f"Using cached values for layer {layer_id} [{graph_spec[layer_id]['Type']}].")
                    continue
                
            log.debug(f"Instantiating layer {layer_id} [{layer_type}]")
            instance, error = self._get_layer_instance(layer_id, layer_type, code)
            instances[layer_id] = instance

            if instance is None:
                log.debug(f"Couldn't instantiate {layer_id} [{layer_type}]")                        
            
            if error is not None:
                errors[layer_id] = error
                log.debug(f"Got userland error when trying to instantiate {layer_id} [{layer_type}]: {repr(error)}")                        

            
        return instances, infos, errors

    def _get_layer_code(self, layer_id, layer_spec):
        # TODO: this should simply check that all the parameters are present in the spec. Until we have a stronger spec, try to render it and if it doesn't work return false
        sf = ScriptFactory()                 
        try:
            if layer_spec['Code'] is None or layer_spec['Code'] == '' or layer_spec['Code'].get('Output') is None:
                code = sf.render_layer_code(layer_id, layer_spec['Type'], layer_spec)
            else:
                code = layer_spec['Code'].get('Output')
        except Exception as e:
            return None, e
        else:
            return code, None    

        
    def _get_layer_instance(self, layer_id, layer_type, code):
        import tensorflow as tf
        import numpy as np
        import dill
        import os        
        import pickle        
        import zmq        
        import sys
        import json
        import time        
        import zlib
        from queue import Queue                
        import logging
        import threading
        from typing import Dict, Any, List, Tuple, Generator        
        from flask import Flask, jsonify#, request
        from tensorflow.python.training.tracking.base import Trackable
        import flask

        from perceptilabs.core_new.utils import Picklable
        #from perceptilabs.core_new.communication.status import *        

        from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE        
        from perceptilabs.core_new.graph import Graph
        from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder                
        from perceptilabs.core_new.api.mapping import MapServer, ByteMap
        from perceptilabs.core_new.serialization import can_serialize, serialize
        
        globs = globals()
        globs.update(locals())
        locs = {}

        try:
            exec(code, globs, locs) # TODO: catch errors here!
        except SyntaxError as e:
            error = exception_to_error(layer_id, layer_type, e)
            return None, error
        except Exception as e:
            error = exception_to_error(layer_id, layer_type, e)            
            return None, error

        if len(locs.values()) == 0:
            return None, None
        
        layer_class = list(locs.values())[0]
        
        try:
            instance = layer_class()
        except Exception as e:
            # "userland runtime errors"
            error = exception_to_error(layer_id, layer_type, e)                        
            return None, error
        
        return instance, None


class LightweightCoreAdapter:
    """ Compability with v1 core """
    def __init__(self, graph_dict, layer_extras_reader, error_handler, issue_handler, cache):
        self._graph_dict = graph_dict
        self._error_handler = error_handler
        self._extras_reader = layer_extras_reader
        self._error_handler = error_handler
        
        self._core = LightweightCore(
            issue_handler=issue_handler,
            cache=cache
        )

    def run(self):
        graph_spec = copy.deepcopy(self._graph_dict)
        results, instance_errors, strategy_errors = self._core.run(graph_spec)

        extras_dict = {}
        for layer_id, layer_info in results.items():
            entry = {
                'Sample': layer_info.sample,
                'outShape': [] if layer_info.out_shape is None else list(layer_info.out_shape),
                'inShape': [] if layer_info.in_shape is None else list(layer_info.in_shape),
                'Variables': layer_info.variables,
                'Default_var': layer_info.default_var
            }
            extras_dict[layer_id] = entry
            self._extras_reader.set_dict(extras_dict)

        self._errors_dict = {}            
        for layer_id, error in strategy_errors.items():
            print(layer_id, graph_spec[layer_id]['Type'], error)                        
            self._errors_dict[layer_id] = error
        
        for layer_id, error in instance_errors.items():
            print(error)            
            self._errors_dict[layer_id] = error            

    @property
    def error_handler(self):

        class CompabilityErrorHandler:
            def __init__(self, errors_dict):
                self._dict = errors_dict
                
            def to_dict(self):
                return copy.copy(self._dict)
            
            def __contains__(self, id_):
                return id_ in self._dict
            
            def __getitem__(self, id_):
                return self._dict[id_]
        
        error_handler = CompabilityErrorHandler(self._errors_dict)        
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

    t1 = time.time()
    
    y = lw.run(dd)    

    t2 = time.time()


    print('2nd, 1st',t2-t1, t1-t0)
    
    import pdb; pdb.set_trace()
        
            




















