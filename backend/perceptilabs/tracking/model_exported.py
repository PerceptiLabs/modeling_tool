from perceptilabs.tracking.utils import get_tool_version


def send_model_exported(tracker, user_email, model_id):
    payload = {
        'deployment_type': 'export',        
        'user_email': user_email,
        'model_id': model_id,
        'version': get_tool_version()        
    }
    tracker.emit('model-exported', user_email, payload)     


    

    
