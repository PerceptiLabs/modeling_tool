from perceptilabs.tracking.base import get_mixpanel, silence_exceptions
from perceptilabs.tracking.utils import get_layer_counts


@silence_exceptions
def send_training_completed(
        user_email, model_id, graph_spec, training_duration, 
        final_loss_training, final_loss_validation, peak_memory_percentage
):
    payload = {
        'user_email': user_email,
        'model_id': model_id,
        'training_duration': training_duration,
        'peak_memory_percentage': peak_memory_percentage
    }
    layer_counts = get_layer_counts(graph_spec)    
    payload.update(layer_counts)
    
    mp = get_mixpanel(user_email)
    mp.track(user_email, 'training-completed', payload)

    
