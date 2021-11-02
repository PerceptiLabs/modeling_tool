import logging
import sentry_sdk
import sys
from flask import request, jsonify

from perceptilabs.endpoints.base_view import BaseView
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.utils import KernelError
import perceptilabs.tracking as tracking
import perceptilabs.automation.utils as automation_utils
import perceptilabs.utils as utils
import perceptilabs.data.utils as data_utils


logger = logging.getLogger(APPLICATION_LOGGER)

class ModelRecommendations(BaseView):
    def __init__(self, data_metadata_cache=None):
        self._data_metadata_cache = data_metadata_cache

    def dispatch_request(self):
        """ Loads the data and invokes the model recommender to return a graph spec. Also triggers a MixPanel event """    
        json_data = request.get_json()
        
        response = None
        try:
            data_loader = self._get_data_loader(json_data['datasetSettings'], json_data.get('userEmail'))            
            graph_spec, training_settings = automation_utils.get_model_recommendation(data_loader)
            response = graph_spec.to_dict()
        except Exception as e:
            raise KernelError.from_exception(e, message="Couldn't get model recommendations because the Kernel responded with an error")
        
        else:
            self._maybe_send_tracking(json_data, data_loader, graph_spec, json_data['datasetSettings'])
            return jsonify(response)

    def _maybe_send_tracking(self, json_data, data_loader, graph_spec, settings_dict):
        if 'user_email' in json_data:
            is_tutorial_data = data_utils.is_tutorial_data_file(json_data['datasetSettings']['filePath'])
            training_size = data_loader.get_dataset_size(partition='training')
            validation_size = data_loader.get_dataset_size(partition='validation')
            test_size = data_loader.get_dataset_size(partition='test')
            sample_size_bytes = sys.getsizeof(data_loader.get_sample(partition='training'))
            dataset_size_bytes = (training_size + validation_size + test_size) * sample_size_bytes

            tracking.send_model_recommended(
                json_data.get('user_email'),
                json_data.get('model_id'),
                json_data.get('skipped_workspace'),
                settings_dict,
                dataset_size_bytes,
                graph_spec,
                is_tutorial_data=is_tutorial_data
            )
