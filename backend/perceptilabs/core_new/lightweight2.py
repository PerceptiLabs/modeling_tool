# TODO: (1) create flask server for running in remote process. (2) dynamic imports (3) more descriptive errors.

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


from perceptilabs.issues import UserlandError
from perceptilabs.core_new.layers.definitions import resolve_checkpoint_path
from perceptilabs.core_new.layers import BaseLayer, DataLayer, InnerLayer, Tf1xLayer, TrainingLayer, ClassificationLayer
from perceptilabs.core_new.graph.splitter import GraphSplitter
from perceptilabs.core_new.graph.utils import get_json_net_topology
from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE
from perceptilabs.core_new.layers.script import ScriptFactory


log = logging.getLogger(__name__)

LayerInfo = namedtuple('LayerInfo', ['sample', 'out_shape', 'in_shape', 'variables', 'default_var'])


def simplify_spec(func):
    def inner(self, graph_spec):
        if 'Layers' in graph_spec:
            graph_spec = copy.deepcopy(graph_spec['Layers'])
        return func(self, graph_spec)
    return inner

def exception_to_error(exception):
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
            
    error = UserlandError(layer_id, layer_spec['Type'], line_no, message)
    return error
    


class Tf1xStrategy:
    def run(self, graph_spec, ordered_ids, layer_instances):
        output_tensors, errors1 = self._get_output_tensors(graph_spec, ordered_ids, layer_instances)
        results, errors2 = self._create_results(graph_spec, output_tensors, ordered_ids, layer_instances)        
        return results, {**errors1, **errors2}

    def _create_results(self, graph_spec, output_tensors, ordered_ids, layer_instances):
        import tensorflow as tf
        sess = tf.Session()

        sess.run(tf.global_variables_initializer())
        self._restore_checkpoint(graph_spec, sess)
        outputs = sess.run(output_tensors)

        errors = {}        
        results = {}
        for layer_id in ordered_ids:
            # Find the default variable (the one that matches output tensor...)
            default_var = None

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
    
    def _get_output_tensors(self, graph_spec, ordered_ids, layer_instances):
        errors = {}
        output_tensors = {}
        for layer_id in ordered_ids:
            layer = layer_instances[layer_id]
            layer_spec = graph_spec[layer_id]

            if layer is None:
                continue
            

            if isinstance(layer, TrainingLayer):
                pass
            elif isinstance(layer, DataLayer):
                try:
                    y = tf.constant(layer.sample)            
                    output_tensors[layer_id] = y
                except Exception as e:
                    errors[layer_id] = exception_to_error(e)
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
                        errors[layer_id] = exception_to_error(e)
                else:
                    log.debug(f'Layer {layer_id} expected inputs from layers {bw_cons}, got {list(args.keys())}. Skipping.')
                        
            else:
                errors[layer_id] = 'unknown type ' + str(type(layer))

        return output_tensors, errors
    
    
class LightweightCore:
    def __init__(self, issue_handler=None):
        self._issue_handler = issue_handler
    
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
       
        layer_instances, instance_errors = self._get_layer_instances(subgraph_spec)
            
        strategy = self._get_subgraph_strategy(subgraph_spec)
        results, strategy_errors = strategy.run(subgraph_spec, ordered_ids, layer_instances)
        
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
    def _get_layer_instances(self, graph_spec):
        instances, errors = {}, {}
        for layer_id, spec in graph_spec.items():
            if not self._can_instantiate_layer(layer_id, spec):
                instances[layer_id] = None
                continue
            
            instance, error = self._get_layer_instance(layer_id, spec)
            instances[layer_id] = instance

            if error is not None:
                errors[layer_id] = error
        return instances, errors

    def _can_instantiate_layer(self, layer_id, layer_spec):
        # TODO: this should simply check that all the parameters are present in the spec. Until we have a stronger spec, try to render it and if it doesn't work return false
        sf = ScriptFactory()                 
        try:
            if layer_spec['Code'] is None or layer_spec['Code'] == '' or layer_spec['Code'].get('Output') is None:
                code = sf.render_layer_code(layer_id, layer_spec['Type'], layer_spec)
            else:
                code = layer_spec['Code'].get('Output')
        except:
            return False
        else:
            return True
        
    def _get_layer_instance(self, layer_id, layer_spec):
        # TODO: revise to not use exec if possible. Fix imports! Align with Graph-object!

        sf = ScriptFactory()         # TODO: move out
        try:
            if layer_spec['Code'] is None or layer_spec['Code'] == '' or layer_spec['Code'].get('Output') is None:
                code = sf.render_layer_code(layer_id, layer_spec['Type'], layer_spec)
            else:
                code = layer_spec['Code'].get('Output')
        except Exception as e:
            if self._issue_handler:
                with self._issue_handler.create_issue('Getting code for layer {layer_id} failed.', e) as issue:
                    self._issue_handler.put_error(issue.frontend_message)
                    log.error(issue.internal_message)
            else:
                log.exception('Getting code for layer {layer_id} failed.')                
            raise

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
            error = exception_to_error(e)
            return None, error
        except Exception as e:
            error = exception_to_error(e)            
            return None, error

        layer_class = list(locs.values())[0]

        try:
            instance = layer_class()
        except Exception as e:
            # "userland runtime errors"        
            error = exception_to_error(e)
            return None, error
        
        return instance, None


class LightweightCoreAdapter:
    def __init__(self, graph_dict, layer_extras_reader, error_handler, issue_handler):
        self._graph_dict = graph_dict
        self._error_handler = error_handler
        self._extras_reader = layer_extras_reader
        self._error_handler = error_handler

        self._core = LightweightCore(issue_handler)

    def run(self):
        graph_spec = copy.deepcopy(self._graph_dict)
        results, instance_errors, strategy_errors = self._core.run(graph_spec)

        extras_dict = {}
        for layer_id, layer_info in results.items():
            #if layer_id == '1564399786876':
            #    import pdb; pdb.set_trace()
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
            self._errors_dict[layer_id] = error
        
        for layer_id, error in instance_errors.items():
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
    ler = LayerExtrasReader()
    
        
    lw_core = LightweightCoreAdapter(dd, ler)
    lw_core.run()

    import pdb; pdb.set_trace()
        
            




















