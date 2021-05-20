from perceptilabs.tracking.base import get_mixpanel, silence_exceptions
from perceptilabs.tracking.utils import get_tool_version


@silence_exceptions
def send_model_exported(user_email, model_id):
    payload = {
        'user_email': user_email,
        'model_id': model_id,
        'version': get_tool_version()        
    }
    mp = get_mixpanel(user_email)
    mp.track(user_email, 'model-exported', payload)     

    

    
