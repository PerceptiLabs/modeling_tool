import logging
import networkx as nx
from collections import namedtuple
from typing import List, Dict, Tuple, Set
import hashlib


from perceptilabs.graph import AbstractGraphSpec
from perceptilabs.layers.specbase import LayerSpec
from perceptilabs.layers.utils import get_layer_definition


logger = logging.getLogger(__name__)


class GraphSpec(AbstractGraphSpec):
    def __init__(self, nodes: List[LayerSpec]):
        self._nx_graph = self._create_networkx_graph(nodes)
        self._nodes_by_id = {n.id_: n for n in nodes}

    def to_dict(self):
        dict_ = {}
        for id_, node in self.nodes_by_id.items():
            dict_[id_] = node.to_dict()
        return dict_

    @classmethod
    def from_dict(cls, dict_):
        try:
            if not isinstance(dict_, dict):
                raise ValueError(f"Expected a dict but got type {type(dict_)}")

            if "Layers" in dict_:
                dict_ = dict_["Layers"]

            layer_specs = [
                cls._parse_layer_spec(id_, spec_dict)
                for id_, spec_dict in dict_.items()
            ]
            return cls(layer_specs)
        except:
            logger.exception(f"Loading graph spec from dict failed. Content: {dict_}")
            raise

    @staticmethod
    def _parse_layer_spec(id_, spec_dict):
        if not isinstance(spec_dict, dict):
            raise ValueError(
                f"Expected a dict but got type {type(spec_dict)} for layer with ID {id_}"
            )

        try:
            type_ = spec_dict["Type"]
            layer_def = get_layer_definition(type_)
            layer_spec = layer_def.spec_class.from_dict(id_, spec_dict)
        except:
            from perceptilabs.utils import stringify

            logger.error(
                "Failed building layer from dict: {}".format(stringify(spec_dict))
            )
            raise
        else:
            return layer_spec

    @property
    def layers(self) -> List[LayerSpec]:
        return list(self.nodes_by_id.values())

    @property
    def input_layers(self) -> List[LayerSpec]:
        return [x for x in self.layers if x.is_input_layer]

    @property
    def target_layers(self) -> List[LayerSpec]:
        return [x for x in self.layers if x.is_target_layer]

    @property
    def io_layers(self) -> List[LayerSpec]:
        return [x for x in self.layers if (x.is_target_layer or x.is_input_layer)]

    @property
    def inner_layers(self) -> List[LayerSpec]:
        return [x for x in self.layers if x not in self.io_layers]

    def get_layer_by_feature_name(self, name):
        for layer_spec in self.io_layers:
            if layer_spec.feature_name == name:
                return layer_spec
        return None

    @property
    def nodes(self) -> List[LayerSpec]:
        return self.layers

    @property
    def edges(self) -> List[Tuple[str, str]]:
        return list(self._nx_graph.edges)

    def __getitem__(self, key):
        if key not in self.nodes_by_id and key not in self.nodes_by_name:
            ids = list(self.nodes_by_id.keys())
            raise ValueError(f"No layer with id {key}. Available layers are: {ids}")
        if key in self.nodes_by_sanitized_name:
            return self.nodes_by_name.get(key)

        return self.nodes_by_id[key]

    def get_layer_by_sanitized_name(self, sanitized_name):
        return self.nodes_by_sanitized_name[sanitized_name]

    def get_successors(self, layer_spec: LayerSpec):
        """Get all nodes directly connected from layer_spec"""
        return [
            self.__getitem__(id_) for id_ in self._nx_graph.successors(layer_spec.id_)
        ]

    def get_predecessors(self, layer_spec: LayerSpec):
        """Get all nodes directly connected to layer_spec"""
        return [
            self.__getitem__(id_) for id_ in self._nx_graph.predecessors(layer_spec.id_)
        ]

    def get_ancestors(self, layer_spec: LayerSpec):
        """Get all nodes with a path to layer_spec"""
        return [
            self.__getitem__(id_)
            for id_ in nx.algorithms.dag.ancestors(self._nx_graph, layer_spec.id_)
        ]

    def compute_field_hash(self, layer_spec, include_ancestors=True):
        """Computes a hash based on the fields (and maybe ancestors) of the layer

        Args:
            include_ancestors: compute the hashes of the ancestors as well
        """
        included_specs = [layer_spec]  # The layer itself

        if include_ancestors:
            included_specs += self.get_ancestors(layer_spec)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Computing field hash of layer {layer_spec.id_} [{layer_spec.type_}] based on layers {[x.id_ for x in included_specs]}"
            )

        hasher = hashlib.md5()
        for spec in included_specs:
            hasher.update(str(spec.compute_field_hash()).encode())

        return hasher.hexdigest()

    def get_ordered_ids(self) -> List[str]:
        """Returns the layers in terms of execution order

        Returns:
            A list of ID strings
        """
        topological_tree = list(nx.topological_sort(self._nx_graph))
        ordered_ids = tuple(topological_tree)
        return ordered_ids

    def get_ordered_layers(self) -> List[LayerSpec]:
        """Returns the layers in terms of execution order.

        Returns:
            A list of LayerSpecs
        """
        return [self.nodes_by_id[id_] for id_ in self.get_ordered_ids()]

    def get_ordered_nodes(self):
        """Returns the layers in terms of execution order. Alias for 'get_ordered_layers'

        Returns:
            A list of LayerSpecs
        """
        return self.get_ordered_layers()

    def __eq__(self, other):
        return len(self.difference(other)) == 0

    def get_origin(self, layer_spec: LayerSpec):
        """Return the 'start nodes' connected to this layer (possibly including the layer itself)"""
        if len(layer_spec.backward_connections) == 0:
            return [layer_spec]
        else:
            original_ancestors = [
                ancestor_spec
                for ancestor_spec in self.get_ancestors(layer_spec)
                if len(ancestor_spec.backward_connections) == 0
            ]
            return original_ancestors

    @property
    def nodes_by_id(self):
        return self._nodes_by_id.copy()

    @property
    def nodes_by_name(self):
        return {layer_spec.name: layer_spec for layer_spec in self.nodes}

    @property
    def nodes_by_sanitized_name(self):
        return {layer_spec.sanitized_name: layer_spec for layer_spec in self.nodes}

    @property
    def node_ids(self):
        return self.layer_ids

    @property
    def layer_ids(self):
        return list(self.nodes_by_id.keys())

    @property
    def edges_by_id(self):
        return [(src_id, dst_id) for src_id, dst_id in self._nx_graph.edges()]

    def get_subgraph(self, layer_ids):
        nx_graph = self._nx_graph.subgraph(layer_ids)

        nodes = [self.nodes_by_id[id_] for id_ in nx_graph.nodes]
        edges = [
            (self.nodes_by_id[id1], self.nodes_by_id[id2])
            for id1, id2 in nx_graph.edges
        ]
        return GraphSpec(list(nodes), list(edges))

    def split(self, splitter):
        subgraph_topologies = splitter.split(self.layer_ids, self.edges_by_id)

        subgraphs = []
        for subgraph_node_ids, subgraph_edges_by_id in subgraph_topologies:
            subgraph_nodes = [self.nodes_by_id[id_] for id_ in subgraph_node_ids]
            subgraph = GraphSpec(subgraph_nodes)
            subgraphs.append(subgraph)
        return subgraphs

    def __len__(self):
        return len(self.nodes_by_id)

    def __iter__(self):
        return iter(self.nodes_by_id.values())

    def show(self):
        import matplotlib
        import matplotlib.pyplot as plt

        matplotlib.use("TkAgg")

        pos = nx.kamada_kawai_layout(self._nx_graph)

        labels = {
            id_: f"{id_} [{self.nodes_by_id[id_].type_}]"
            for id_ in self._nx_graph.nodes
        }
        nx.draw(self._nx_graph, pos, labels=labels, with_labels=True)

        edge_labels = {
            (
                conn_spec.src_id,
                conn_spec.dst_id,
            ): f"{conn_spec.src_var} to {conn_spec.dst_var}"
            for conn_spec in self._get_connections(self.nodes)
        }
        nx.draw_networkx_edge_labels(
            self._nx_graph, pos, edge_labels=edge_labels, font_color="red"
        )

        plt.show()

    def items(self):
        return self.nodes_by_id.items()

    def get_start_nodes(self):
        start_nodes = [
            node for node in self.nodes if len(node.backward_connections) == 0
        ]
        return start_nodes

    def _get_connections(self, layer_specs):
        bw_cons = set()
        fw_cons = set()
        for layer_spec in layer_specs:
            for conn_spec in layer_spec.backward_connections:
                bw_cons.add(conn_spec)
            for conn_spec in layer_spec.forward_connections:
                fw_cons.add(conn_spec)

        if bw_cons != fw_cons:
            bw_cons_extra = bw_cons.difference(fw_cons)
            fw_cons_extra = fw_cons.difference(bw_cons)

            text = "Mismatch between backwards/forward connections."
            if len(bw_cons_extra) > 0:
                text += (
                    f"\nConnections {bw_cons_extra} in backwards, but not in forwards."
                )
            if len(fw_cons_extra) > 0:
                text += (
                    f"\nConnections {fw_cons_extra} in forwards, but not in backwards."
                )
            raise RuntimeError(text)

        return bw_cons

    def _create_networkx_graph(self, layer_specs):
        nx_graph = nx.DiGraph()

        connections = self._get_connections(layer_specs)
        edges_by_id = [
            (conn_spec.src_id, conn_spec.dst_id) for conn_spec in connections
        ]

        nx_graph.add_edges_from(edges_by_id)
        nx_graph.add_nodes_from([l.id_ for l in layer_specs])
        return nx_graph

    @property
    def training_layer(self) -> LayerSpec:
        """Get the training layer of this graph. Assumes there's only one.

        Returns:
            The training layer.
        """
        for layer in self.layers:
            if layer.is_training_layer:
                return layer
        return None

    def difference(self, other: "GraphSpec") -> Set[str]:
        """Gets the IDs of layers that are different between two graphs

        Args:
            other: another GraphSpec

        Returns:
            a set of layer ids
        """

        if type(self) != type(other):
            return set()

        different_layers = set()
        for node1, node2 in zip(self.get_ordered_nodes(), other.get_ordered_nodes()):
            if node1 != node2:
                different_layers.add(node1.id_)

        return different_layers

    def __repr__(self):
        text = ""
        for layer in self.get_ordered_layers():
            text += repr(layer) + "\n"
        return text
