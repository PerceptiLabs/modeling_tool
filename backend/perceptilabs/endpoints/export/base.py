import os
import logging

from flask import request, jsonify
from flask.views import View


from perceptilabs.graph.spec import GraphSpec
from perceptilabs.endpoints.base_view import BaseView
from perceptilabs.script import ScriptFactory
from perceptilabs.exporter.base import Exporter, CompatibilityError
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.epochs import EpochsAccess


logger = logging.getLogger(APPLICATION_LOGGER)


class Export(BaseView):
    script_factory = ScriptFactory()

    def __init__(self, model_access, epochs_access, data_metadata_cache=None):
        self._data_metadata_cache = data_metadata_cache
        self._model_access = model_access
        self._epochs_access = epochs_access

    def dispatch_request(self):
        """ Renders the code for a layer """
        json_data = request.get_json()
        checkpoint_directory = json_data['checkpointDirectory']

        if json_data['exportSettings']['Type'] != 'Checkpoint':
            if not self._epochs_access.has_saved_epoch(
                    checkpoint_directory, require_trainer_state=False):
                return jsonify("Cannot export an untrained model. Make sure to run training first.")

        try:
            export_settings = json_data['exportSettings']
            graph_spec = self._model_access.get_graph_spec(
                model_id=json_data['network']) #TODO: F/E should send an ID
            
            data_loader = self._get_data_loader(
                json_data['datasetSettings'], json_data.get('userEmail'))

            model_id = json_data.get('modelId')
            user_email = json_data.get('userEmail')

            epoch_id = self._epochs_access.get_latest(
                training_session_id=checkpoint_directory,  # TODO: Frontend needs to send ID
                require_checkpoint=True,
                require_trainer_state=False
            )

            checkpoint_path = self._epochs_access.get_checkpoint_path(
                training_session_id=checkpoint_directory,
                epoch_id=epoch_id
            )
            training_model = self._model_access.get_training_model(
                graph_spec.to_dict(),  # TODO. f/e should send an ID
                checkpoint_path=checkpoint_path
            )
            
            exporter = Exporter(
                graph_spec, training_model, data_loader, model_id=model_id, user_email=user_email)
            
            export_path = os.path.join(export_settings['Location'], export_settings['name'])
            mode = self._get_export_mode(export_settings)
            exporter.export(export_path, mode=mode)

        except CompatibilityError:
            return jsonify(f"Model not compatible.")
        except Exception as e:
            logging.exception("Model export failed")
            return jsonify(f"Model export failed")
        else:
            return jsonify(f"Model exported to '{export_path}'")

    def _get_export_mode(self, export_settings):
        type_ = export_settings['Type']
        if type_== 'TFModel':
            if export_settings['Compressed']:
                mode = 'Compressed'
            elif export_settings['Quantized']:
                mode = 'Quantized'
            else:
                mode = 'Standard'
        else:
            mode = type_
        return mode
