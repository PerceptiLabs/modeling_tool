
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
    from perceptilabs.layers.specbase import sanitize_name
    name = name.replace(' ', '_')
    name = '_' + name
    return name


def get_json_net_topology(json_network, names_as_id=False, include_var_names=False):
    if 'Layers' in json_network:
        json_network = json_network['Layers']

    node_ids = []
    edges_by_id = []
    var_names = {}
    for id_, spec in json_network.items():
        node_ids.append(str(id_))

        for conn_spec in spec['backward_connections']:
            dst_var = conn_spec['dst_var']                                                
            src_var = conn_spec['src_var']
            
            if names_as_id:
                bw_id = sanitize_layer_name(conn_spec['src_name'])
            else:
                bw_id = conn_spec['src_id']

            bw_id = str(bw_id)
            id_ = str(id_)
            edge = (bw_id, id_)
            edges_by_id.append(edge)

            if include_var_names:
                key = bw_id + ':' + id_
                if key not in var_names:
                    var_names[key] = []
                var_names[key].append((src_var, dst_var))
    if include_var_names:
        return node_ids, edges_by_id, var_names
    else:
        return node_ids, edges_by_id

        

        
    
    
    
    
    
