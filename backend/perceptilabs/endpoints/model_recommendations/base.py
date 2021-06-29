import logging
from flask import request, jsonify
from flask.views import View

from perceptilabs.data.base import DataLoader
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.tracking as tracking
import perceptilabs.automation.utils as automation_utils


logger = logging.getLogger(APPLICATION_LOGGER)


class ModelRecommendations(View):
    def dispatch_request(self):
        """ Loads the data and invokes the model recommender to return a graph spec. Also triggers a MixPanel event """    
        json_data = request.get_json()
        
        response = None
        try:
            dataset_settings = json_data['datasetSettings']
            data_loader = DataLoader.from_dict(dataset_settings)
            
            graph_spec, training_settings = automation_utils.get_model_recommendation(data_loader)
            response = graph_spec.to_dict()
        except ValueError as e:
            return jsonify({"errorMessage": str(e)})            
        else:
            self._maybe_send_tracking(json_data, data_loader, graph_spec)
            return jsonify(response)

    def _maybe_send_tracking(self, json_data, data_loader, graph_spec):
        if 'user_email' in json_data:
            tracking.send_model_recommended(
                json_data.get('user_email'),
                json_data.get('model_id'),
                json_data.get('skipped_workspace'),
                data_loader.feature_specs,
                graph_spec,
                is_tutorial_data=data_loader.is_tutorial_data
            )
