from perceptilabs.tracking.base import get_mixpanel, silence_exceptions


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

    def try_increment(key):
        try:
            payload[key] += 1
        except KeyError:
            payload[key] = 1    
    
    for layer_spec in graph_spec:
        try_increment('num_layers_total')
        try_increment(f'num_layers_{layer_spec.type_}')                            

    mp = get_mixpanel(user_email)
    mp.track(user_email, 'training-completed', payload)

    
