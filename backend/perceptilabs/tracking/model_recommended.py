from perceptilabs.tracking.base import get_mixpanel, silence_exceptions


@silence_exceptions
def send_model_recommended(user_email, model_id, skipped_workspace, graph_spec, is_tutorial_data):
    """ Sends a MixPanel event describing the model recommendation """
    payload = {
        'user_email': user_email,
        'model_id': model_id,
        'is_tutorial_data': is_tutorial_data,
        'skipped_workspace': skipped_workspace
    }

    def try_increment(key):
        try:
            payload[key] += 1
        except KeyError:
            payload[key] = 1    
    
    for layer_spec in graph_spec:
        if layer_spec.is_input_layer:
            try_increment('num_inputs_total')
            try_increment(f'num_inputs_{layer_spec.datatype}')                            
        elif layer_spec.is_output_layer:
            try_increment('num_outputs_total')
            try_increment(f'num_outputs_{layer_spec.datatype}')                            

    mp = get_mixpanel(user_email)
    mp.track(user_email, 'model-recommended', payload)     

    
