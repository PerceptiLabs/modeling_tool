import os

from perceptilabs.tracking.base import get_mixpanel, silence_exceptions
from perceptilabs.data.utils import is_tutorial_data_file
from perceptilabs.tracking.utils import get_tool_version

@silence_exceptions
def send_data_selected(user_email, file_path):
    """ Sends an event to MixPanel whenever the user selects a data file """
    _, file_ext = os.path.splitext(file_path)
    
    payload = {
        'user_email': user_email,
        'file_path': file_path,
        'file_ext': file_ext,    
        'is_tutorial_data': is_tutorial_data_file(file_path),
        'version': get_tool_version()                
    }
    mp = get_mixpanel(user_email)
    mp.track(user_email, 'data-selected', payload)     

    
