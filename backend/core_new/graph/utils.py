
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
