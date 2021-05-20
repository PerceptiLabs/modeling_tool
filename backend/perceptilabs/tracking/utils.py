import collections
import numpy as np


def get_tool_version():
    """ Retrieves the version of the tool """
    import perceptilabs
    return perceptilabs.__version__


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


def aggregate_summaries(all_summaries):
    """ Returns a dict with the following structure:

    {
        'metric_accuracy_training_max_over_layers': 0.8,  
        'metric_accuracy_training_avg_over_layers': 0.5,
        'metric_accuracy_training_min_over_layers': 0.3,
        'metric_accuracy_training_num_layers': 3,    #  Number of layers with an 'accuracy_training' value
        'metric_loss_training_avg_over_layers': 123.0, 
        ...
    }
    """

    # Collect all metrics of similar type (e.g., the accuracy value of all categorical layer)    
    metric_values = collections.defaultdict(list)
    for summary in all_summaries:
        for metric, value in summary.items():
            metric_values[metric].append(value)

    aggregated_values = {}
    for metric, values in metric_values.items():
        aggregated_values['metric_' + metric + '_max_over_layers'] = float(np.max(values))
        aggregated_values['metric_' + metric + '_avg_over_layers'] = float(np.average(values))
        aggregated_values['metric_' + metric + '_min_over_layers'] = float(np.min(values))
        aggregated_values['metric_' + metric + '_num_layers'] = len(values)  # Number of layers with the given metric
        
    return aggregated_values
    
