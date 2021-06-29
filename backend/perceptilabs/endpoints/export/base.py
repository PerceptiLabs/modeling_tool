import os
import logging

from flask import request, jsonify
from flask.views import View


from perceptilabs.graph.spec import GraphSpec
from perceptilabs.data.base import DataLoader
from perceptilabs.script import ScriptFactory
from perceptilabs.exporter.base import Exporter
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.endpoints.utils as endpoints_utils

logger = logging.getLogger(APPLICATION_LOGGER)


class Export(View):
    script_factory = ScriptFactory()
    
    def dispatch_request(self):
        """ Renders the code for a layer """
        json_data = request.get_json()
        checkpoint_directory = json_data['checkpointDirectory']

        if not endpoints_utils.is_valid_checkpoint_directory(checkpoint_directory):
            return jsonify("Cannot export an untrained model. Make sure to run training first.")
        
        try:
            export_settings = json_data['exportSettings']
            graph_spec = GraphSpec.from_dict(json_data['network'])
            data_loader = DataLoader.from_dict(json_data['datasetSettings'])
            
            model_id = json_data.get('modelId')
            user_email = json_data.get('userEmail')        
            
            exporter = Exporter.from_disk(
                checkpoint_directory, graph_spec, self.script_factory, data_loader,
                model_id=model_id, user_email=user_email
            )

            export_path = os.path.join(export_settings['Location'], export_settings['name'])
            exporter.export_inference(export_path)

            return jsonify(f"Model exported to '{export_path}'")
        except:
            logging.exception("Model export failed")
            return jsonify(f"Model export failed")            
