from perceptilabs.tracking.utils import get_tool_version


def send_model_exported(call_context, tracker, model_id):
    payload = {
        'deployment_type': 'export',
        'user_email': call_context.get('user_email'),
        'model_id': model_id,
        'version': get_tool_version()
    }
    tracker.emit('model-exported', call_context.get('user_email'), payload)

