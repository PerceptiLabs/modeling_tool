import os
from perceptilabs.tracking.utils import get_tool_version

def send_data_selected(tracker, user_email, file_path, is_plabs_sourced, dataset_id):
    """ Sends an event to MixPanel whenever the user selects a data file """
    _, file_ext = os.path.splitext(file_path)
    dataset_size_bytes = os.path.getsize(file_path)
    
    payload = {
        'user_email': user_email,
        'file_size_bytes': dataset_size_bytes,
        'file_path': file_path,
        'file_ext': file_ext,    
        'is_perceptilabs_sourced': is_plabs_sourced,
        'dataset_id': dataset_id,
        'version': get_tool_version()                
    }
    tracker.emit('data-selected', user_email, payload)     

    
