import os
import logging
import copy
import json
import time
import importlib
import threading
from collections import namedtuple
import numpy as np
from tempfile import NamedTemporaryFile
from typing import Tuple, Dict, List

from perceptilabs.utils import stringify, add_line_numbering, is_tf2x, is_tf1x
from perceptilabs.issues import UserlandError
from perceptilabs.core_new.layers import BaseLayer, DataLayer, DataReinforce, DataSupervised, DataRandom, InnerLayer, Tf1xLayer, TrainingRandom, TrainingSupervised, TrainingReinforce, TrainingLayer, ClassificationLayer, ObjectDetectionLayer, RLLayer
from perceptilabs.graph.splitter import GraphSplitter
from perceptilabs.core_new.graph.utils import get_json_net_topology
from perceptilabs.core_new.graph.builder import GraphBuilder, SnapshotBuilder
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE
from perceptilabs.script import ScriptFactory
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.specbase import TrainingLayerSpec, InnerLayerSpec, IoLayerSpec
from perceptilabs.layers.datadata.spec import DataDataSpec
from perceptilabs.layers.datarandom.spec import DataRandomSpec
from perceptilabs.layers.dataenvironment.spec import DataEnvironmentSpec
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.lwcore.utils import exception_to_error, format_exception
from perceptilabs.lwcore.cache import LightweightCache
from perceptilabs.lwcore.strategies import DefaultStrategy, DataSupervisedStrategy, DataReinforceStrategy, Tf1xInnerStrategy, Tf1xTrainingStrategy, Tf2xInnerStrategy, Tf2xTrainingStrategy, IoLayerStrategy
from perceptilabs.lwcore.results import LayerResults
import perceptilabs.dataevents as dataevents


logger = logging.getLogger(APPLICATION_LOGGER)


def print_result_errors(layer_spec, results):
    text = 'Layer ' + str(layer_spec) + ' has errors.'
    for error_type, userland_error in results.errors:
        text += '\n' + error_type + ': ' + userland_error.format()
    logger.debug(text)

    
class LightweightCore:
    def __init__(self, issue_handler=None, cache=None, data_loader=None):
        self._issue_handler = issue_handler
        self._cache = cache
        self._script_factory = ScriptFactory(mode='tf2x' if is_tf2x() else 'tf1x')
        self._data_loader = data_loader
    
    def run(self, graph_spec):
        t0 = time.perf_counter()
        subgraph_specs = graph_spec.split(GraphSplitter())        
        all_results = {}
        all_durations = {}
        all_used_cache = {}

        for subgraph_spec in subgraph_specs:
            subgraph_results, subgraph_durations, subgraph_used_cache = self._run_subgraph(subgraph_spec)
            all_results.update(subgraph_results)
            all_durations.update(subgraph_durations)
            all_used_cache.update(subgraph_used_cache)

        t_total = time.perf_counter() - t0
        layers_that_used_cache = [layer_id for layer_id, used_cache in all_used_cache.items() if used_cache]        
        logger.info(f"Ran lightweight core. Duration: {t_total}s. Used cache for layers: "  + ", ".join(layers_that_used_cache))
        
        return all_results
    
    def _run_subgraph(self, subgraph_spec):
        all_results = {}
        all_durations = {}
        all_used_cache = {}
        for layer_spec in subgraph_spec.get_ordered_layers():
            layer_result, durations, used_cache = self._get_layer_results(layer_spec, subgraph_spec, all_results)
            
            if logger.isEnabledFor(logging.DEBUG) and layer_result.has_errors:
                print_result_errors(layer_spec, layer_result)
                
            all_durations[layer_spec.id_] = durations
            all_used_cache[layer_spec.id_] = used_cache                    
            all_results[layer_spec.id_] = layer_result                
            
        assert len(all_results) == len(subgraph_spec)
        return all_results, all_durations, all_used_cache

    def _get_layer_results(self, layer_spec, subgraph_spec, ancestor_results):
        """ Either fetched a cached result or Computes results of layer_spec using ancestor results """        
        t0 = time.perf_counter()        
        cached_result, layer_hash = self._get_cached_result(layer_spec, subgraph_spec)
        t1 = time.perf_counter()
        layer_result = cached_result or self._compute_layer_results(layer_spec, subgraph_spec, ancestor_results)
        t2 = time.perf_counter()
        self._maybe_put_results_in_cache(layer_spec, cached_result, layer_result, layer_hash)
        t3 = time.perf_counter()

        used_cache = cached_result is not None
        durations = {'t_cache_lookup': t1 - t0, 't_compute': t2 - t1, 't_cache_insert': t3 - t2, 'used_cache': used_cache, 'type': layer_spec.type_}
        return layer_result, durations, used_cache

    def _maybe_put_results_in_cache(self, layer_spec, cached_result, layer_result, layer_hash):
        """ Try to put new results in cache """        
        if cached_result is None and self._cache is not None and layer_hash is not None:                        
            self._cache.put(layer_hash, layer_result)
            logger.debug(f"Cached computed results for layer {layer_spec.id_} [{layer_spec.type_}]. Hash: {layer_hash}")

    def _get_cached_result(self, layer_spec, subgraph_spec):
        """ Computes layer hash and retrieves cached result if available. """
        cached_result = None
        layer_hash = None
        
        if self._cache is not None:
            layer_hash = subgraph_spec.compute_field_hash(layer_spec, include_ancestors=True)
            logger.debug(f"Computed hash for layer {layer_spec.id_} [{layer_spec.type_}]. Hash: {layer_hash}")
            
            if layer_hash in self._cache:
                cached_result = self._cache.get(layer_hash)
                logger.debug(f"Retrieved cached results for layer {layer_spec.id_} [{layer_spec.type_}]. Hash: {layer_hash}")
                
        return cached_result, layer_hash

    def _compute_layer_results(self, layer_spec, graph_spec, all_results):
        """ Find and invoke a strategy for computing the results of a layer """
        input_results = {
            from_id: all_results[from_id]
            for (from_id, to_id) in graph_spec.edges_by_id if to_id == layer_spec.id_
        }
        
        strategy = self._get_layer_strategy(layer_spec, graph_spec, self._script_factory)
        
        try:
            results = strategy.run(layer_spec, graph_spec, input_results)
        except:
            logger.exception(f"Failed running strategy '{strategy.__class__.__name__}' on layer {layer_spec.id_}")
            raise
        logger.debug(f"Computed results for layer {layer_spec.id_} [{layer_spec.type_}]")
        return results

    def _get_layer_strategy(self, layer_spec, graph_spec=None, script_factory=None):
        if isinstance(layer_spec, IoLayerSpec):
            strategy = IoLayerStrategy(self._data_loader)            
        elif isinstance(layer_spec, TrainingLayerSpec) and is_tf1x():
            strategy = Tf1xTrainingStrategy(script_factory)
        elif isinstance(layer_spec, TrainingLayerSpec) and is_tf2x():
            strategy = Tf2xTrainingStrategy(script_factory)            
        elif isinstance(layer_spec, (DataDataSpec, DataRandomSpec)):
            strategy = DataSupervisedStrategy(script_factory)
        elif isinstance(layer_spec, DataEnvironmentSpec):
            strategy = DataReinforceStrategy(script_factory)
        elif isinstance(layer_spec, InnerLayerSpec) and is_tf1x(): 
            strategy = Tf1xInnerStrategy(script_factory)
        elif isinstance(layer_spec, InnerLayerSpec) and is_tf2x(): 
            strategy = Tf2xInnerStrategy(script_factory)
        else:
            strategy = DefaultStrategy()
        return strategy


class LightweightCoreAdapter:
    """ Compatibility with v1 core """
    def __init__(self, graph_spec, layer_extras_reader, error_handler, issue_handler, cache, data_dict, data_loader=None):
        self._graph_spec = graph_spec
        self._error_handler = error_handler
        self._extras_reader = layer_extras_reader
        self._error_handler = error_handler
        self._data_dict = data_dict
        
        self._core = LightweightCore(
            issue_handler=issue_handler,
            cache=cache,
            data_loader=data_loader
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
                'cols': layer_info.columns,
                'trained': layer_info.trained
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
    
        
            




















