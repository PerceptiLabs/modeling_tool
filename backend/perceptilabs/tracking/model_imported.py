from perceptilabs.tracking.utils import get_tool_version

def send_model_imported(tracker, call_context, model_id):
    payload = {
        'deployment_type': 'importing',
        'model_id': model_id,
        'version': get_tool_version()
    }
    tracker.emit('model-imported', call_context, payload)
