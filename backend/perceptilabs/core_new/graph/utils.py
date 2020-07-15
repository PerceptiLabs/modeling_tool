
def breadth_first_sort(graph, start_nodes):
    visited = []
    queue = [start_nodes]
 
    # keep looping until there are nodes still to be checked
    while queue:
        # pop shallowest node (first node) from queue
        id_ = queue.pop(0)
        if id_ not in visited:
            # add node to list of checked nodes
            visited.append(id_)
            neighbors = graph[id_]
 
            # add neighbors of node to queue
            for neighbor in neighbors:
                queue.append(neighbor)
    return visited


def sanitize_layer_name(name):
    from perceptilabs.graph.spec.layers.base import sanitize_name
    name = name.replace(' ', '_')
    
    name = '_' + name
    return name


def get_json_net_topology(json_network, names_as_id=False):
    if 'Layers' in json_network:
        json_network = json_network['Layers']

    node_ids = []
    edges_by_id = []
    for id_, spec in json_network.items():
        node_ids.append(str(id_))

        for bw_id, bw_name in spec['backward_connections']:
            if names_as_id:
                bw_id = bw_name
            edge = (str(bw_id), str(id_))
            edges_by_id.append(edge)

    return node_ids, edges_by_id

        

        
    
    
    
    
    
