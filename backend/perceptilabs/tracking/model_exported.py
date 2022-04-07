from perceptilabs.tracking.utils import get_tool_version


def send_model_exported(tracker, call_context, model_id):
    payload = {
        "deployment_type": "export",
        "model_id": model_id,
        "version": get_tool_version(),
    }
    tracker.emit("model-exported", call_context, payload)
