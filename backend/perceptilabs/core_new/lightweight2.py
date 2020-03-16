# TODO: (1) create flask server for running in remote process. (2) dynamic imports (3) more descriptive errors.

import traceback
import copy
import json
import time
import networkx as nx
import requests
import importlib
import threading
from flask import Flask, request, jsonify
from collections import namedtuple

from perceptilabs.core_new.layers.definitions import resolve_checkpoint_path
from perceptilabs.core_new.layers import BaseLayer, DataLayer, InnerLayer, Tf1xLayer, TrainingLayer, ClassificationLayer
from perceptilabs.core_new.graph.splitter import GraphSplitter
from perceptilabs.core_new.graph.utils import get_json_net_topology
from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE
from perceptilabs.core_new.layers.script import ScriptFactory

LayerInfo = namedtuple('LayerInfo', ['sample', 'out_shape', 'in_shape', 'variables', 'default_var'])


def simplify_spec(func):
    def inner(self, graph_spec):
        if 'Layers' in graph_spec:
            graph_spec = copy.deepcopy(graph_spec['Layers'])
        return func(self, graph_spec)
    return inner


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

            if isinstance(layer, TrainingLayer):
                pass
            elif isinstance(layer, DataLayer):
                try:
                    y = tf.constant(layer.sample)            
                    output_tensors[layer_id] = y
                except:
                    errors[layer_id] = 'failed getting datalayer sample'
            elif isinstance(layer, InnerLayer):
                try:
                
                    input_ids = [x[0] for x in layer_spec['backward_connections']]
                    args = [output_tensors[id_] for id_ in input_ids]
                    y = layer(*args)            
                    output_tensors[layer_id] = y
                except:
                    errors[layer_id] = 'failed for inner layer'
            else:
                errors[layer_id] = 'unknown type ' + str(type(layer))

        return output_tensors, errors
    
    
class LightweightCore:
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
            instance, error = self._get_layer_instance(layer_id, spec)
            instances[layer_id] = instance

            if error is not None:
                errors[layer_id] = error
        return instances, errors
            
    def _get_layer_instance(self, layer_id, layer_spec):
        # TODO: revise to not use exec if possible. Fix imports! Align with Graph-object!

        sf = ScriptFactory()         # TODO: move out
        try:
            if layer_spec['Code'] is None or layer_spec['Code'] == '' or layer_spec['Code'].get('Output') is None:
                code = sf.render_layer_code(layer_id, layer_spec['Type'], layer_spec)
            else:
                code = layer_spec['Code'].get('Output')
        except Exception as e:
            tb = traceback.TracebackException(e.__class__,
                                              e,
                                              e.__traceback__)
            
            descr = "".join(tb.format_exception_only())

            
            print('code prob', e, descr)
            
        #return None, f"code problem!"

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
        except Exception as e:
            return None, f"exec problem!"            

        layer_class = list(locs.values())[0]
        instance = layer_class()
        return instance, None


class LightweightCoreAdapter:
    def __init__(self, graph_dict, layer_extras_reader, error_handler):
        self._graph_dict = graph_dict
        self._error_handler = error_handler
        self._extras_reader = layer_extras_reader
        self._error_handler = error_handler

        self._core = LightweightCore()

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

        for layer_id, error in {**instance_errors, **strategy_errors}.items():
            pass

    @property
    def error_handler(self):
        return self._error_handler
            

if __name__ == "__main__":
    import json    
    with open('net.json_', 'r') as f:
        dd = json.load(f)

    from perceptilabs.core_new.extras import LayerExtrasReader
    ler = LayerExtrasReader()
    
        
    lw_core = LightweightCoreAdapter(dd, ler)
    lw_core.run()

    import pdb; pdb.set_trace()
        
            











'''        
app = Flask(__name__)


graph_builder = GraphBuilder()

snapshot_builder = SnapshotBuilder(
    BASE_TO_REPLICA_MAP, 
    REPLICATED_PROPERTIES_TABLE
)

cache = {}


@app.route('/', methods=['GET'])
def endpoint_index():
    import time
    import hashlib

    t0 = time.perf_counter()
    
    with open('deploy.py', 'rt') as f: 
        text = f.read()
        key = hashlib.md5(text.encode('utf-8')).hexdigest()

    if key in cache:
        snapshot = cache[key]
    else:
        spec = importlib.util.spec_from_file_location("deployed_module", 'deploy.py') # TODO: dont hardcode path, load from request instead
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        graph = module.get_graph()

        print(time.perf_counter() - t0, 'aaa')        

        t11 = time.perf_counter()
        iterator = graph.training_nodes[0].layer_instance.run(graph)

        sentinel = object()
        next(iterator, sentinel)

        print(time.perf_counter() - t11)
        
        snapshot = snapshot_builder.build(graph)

        #cache[key] = snapshot # TODO: disable for now.

    t1 = time.perf_counter()
    dt = t1 - t0

    print(f"lw pass time: {dt}")
    
    
    return 'aa'


@app.route('/status', methods=['GET'])
def endpoint_status(self):
    return 'running'


@app.route('/initialize', methods=['GET'])
def endpoint_initialize():
    target = request.args.get("target", None)

    if target == 'tf1x':
        import tensorflow as tf
    else:
        raise ValueError("Unknown initializer")

    return jsonify({'aa': 'bb'})

def start_service(port, new_process=False):
    if not new_process:
        app.run(port=str(port), threaded=True)
    else:
        from multiprocessing import Process
        proc = Process(target=start_service, args=(port,), kwargs={'new_process': False})
        proc.start()
        

def is_service_available():
    #requests.get
    pass



class LightweightCore2:

    def __init__(self, address):
        self._address = address


    def run(self, code):
        r = requests.get(self._address, json={'code': ''})
        print(r.json)
    
    
        
    

    

    
if __name__ == "__main__":
    start_service(8181, new_process=True)

'''














