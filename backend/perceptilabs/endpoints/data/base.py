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
        
        dataset_key = ['pipelines', user_email, csv_file, dataset_settings.compute_hash()]

        def on_submit(csv_file, dataset_settings):
            try:
                file_access = FileAccess(os.path.dirname(csv_file))                            

                df = pd.read_csv(csv_file)
                df = data_utils.localize_file_based_features(df, dataset_settings, file_access)
            
                metadata = DataLoader.compute_metadata(
                    df,
                    dataset_settings,
                    num_repeats=num_repeats
                )
                
                self._data_metadata_cache.put(dataset_key, metadata)
            except:
                logger.exception("Exception while computing metadata")
                raise

            logger.info(f"Inserted metadata with hash '{dataset_hash}'")
            return dataset_hash

        future = self._executor.submit(on_submit, csv_file, dataset_settings)
        dataset_hash = self._data_metadata_cache.make_key(dataset_key)

        return jsonify({"datasetHash": dataset_hash})


class IsDataReady(View):
    def __init__(self, data_metadata_cache=None):
        self._data_metadata_cache = data_metadata_cache

    def dispatch_request(self):
        dataset_hash = request.args['dataset_hash']

        if dataset_hash in self._data_metadata_cache:
            logger.info(f"Found metadata with hash '{dataset_hash}'")
            return jsonify({"is_ready": "true"})
        else:
            return make_response('', 204)

