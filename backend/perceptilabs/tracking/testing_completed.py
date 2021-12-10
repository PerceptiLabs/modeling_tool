from perceptilabs.tracking.utils import get_layer_counts, get_tool_version

def send_testing_completed(tracker, user_email, model_id, test_name):
    payload = {
        'user_email': user_email,
        'model_id': model_id,
        'test_name': test_name,
        'version': get_tool_version()                
    }
    tracker.emit('testing-completed', user_email, payload)     

