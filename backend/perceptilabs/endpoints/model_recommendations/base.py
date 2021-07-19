import logging
from flask import request, jsonify
from flask.views import View

from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.tracking as tracking
import perceptilabs.automation.utils as automation_utils


logger = logging.getLogger(APPLICATION_LOGGER)


class ModelRecommendations(View):
    def __init__(self, data_metadata_cache=None):
        self._data_metadata_cache = data_metadata_cache
    
    def dispatch_request(self):
        """ Loads the data and invokes the model recommender to return a graph spec. Also triggers a MixPanel event """    
        json_data = request.get_json()
        
        response = None
        try:
            dataset_settings = DatasetSettings.from_dict(json_data['datasetSettings'])
            data_metadata = self._data_metadata_cache.get(dataset_settings.compute_hash()) if self._data_metadata_cache else None 
            data_loader = DataLoader.from_settings(dataset_settings, metadata=data_metadata)
            
            graph_spec, training_settings = automation_utils.get_model_recommendation(data_loader)
            response = graph_spec.to_dict()
        except ValueError as e:
            return jsonify({"errorMessage": str(e)})            
        else:
            self._maybe_send_tracking(json_data, data_loader, graph_spec, json_data['datasetSettings'])
            return jsonify(response)

    def _maybe_send_tracking(self, json_data, data_loader, graph_spec, settings_dict):
        if 'user_email' in json_data:
            tracking.send_model_recommended(
                json_data.get('user_email'),
                json_data.get('model_id'),
                json_data.get('skipped_workspace'),
                settings_dict,
                graph_spec,
                is_tutorial_data=data_loader.is_tutorial_data
            )
