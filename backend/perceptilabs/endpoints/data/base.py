import os
from flask import request, jsonify, make_response
from flask.views import View
import pandas as pd
import logging

from perceptilabs.caching.utils import NullCache
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.resources.files import FileAccess
import perceptilabs.utils as utils
import perceptilabs.data.utils as data_utils            

logger = logging.getLogger(APPLICATION_LOGGER)


# TODO: move to general api file....

class PutData(View):
    def __init__(self, datasets_interface):
        self._datasets_interface = datasets_interface
    
    def dispatch_request(self):
        json_data = request.get_json()
        settings_dict = json_data['datasetSettings']
        user_email = json_data.get('userEmail')

        session_id = self._datasets_interface.start_preprocessing(
            settings_dict, user_email)

        return jsonify({"preprocessingSessionId": session_id})


class IsDataReady(View):
    def __init__(self, datasets_interface):
        self._datasets_interface = datasets_interface

    def dispatch_request(self):
        message, is_present, is_complete, error = self._datasets_interface.get_preprocessing_status(
            request.args['preprocessing_session_id'])

        if is_present:
            response = {
                'message': f"Build status: '{message}'",
                'is_complete': is_complete,
                'error': error
            }
        
            return jsonify(response)
        else:
            return make_response('', 204)
        

