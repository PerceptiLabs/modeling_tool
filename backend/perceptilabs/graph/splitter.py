import networkx as nx
import uuid


class _Node:
    def __init__(self, id):
        self._id = id
        self._hash = hash((uuid.uuid4(), id))

    @property
    def id(self):
        return self._id

    def __hash__(self):
        return self._hash

    
class GraphSplitter:
    def _build_complete_graph(self, node_ids, edges_by_id):
        id_to_node = {}        
        graph = nx.DiGraph()

        for id1, id2 in edges_by_id:
            if id1 not in id_to_node:
                id_to_node[id1] = _Node(id1)
            if id2 not in id_to_node:
                id_to_node[id2] = _Node(id2)
            graph.add_edge(id_to_node[id1], id_to_node[id2])

        for id_ in node_ids:
            if id_ not in id_to_node:
                id_to_node[id_] = _Node(id_)
            graph.add_node(id_to_node[id_])
                
        return graph

    def _get_subgraphs(self, disjoint_graphs, split_ids):
        if split_ids is None:
            return disjoint_graphs
        
        all_subgraphs = []
        for graph in disjoint_graphs:
            # Split the graph at select nodes. 
            # Remove their outgoing connections and create an equivalent node with those.            
            new_edges = []
            for edge in graph.edges:
                node1, node2 = edge
                if node1.id in split_ids:
                    print("replacing edge!")
                    edge = (_Node(node1.id), node2) # Create a new, equivalent, instance
                    
                new_edges.append(edge)

            # Pick up isolated nodes
            isolated_nodes = []
            for node in graph.nodes:
                if len(list(graph.neighbors(node))) == 0:
                    isolated_nodes.append(node)

            # Create a graph, this one with two versions of the nodes to split at.
            new_graph = nx.DiGraph()
            new_graph.add_edges_from(new_edges)
            new_graph.add_nodes_from(isolated_nodes)

            # Extract disjoint subgraphs
            subgraphs = self._get_disjoint_graphs(new_graph)
            all_subgraphs.extend(subgraphs)            
                
        return all_subgraphs

    def _get_disjoint_graphs(self, graph):
        disj_graphs = []
        for nodes in nx.weakly_connected_components(graph):
            new_graph = graph.subgraph(nodes).copy()
            disj_graphs.append(new_graph)
        return disj_graphs    
        
    def split(self, node_ids, edges_by_id, split_ids=None):
        complete_graph = self._build_complete_graph(node_ids, edges_by_id)
        disjoint_graphs = self._get_disjoint_graphs(complete_graph)
        subgraphs = self._get_subgraphs(disjoint_graphs, split_ids)

        result = []
        for subgraph in subgraphs:
            _node_ids = [n.id for n in subgraph.nodes]
            _edges_by_id = [(n1.id, n2.id) for n1, n2 in subgraph.edges]
            result.append((_node_ids, _edges_by_id))
        return result
