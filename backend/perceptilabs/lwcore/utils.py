import traceback
import re

from perceptilabs.issues import UserlandError


def format_exception(exception, adjust_by_offset=None):
    """Format an exception with shifted line numbers due to imports and other not-shown stuff"""
    pattern = '  File "<rendered-code.*, line ([0-9]*), in .*'

    tb_obj = traceback.TracebackException(
        exception.__class__, exception, exception.__traceback__
    )

    def adjust_line_num(match):
        """Decreases the line number in a traceback string. Assumes that the line string is in the first match."""
        i1, i2 = match.regs[1]
        line_number = int(match.string[i1:i2]) - adjust_by_offset
        new_string = match.string[0:i1] + str(line_number) + match.string[i2:]
        return new_string

    message = ""
    for counter, line in enumerate(tb_obj.format()):
        if adjust_by_offset is None:
            message += line
        else:
            # The code shown to the user does not include the import statements (and the optional preamble)
            # Therefore, we decrease the traceback line by an offset
            message += re.sub(pattern, adjust_line_num, line)

    return message


def exception_to_error(layer_id, layer_type, exception, line_offset=None):
    tb_obj = traceback.TracebackException(
        exception.__class__, exception, exception.__traceback__
    )

    # Get the line number of the last frame of rendered code
    line_no = None
    last_rendered_is_another_layer = True

    for frame in tb_obj.stack:
        if frame.filename.startswith(f"<rendered-code: "):
            line_no = int(frame.lineno)
            last_rendered_is_another_layer = not frame.filename.startswith(
                f"<rendered-code: {layer_id}"
            )

    if last_rendered_is_another_layer:
        # If the origin of the layer is _another_ rendered layer, then we will not raise an error here.
        # Example: A Dense layer has an error that propagates to the training layer.
        return None

    # The executed code is different from the code seen by the user (e.g., imports are not shown).
    # Subtract the unseen part to make sure the error is pointed at the correct line
    if line_no is not None and line_offset is not None:
        line_no -= line_offset

    message = format_exception(exception, adjust_by_offset=line_offset)
    error = UserlandError(layer_id, layer_type, line_no, message)
    return error


""" Contains old preview stuff broken out from the old Flask view. All of this should be refactored ASAP! """

import numpy as np

from perceptilabs.createDataObject import create_data_object, MAX_DATA_POINTS
from perceptilabs.layers.deeplearningconv.stats import ConvPreviewStats
from perceptilabs.layers.unet.stats import UnetPreviewStats
from perceptilabs.layers.iooutput.stats.mask import MaskPreviewStats
from perceptilabs.stats.base import PreviewStats
from perceptilabs.utils import KernelError


def _get_input_shape(layer_spec, lw_results):
    shape_str = ""  # Default
    if len(layer_spec.backward_connections) > 0:
        conn = layer_spec.backward_connections[0]
        input_results = lw_results.get(conn.src_id).sample
        if input_results is not None:
            sample = input_results.get(conn.src_var)
            shape = np.squeeze(sample.shape).tolist() if sample is not None else []
            shape_str = str(shape)

    return shape_str


def _get_layer_content(layer_spec, lw_results, skip_previews=False):
    layer_results = lw_results[layer_spec.id_]
    sample = layer_results.sample.get("output")
    shape = np.atleast_1d(sample).shape if sample is not None else ()

    output_shape_str = "x".join(str(d) for d in shape)

    # Ignore errors for layers that are not fully configured
    if layer_spec.should_show_errors and layer_results.has_errors:
        error_type, error_info = list(layer_results.errors)[-1]  # Get the last error
        error = {"Message": error_info.message, "Row": error_info.line_number}
    else:
        error = None

    preview_content = None
    layer_sample_data_points = None

    def get_stats_object(layer_spec):
        if layer_spec.type_ == "DeepLearningConv":
            return ConvPreviewStats()
        elif layer_spec.type_ == "UNet":
            return UnetPreviewStats()
        elif layer_spec.type_ == "IoOutput" and layer_spec.datatype == "mask":
            return MaskPreviewStats()
        else:
            return PreviewStats()

    if (error is None) and (not layer_results.has_errors) and (not skip_previews):
        try:
            stats_obj = get_stats_object(layer_spec)
            sample_data, sample_layer_shape, type_list = stats_obj.get_preview_content(
                sample
            )

            preview_content = {
                "data": sample_data,
                "data_shape": sample_layer_shape,
                "data_points": layer_sample_data_points,
                "type_list": type_list,
            }

        except Exception as e:
            raise KernelError.from_exception(
                e, message=f"Failed getting preview for layer {layer_spec}"
            )

    input_shape_str = _get_input_shape(layer_spec, lw_results)

    content = {"inShape": input_shape_str, "outShape": output_shape_str, "Error": error}

    if not skip_previews:
        content["dim_content"] = {"Dim": output_shape_str, "Error": error}
        content["preview"] = preview_content

    return content


def get_network_data(graph_spec, lw_results, skip_previews=False):
    content = {}
    for layer_id, layer_results in lw_results.items():
        layer_spec = graph_spec[layer_id]
        content[layer_id] = _get_layer_content(
            layer_spec, lw_results, skip_previews=skip_previews
        )

    return content


def _subsample_data(subsample_data_info, total_num_layer_components, total_data_points):
    """Given total data points, subsample each layer component equally according to max threshold

    Args:
       subsample_data_info (dict): Dictionary containing layer information
       total_num_layer_components (int): Total number of layer components on the modeling view
       total_data_points (int): Total number of data points across all layers

    Return:
       preview_content (dict): Dictionary of data objects
    """

    preview_content = {}
    ratio = None

    if total_data_points <= MAX_DATA_POINTS:
        ratio = 1
    else:
        ratio = round(total_data_points / MAX_DATA_POINTS)

    for layer_id, preview in subsample_data_info.items():
        sample_data = preview.get("data", None)
        type_list = preview.get("type_list", None)
        preview_content[layer_id] = create_data_object(
            sample_data, type_list=type_list, subsample_ratio=ratio
        )

    return preview_content


def format_content(content):
    total_num_layer_components = 0
    total_data_points = 0

    dim_content, subsample_data_info = {}, {}
    for layer_id in content:
        dim_content[layer_id] = content[layer_id]["dim_content"]
        preview = content[layer_id]["preview"]

        if preview is not None:
            subsample_data_info[layer_id] = preview

            total_data_points += int(np.prod(preview["data_shape"]))
            total_num_layer_components += 1

    preview_content = _subsample_data(
        subsample_data_info, total_num_layer_components, total_data_points
    )
    return preview_content, dim_content
