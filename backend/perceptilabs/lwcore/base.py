import os
import logging
import hashlib
import copy
import json
import time
import importlib
import threading
from collections import namedtuple
import numpy as np
from tempfile import NamedTemporaryFile
from typing import Tuple, Dict, List

from perceptilabs.utils import stringify, add_line_numbering, Timer
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
from perceptilabs.caching.lightweight_cache import LightweightCache
from perceptilabs.lwcore.strategies import DefaultStrategy, DataSupervisedStrategy, DataReinforceStrategy, Tf1xInnerStrategy, Tf1xTrainingStrategy, Tf2xInnerStrategy, Tf2xTrainingStrategy, IoLayerStrategy
from perceptilabs.lwcore.results import LayerResults
from perceptilabs.caching.utils import NullCache
import perceptilabs.dataevents as dataevents


logger = logging.getLogger(APPLICATION_LOGGER)


def print_result_errors(layer_spec, results):
    text = 'Layer ' + str(layer_spec) + ' has errors.'
    for error_type, userland_error in results.errors:
        text += '\n' + error_type + ': ' + userland_error.format()
    logger.debug(text)


class LightweightCore:
    def __init__(self, issue_handler=None, cache=NullCache(), data_loader=None):
        self._issue_handler = issue_handler
        self._cache = cache.for_compound_keys()
        self._script_factory = ScriptFactory()
        self._data_loader = data_loader

    def run(self, graph_spec):
        t0 = time.perf_counter()
        subgraph_specs = graph_spec.split(GraphSplitter())
        all_results = {}
        all_durations = {}
        all_used_cache = {}

        data_batch = self._get_flat_data_batch()
        dataset_hash = self._data_loader.settings.compute_hash() if self._data_loader else ''

        for subgraph_spec in subgraph_specs:
            subgraph_results, subgraph_durations, subgraph_used_cache = self._run_subgraph(subgraph_spec, data_batch, dataset_hash)
            all_results.update(subgraph_results)
            all_durations.update(subgraph_durations)
            all_used_cache.update(subgraph_used_cache)

        t_total = time.perf_counter() - t0
        layers_that_used_cache = [layer_id for layer_id, used_cache in all_used_cache.items() if used_cache]
        logger.info(f"Ran lightweight core. Duration: {t_total}s. Used cache for layers: "  + ", ".join(layers_that_used_cache))

        self._maybe_print_results(graph_spec, all_results)
        return all_results

    def _run_subgraph(self, subgraph_spec, data_batch, dataset_hash):
        all_results = {}
        all_durations = {}
        all_used_cache = {}
        for layer_spec in subgraph_spec.get_ordered_layers():
            layer_result, durations, used_cache = self._get_layer_results(layer_spec, subgraph_spec, all_results, data_batch, dataset_hash)

            if logger.isEnabledFor(logging.DEBUG) and layer_result.has_errors:
                print_result_errors(layer_spec, layer_result)

            all_durations[layer_spec.id_] = durations
            all_used_cache[layer_spec.id_] = used_cache
            all_results[layer_spec.id_] = layer_result

        assert len(all_results) == len(subgraph_spec)
        return all_results, all_durations, all_used_cache

    def _cache_key(self, layer_spec, subgraph_spec, dataset_hash):
        layer_hash = subgraph_spec.compute_field_hash(layer_spec, include_ancestors=True)
        hasher = hashlib.md5()
        hasher.update(str(layer_hash).encode())
        hasher.update(dataset_hash.encode())
        return ['previews', hasher.hexdigest()]


    def _get_layer_results(self, layer_spec, subgraph_spec, ancestor_results, data_batch, dataset_hash):
        timer = Timer()
        desc = f"layer {layer_spec.id_} [{layer_spec.type_}]."

        key = self._cache_key(layer_spec, subgraph_spec, dataset_hash)

        def calculate_result():
            with timer.wrap('compute'):
                return self._compute_layer_results(layer_spec, subgraph_spec, ancestor_results, data_batch)


        with timer.wrap('all'):
            layer_result, used_cache = self._cache.get_or_calculate(key, calculate_result)

        durations = timer.calc(
            t_cache_lookup=('pre_all', 'pre_compute'),
            t_compute=('pre_compute', 'post_compute'),
            t_cache_insert=('post_compute', 'post_all'),
        )
        durations = {**durations, 'used_cache': used_cache, 'type': layer_spec.type_}
        return layer_result, durations, used_cache

    def _compute_layer_results(self, layer_spec, graph_spec, all_results, data_batch):
        """ Find and invoke a strategy for computing the results of a layer """
        input_results = {
            from_id: all_results[from_id]
            for (from_id, to_id) in graph_spec.edges_by_id if to_id == layer_spec.id_
        }

        strategy = self._get_layer_strategy(layer_spec, data_batch, self._script_factory)

        try:
            results = strategy.run(layer_spec, graph_spec, input_results)
        except:
            logger.exception(f"Failed running strategy '{strategy.__class__.__name__}' on layer {layer_spec.id_}")
            raise
        logger.debug(f"Computed results for layer {layer_spec.id_} [{layer_spec.type_}]")
        return results

    def _get_layer_strategy(self, layer_spec, data_batch, script_factory):
        if isinstance(layer_spec, IoLayerSpec):
            strategy = self._get_io_layer_strategy(layer_spec, data_batch)
        elif isinstance(layer_spec, TrainingLayerSpec):
            strategy = Tf2xTrainingStrategy(script_factory)
        elif isinstance(layer_spec, (DataDataSpec, DataRandomSpec)):
            strategy = DataSupervisedStrategy(script_factory)
        elif isinstance(layer_spec, DataEnvironmentSpec):
            strategy = DataReinforceStrategy(script_factory)
        elif isinstance(layer_spec, InnerLayerSpec):
            strategy = Tf2xInnerStrategy(script_factory)
        else:
            strategy = DefaultStrategy()
        return strategy

    def _get_io_layer_strategy(self, layer_spec, data_batch):
        feature_batch = data_batch[layer_spec.feature_name]
        strategy = IoLayerStrategy(feature_batch)
        return strategy

    def _get_flat_data_batch(self):
        data_batch = {}
        if self._data_loader is not None:
            dataset = self._data_loader.get_dataset(partition='training', shuffle=False)
            inputs_batch, targets_batch = next(iter(dataset))

            for feature_name, value in inputs_batch.items():
                data_batch[feature_name] = value
            for feature_name, value in targets_batch.items():
                data_batch[feature_name] = value

        return data_batch

    def _maybe_print_results(self, graph_spec, all_results):
        if not logger.isEnabledFor(logging.DEBUG):
            return

        text = 'Printing layer results\n'
        for layer_id, results in all_results.items():
            layer_spec = graph_spec[layer_id]
            output = results.sample.get('output')

            text += f"---- Results for: {layer_spec.id_} [{layer_spec.type_}] ----\n"
            text += f"has errors: {results.has_errors}\n"

            if output is not None:
                text += f"sample output max: {output.max()}\n"
                text += f"sample output min: {output.min()}\n"
                text += f"sample output shape: {output.shape}\n"
            else:
                text += "sample output is None"

        logger.debug(text)


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























