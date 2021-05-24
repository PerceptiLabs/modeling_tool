from perceptilabs.tracking.base import get_mixpanel, silence_exceptions
from perceptilabs.tracking.utils import get_layer_counts, get_preprocessing_counts, get_tool_version


@silence_exceptions
def send_model_recommended(
        user_email, model_id, skipped_workspace, feature_specs, graph_spec, is_tutorial_data
):
    """ Sends a MixPanel event describing the model recommendation """
    payload = {
        'user_email': user_email,
        'model_id': model_id,
        'is_tutorial_data': is_tutorial_data,
        'skipped_workspace': skipped_workspace,
        'version': get_tool_version()
    }
    layer_counts = get_layer_counts(graph_spec)    
    payload.update(layer_counts)

    preprocessing_counts = get_preprocessing_counts(feature_specs)    
    payload.update(preprocessing_counts)
    
    mp = get_mixpanel(user_email)
    mp.track(user_email, 'model-recommended', payload)     

    
