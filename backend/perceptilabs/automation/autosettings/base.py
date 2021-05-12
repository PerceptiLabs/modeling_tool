import logging
import collections
from typing import Dict, Tuple, Type, List
from abc import ABC, abstractmethod
import networkx as nx

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.lwcore import LayerResults
from perceptilabs.layers.specbase import LayerSpec, DummySpec
from perceptilabs.layers.utils import get_layer_definition
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
    def apply(self, graph_spec: GraphSpec, layer_spec: LayerSpec, lw_results: Dict[str, LayerResults]) -> LayerSpec:
        """ A new layer will be created based on the builder configuration """
        raise NotImplementedError


class SettingsEngine:
    def __init__(self, inference_rules: List[Type['InferenceRule']], lw_core=None):
        self._rule_classes = inference_rules
        self._lw_core = lw_core

    def run(self, graph_spec: GraphSpec, lw_results=None):
        skip_ids = []
        for spec in graph_spec.nodes_by_id.values():
            if spec.visited:
                skip_ids.append(spec.id_)                
                logger.info(f"Skipping settings recommendations for layer {spec.id_} because it has been modified by the user")
                
            if isinstance(spec, DummySpec):
                skip_ids.append(spec.id_)
                logger.info(f"Cannot make settings recommendation for layer {spec.id_}: no spec object/builder found for type '{spec.type_}'")

        rules = [rc() for rc in self._rule_classes]
        ordered_ids, rule_instances = self._get_ordered_layers(graph_spec, rules, skip_ids)

        # Loop over IDs instead of objects because the object instance will change
        new_specs = {}


        current_graph_spec = graph_spec
        for layer_id in ordered_ids:
            original_layer_spec = current_graph_spec.nodes_by_id[layer_id]
            spec_class = get_layer_definition(original_layer_spec.type_).spec_class

            if lw_results is None and self._lw_core is not None:            
                lw_results = self._lw_core.run(current_graph_spec)

            # Apply all topologically valid rules in order
            current_layer_spec = original_layer_spec
            for rule in rule_instances[original_layer_spec.id_]:
                current_layer_spec = self._maybe_apply_rule(rule, current_graph_spec, current_layer_spec, lw_results)
                
            if current_layer_spec != original_layer_spec:
                new_specs[current_layer_spec.id_] = current_layer_spec

                # Build a new graph spec
                current_graph_dict = current_graph_spec.to_dict()
                current_graph_dict[current_layer_spec.id_] = current_layer_spec.to_dict()
                current_graph_spec = GraphSpec.from_dict(current_graph_dict)

        if current_graph_spec != graph_spec:
            return current_graph_spec
        else:
            return None

    def _maybe_apply_rule(self, rule, current_graph_spec, current_layer_spec, lw_results):
        new_layer_spec = current_layer_spec # Default
        try:
            if rule.is_applicable(current_graph_spec, current_layer_spec, lw_results):
                new_layer_spec = rule.apply(current_graph_spec, current_layer_spec, lw_results)
                logger.info(f"Autosettings: applied rule {rule.__class__.__name__} to {current_layer_spec}")                
        except:
            logger.exception(f"Autosettings: rule {rule.__class__.__name__} crashed unexpectedly when applied to layer {current_layer_spec.id_} [{current_layer_spec.type_}]")
        finally:
            return new_layer_spec
                                        
            
                
    def _get_ordered_layers(self, graph_spec, rules, skip_ids):
        """Create settings&data depency graph

        Augment the current dependency graph (considers data dependencies only)
        to incorporate dependencies on the settings of other layers
        """
        nx_graph = nx.DiGraph()
        nx_graph.add_nodes_from(graph_spec.node_ids)
        nx_graph.add_edges_from(graph_spec.edges)

        rule_instances = collections.defaultdict(list)        
        for id_ in graph_spec.node_ids:
            if id_ in skip_ids:
                continue

            layer_spec = graph_spec.nodes_by_id[id_]
            for rule_class in self._rule_classes:
                rule = rule_class()
                is_valid, dependencies = rule.is_topologically_valid(graph_spec, layer_spec)

                if is_valid:
                    nx_graph.add_edges_from(
                        [(dependency.id_, layer_spec.id_) for dependency in dependencies]
                    )
                    rule_instances[layer_spec.id_].append(rule)
                    
        DEBUG = False
        if DEBUG:
            print(list(nx.topological_sort(nx_graph)))
            import matplotlib.pyplot as plt
            pos = nx.kamada_kawai_layout(nx_graph)
            nx.draw(nx_graph, pos, with_labels=True)
            plt.show()

        return nx.topological_sort(nx_graph), rule_instances

