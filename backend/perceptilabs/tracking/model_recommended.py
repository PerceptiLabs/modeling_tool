from perceptilabs.tracking.utils import (
    get_layer_counts,
    get_preprocessing_counts,
    get_tool_version,
)


def send_model_recommended(
    tracker,
    call_context,
    model_id,
    skipped_workspace,
    dataset_settings_dict,
    dataset_size_bytes,
    graph_spec,
    is_perceptilabs_sourced,
    dataset_id,
    target_type,
):
    """Sends a MixPanel event describing the model recommendation"""
    payload = {
        "model_id": model_id,
        "dataset_size_bytes": dataset_size_bytes,
        "is_perceptilabs_sourced": is_perceptilabs_sourced,
        "dataset_id": dataset_id,
        "skipped_workspace": skipped_workspace,
        "version": get_tool_version(),
        "target_type": target_type,
    }
    layer_counts = get_layer_counts(graph_spec)
    payload.update(layer_counts)

    preprocessing_counts = get_preprocessing_counts(dataset_settings_dict)
    payload.update(preprocessing_counts)

    tracker.emit("model-recommended", call_context, payload)
