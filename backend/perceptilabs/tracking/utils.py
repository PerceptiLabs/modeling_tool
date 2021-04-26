def get_layer_counts(graph_spec):
    counts = {}
    
    def try_increment(key):
        try:
            counts[key] += 1
        except KeyError:
            counts[key] = 1    
    
    for layer_spec in graph_spec:
        try_increment('num_layers_total')
        try_increment(f'num_layers_{layer_spec.type_}')                            

    return counts
