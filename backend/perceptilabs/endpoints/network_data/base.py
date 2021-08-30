import logging
import numpy as np
from flask import request, jsonify
from flask.views import View

from perceptilabs.caching.utils import NullCache
from perceptilabs.endpoints.base_view import BaseView
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.lwcore import LightweightCore
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.tracking as tracking
import perceptilabs.automation.utils as automation_utils
from perceptilabs.createDataObject import subsample_data


logger = logging.getLogger(APPLICATION_LOGGER)


class NetworkData(BaseView):
    def __init__(self, data_metadata_cache=NullCache(), preview_cache=NullCache()):
        self._data_metadata_cache = data_metadata_cache
        self._preview_cache = preview_cache

    def dispatch_request(self):
        json_data = request.get_json()
        graph_spec = GraphSpec.from_dict(json_data['network'])
        data_loader = self._get_data_loader(json_data['datasetSettings'], json_data.get('userEmail'))

        lw_core = LightweightCore(data_loader=data_loader, cache=self._preview_cache)
        graph_spec, auto_updated_layers = self._maybe_apply_autosettings(graph_spec, settings_engine=None)

        dim_content, preview_content, trained_layers_info, subsample_data_info = {}, {}, {}, {}
        lw_results = lw_core.run(graph_spec)
        total_num_layer_components = 0
        total_data_points = 0

        for layer_id, layer_results in lw_results.items():
            layer_spec = graph_spec[layer_id]
            dimensions, preview, layer_data_points = self._get_layer_content(layer_spec, layer_results, auto_updated_layers)
            trained_layers_info[layer_id] = layer_results.trained
            dim_content[layer_id] = dimensions

            if preview is not None:
                subsample_data_info[layer_id] = preview

            if layer_data_points:
                total_data_points += layer_data_points

            total_num_layer_components += 1

        preview_content = subsample_data(subsample_data_info, total_num_layer_components, total_data_points)

        output = {
            "previews": preview_content,  # TODO(anton.k): the best way to do this is probably to send file URLs w/ the images. That's a lot easier to debug. See: https://stackoverflow.com/questions/33279153/rest-api-file-ie-images-processing-best-practices
            "outputDims": dim_content,
            "newNetwork": graph_spec.to_dict() if auto_updated_layers else {},
            "trainedLayers": trained_layers_info
        }

        return output

    def _get_layer_content(self, layer_spec, layer_results, auto_updated_layers):
        sample = layer_results.sample.get(layer_spec.preview_variable)
        shape = np.atleast_1d(sample).shape if sample is not None else ()

        dim_str = "x".join(str(d) for d in shape)
        dim_content = {"Dim": dim_str}

        # Ignore errors for layers that are not fully configured
        if layer_spec.should_show_errors and layer_results.has_errors:
            error_type, error_info = list(layer_results.errors)[-1] # Get the last error
            dim_content['Error'] = {'Message': error_info.message, 'Row': error_info.line_number}
        else:
            dim_content['Error'] = None

        preview_content = None
        layer_sample_data_points = None

        if (layer_spec.get_preview or layer_spec.id_ in auto_updated_layers) and (not layer_results.has_errors):
            try:
                sample_array = np.asarray(sample)
                sample_layer_shape = sample_array.shape
                layer_sample_data_points = int(np.prod(sample_layer_shape))

                if layer_spec.type_ == 'DeepLearningConv':
                    sample_data = list()
                    if np.all(sample_array) != None:
                        for idx in range(sample_array.shape[-1]):
                            sample_data.append(sample_array[:,:,idx])
                else:
                    sample_data = [self._reduce_to_2d(sample_array).squeeze()]

                preview_content = {
                    'data': sample_data,
                    'data_shape': sample_layer_shape,
                    'data_points': layer_sample_data_points
                }

                if layer_spec.to_dict().get('previewVariable') == 'W' and len(sample_array.shape) >= 2:
                    preview_content['type_list'] = ['heatmap']

            except:
                logger.exception(f'Failed getting preview for layer {layer_spec}')

        return dim_content, preview_content, layer_sample_data_points

    def _maybe_apply_autosettings(self, graph_spec, settings_engine):
        if settings_engine is not None:
            new_graph_spec = settings_engine.run(graph_spec)

            if new_graph_spec is not None:
                return new_graph_spec, new_graph_spec.difference(graph_spec)
        else:
            logger.warning("Settings engine is not set. Cannot make recommendations. Using old json_network.")
        return graph_spec, set()

    def _try_fetch(self, dict_, variable):
        try:
            return dict_[variable]
        except:
            return ""

    def _reduce_to_2d(self, data):
        data_shape = np.shape(np.squeeze(data))

        is_scalar = len(data_shape) <= 1
        is_vector = len(data_shape) == 2
        is_image = len(data_shape) == 3 and (data_shape[-1] == 3 or data_shape[-1] == 1)

        if is_scalar or is_vector or is_image:
            return data
        else:
            return self._reduce_to_2d(data[..., -1])

