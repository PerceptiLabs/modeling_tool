from perceptilabs.tracking.utils import get_tool_version

def send_model_served(tracker, user_email, model_id):
    payload = {
        'deployment_type': 'serving',
        'user_email': user_email,
        'model_id': model_id,
        'version': get_tool_version()        
    }
    tracker.emit('model-exported', user_email, payload)  # TODO: we should probably rename the event to model-deployed...
    

    

    
