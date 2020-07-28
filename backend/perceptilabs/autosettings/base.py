import logging
import collections
from typing import Dict, Tuple, Type, List
from abc import ABC, abstractmethod
import networkx as nx

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.core_new.lightweight2 import LayerResults
from perceptilabs.graph.spec.layers import LayerSpec, LayerSpecBuilder, DummyBuilder, get_layer_builder, DummySpec
from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


class InferenceRule(ABC):
    @abstractmethod
    def is_topologically_valid(self, graph_spec: GraphSpec, layer_spec: LayerSpec) -> Tuple[bool, List[LayerSpec]]:
        """ Checks whether the all dependent nodes exist and returns them """
        raise NotImplementedError
    
    @abstractmethod
    def is_applicable(self, graph_spec: GraphSpec, layer_spec: LayerSpec, lw_results: Dict[str, LayerResults]) -> bool:
        """ Checks whether the rule applies to the current layer and graph """
        raise NotImplementedError

    @abstractmethod
    def apply(self, graph_spec: GraphSpec, layer_spec: LayerSpec, builder: LayerSpecBuilder, lw_results: Dict[str, LayerResults]) -> None:
        """ A new layer will be created based on the builder configuration """
        raise NotImplementedError


class SettingsEngine:
    def __init__(self, inference_rules: List[Type['InferenceRule']], lw_core=None):
        self._rule_classes = inference_rules
        self._lw_core = lw_core

    def run(self, graph_spec: GraphSpec, graph_spec_tmp=None):
        # TODO(anton.k): remove the graph_spec_tmp dependency once the lightweight core has been refactored
        #if graph_spec_tmp and self._lw_core:
        #    lw_results = self._lw_core.run(graph_spec_tmp)

        skip_ids = []
        for id in graph_spec.nodes:
            spec = graph_spec.nodes_by_id[id]

            if spec.visited:
                skip_ids.append(spec.id)                
                logger.warning(f"Skipping settings recommendations for layer {spec.id} because it has been modified by the user")
                
            if isinstance(spec, DummySpec):
                skip_ids.append(spec.id)
                logger.warning(f"Cannot make settings recommendation for layer {spec.id}: no spec object/builder found for type '{spec.type}'")

        rules = [rc() for rc in self._rule_classes]
        ordered_ids, rule_instances = self._get_ordered_layers(graph_spec, rules, skip_ids)

        # Loop over IDs instead of objects because the object instance will change
        new_specs = {}
        lw_results = None
        current_graph_spec = graph_spec
        for layer_id in ordered_ids:
            original_layer_spec = current_graph_spec.nodes_by_id[layer_id]
            standard_builder = get_layer_builder(original_layer_spec.type)

            if self._lw_core:
                current_graph_dict = current_graph_spec.to_dict()
                lw_results = self._lw_core.run(current_graph_dict)
                
            # Apply all topologically valid rules in order
            current_layer_spec = original_layer_spec
            for rule in rule_instances[original_layer_spec.id]:

                if rule.is_applicable(current_graph_spec, current_layer_spec, lw_results):
                    builder = standard_builder.from_existing(current_layer_spec)
                    rule.apply(current_graph_spec, current_layer_spec, builder, lw_results)
                    logger.info(f"Autosettings: applied rule {rule.__class__.__name__} to {current_layer_spec}")
                    current_layer_spec = builder.build()
                    
            if current_layer_spec != original_layer_spec:
                new_specs[current_layer_spec.id] = current_layer_spec

                # Build a new graph spec
                current_graph_dict = current_graph_spec.to_dict()
                current_graph_dict[current_layer_spec.id] = standard_builder.to_dict(current_layer_spec)
                current_graph_spec = GraphSpec.from_dict(current_graph_dict)
        return new_specs
            
                
    def _get_ordered_layers(self, graph_spec, rules, skip_ids):
        """Create settings&data depency graph

        Augment the current dependency graph (considers data dependencies only)
        to incorporate dependencies on the settings of other layers
        """
        nx_graph = nx.DiGraph()
        nx_graph.add_nodes_from(graph_spec.nodes)
        nx_graph.add_edges_from(graph_spec.edges)

        rule_instances = collections.defaultdict(list)        

        for id in graph_spec.nodes:
            if id in skip_ids:
                continue

            layer_spec = graph_spec.nodes_by_id[id]
            for rule_class in self._rule_classes:
                rule = rule_class()
                is_valid, dependencies = rule.is_topologically_valid(graph_spec, layer_spec)

                if is_valid:
                    nx_graph.add_edges_from([(dep.id, layer_spec.id) for dep in dependencies])
                    rule_instances[layer_spec.id].append(rule)
                    
        DEBUG = False
        if DEBUG:
            print(list(nx.topological_sort(nx_graph)))
            import matplotlib.pyplot as plt
            pos = nx.kamada_kawai_layout(nx_graph)
            nx.draw(nx_graph, pos, with_labels=True)
            plt.show()

        return nx.topological_sort(nx_graph), rule_instances

