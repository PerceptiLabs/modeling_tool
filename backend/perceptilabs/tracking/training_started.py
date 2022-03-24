from perceptilabs.tracking.utils import get_layer_counts, get_tool_version


def send_training_started(tracker, call_context, model_id, graph_spec):
    payload = {
        'model_id': model_id,
        'version': get_tool_version()
    }
    layer_counts = get_layer_counts(graph_spec)
    payload.update(layer_counts)

    tracker.emit('training-started', call_context, payload)
