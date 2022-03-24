from perceptilabs.tracking.utils import get_layer_counts, get_tool_version

def send_testing_completed(tracker, call_context, model_id, test_name):
    payload = {
        'model_id': model_id,
        'test_name': test_name,
        'version': get_tool_version()
    }
    tracker.emit('testing-completed', call_context, payload)

