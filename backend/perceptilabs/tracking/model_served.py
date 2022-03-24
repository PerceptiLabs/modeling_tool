from perceptilabs.tracking.utils import get_tool_version

def send_model_served(tracker, call_context, model_id):
    payload = {
        'deployment_type': 'serving',
        'model_id': model_id,
        'version': get_tool_version()
    }
    tracker.emit('model-exported', call_context, payload)  # TODO: we should probably rename the event to model-deployed...
