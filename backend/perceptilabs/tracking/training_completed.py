from perceptilabs.tracking.base import get_mixpanel, silence_exceptions
from perceptilabs.tracking.utils import get_layer_counts, aggregate_summaries, get_tool_version

@silence_exceptions
def send_training_completed(
        user_email, model_id, graph_spec, training_duration, 
        dataset_size, sample_size, num_iters_completed, num_epochs_completed,
        batch_size, data_units_iter_based, data_units_epoch_based,
        model_params, trainable_params,
        peak_memory_percentage, all_output_summaries
):
    payload = {
        'user_email': user_email,
        'model_id': model_id,
        'dataset_size_bytes': dataset_size,
        'sample_size': sample_size,
        'num_iters_completed': num_iters_completed,
        'num_epochs_completed': num_epochs_completed,
        'batch_size': batch_size,
        'data_units_iter_based': data_units_iter_based,
        'data_units_epoch_based': data_units_epoch_based,
        'model_params': model_params,
        'trainable_params': trainable_params,
        'training_duration': training_duration,
        'peak_memory_percentage': peak_memory_percentage,
        'version': get_tool_version()                
    }
    layer_counts = get_layer_counts(graph_spec)    
    payload.update(layer_counts)

    aggregated_metrics = aggregate_summaries(all_output_summaries)
    payload.update(aggregated_metrics)
    
    mp = get_mixpanel(user_email)
    mp.track(user_email, 'training-completed', payload)

    
