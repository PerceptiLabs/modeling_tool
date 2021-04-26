from perceptilabs.tracking.base import get_mixpanel, silence_exceptions
from perceptilabs.tracking.utils import get_layer_counts


@silence_exceptions
def send_training_started(user_email, model_id, graph_spec):
    payload = {
        'user_email': user_email,
        'model_id': model_id,
    }
    layer_counts = get_layer_counts(graph_spec)    
    payload.update(layer_counts)
    
    mp = get_mixpanel(user_email)
    mp.track(user_email, 'training-started', payload)

    
