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

class PutData(View):
    def __init__(self, executor, data_metadata_cache=NullCache()):
        self._executor = executor
        self._data_metadata_cache = data_metadata_cache.for_compound_keys()
        

    def dispatch_request(self):
        json_data = request.get_json()
        settings_dict = json_data['datasetSettings']
        user_email = json_data.get('userEmail')

        num_repeats = utils.get_num_data_repeats(settings_dict)
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        csv_file = settings_dict['filePath']  # TODO. move one level up
        
        dataset_key = ['pipelines', user_email, dataset_settings.compute_hash()]
        dataset_hash = self._data_metadata_cache.make_key(dataset_key)

        def on_status_updated(status, feature_name, total_steps, steps_completed):
            build_message =  f"Step {steps_completed}/{total_steps}: building {status} pipeline for feature \'{feature_name}\'"
            _ = self._data_metadata_cache.put(dataset_key, {'metadata': None, 'status': build_message})
        
        
        def on_submit(csv_file, dataset_settings):
            try:
                file_access = FileAccess(os.path.dirname(csv_file))                            

                df = pd.read_csv(csv_file)
                df = data_utils.localize_file_based_features(df, dataset_settings, file_access)
                metadata = DataLoader.compute_metadata(
                    df,
                    dataset_settings,
                    num_repeats=num_repeats,
                    on_status_updated=on_status_updated)
                dataset_hash = self._data_metadata_cache.put(dataset_key, {'metadata':metadata, 'status': 'complete'})
            except:
                logger.exception("Exception while computing metadata")
                raise

            logger.info(f"Inserted metadata with hash '{dataset_hash}'")


        _ = self._executor.submit(on_submit, csv_file, dataset_settings)

        return jsonify({"datasetHash": dataset_hash})


class IsDataReady(View):
    def __init__(self, data_metadata_cache=None):
        self._data_metadata_cache = data_metadata_cache

    def dispatch_request(self):
        dataset_hash = request.args['dataset_hash']
        metadata = self._data_metadata_cache.get(dataset_hash)
        if metadata is not None:
            message = metadata['status'] 
        else: 
            message = 'Initializing preprocessing.'

        if dataset_hash in self._data_metadata_cache:

            logger.info(f"Found metadata with hash '{dataset_hash}'")
            is_complete = 'complete' in message
            response = {
                'message': f"Build status: '{message}'",
                'is_complete': is_complete 
            }
            return jsonify(response)
        else:
            return make_response('', 204)

