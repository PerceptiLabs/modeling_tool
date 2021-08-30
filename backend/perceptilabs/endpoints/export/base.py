import os
import logging

from flask import request, jsonify
from flask.views import View


from perceptilabs.graph.spec import GraphSpec
from perceptilabs.endpoints.base_view import BaseView
from perceptilabs.script import ScriptFactory
from perceptilabs.exporter.base import Exporter, CompatibilityError
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.endpoints.utils as endpoints_utils

logger = logging.getLogger(APPLICATION_LOGGER)


class Export(BaseView):
    script_factory = ScriptFactory()

    def __init__(self, data_metadata_cache=None):
        self._data_metadata_cache = data_metadata_cache

    def dispatch_request(self):
        """ Renders the code for a layer """
        json_data = request.get_json()
        checkpoint_directory = json_data['checkpointDirectory']

        if json_data['exportSettings']['Type'] != 'Checkpoint':
            if not endpoints_utils.is_valid_checkpoint_directory(checkpoint_directory):
                return jsonify("Cannot export an untrained model. Make sure to run training first.")

        try:
            export_settings = json_data['exportSettings']
            graph_spec = GraphSpec.from_dict(json_data['network'])
            data_loader = self._get_data_loader(json_data['datasetSettings'], json_data.get('userEmail'))

            model_id = json_data.get('modelId')
            user_email = json_data.get('userEmail')

            exporter = Exporter.from_disk(
                checkpoint_directory, graph_spec, self.script_factory, data_loader,
                model_id=model_id, user_email=user_email
            )
            export_path = os.path.join(export_settings['Location'], export_settings['name'])
            exporter.export(export_path, export_settings['Type'])
            
        except CompatibilityError:
            return jsonify(f"Model not compatible.")            
        except:
            logging.exception("Model export failed")
            return jsonify(f"Model export failed")
        else:
            return jsonify(f"Model exported to '{export_path}'")            
