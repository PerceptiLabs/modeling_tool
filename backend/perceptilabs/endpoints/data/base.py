from flask import request, jsonify, make_response
from flask.views import View
import pandas as pd
import logging

from perceptilabs.caching.utils import NullCache
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.utils as utils

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

        dataset_key = ['pipelines', user_email, dataset_settings.compute_hash()]

        def on_submit(dataset_settings):
            df = pd.read_csv(dataset_settings.file_path)
            metadata = DataLoader.compute_metadata(
                df,
                dataset_settings,
                num_repeats=num_repeats)

            dataset_hash = self._data_metadata_cache.put(dataset_key, metadata)

            logger.info(f"Inserted metadata with hash '{dataset_hash}'")
            return dataset_hash

        future = self._executor.submit(on_submit, dataset_settings)
        dataset_hash = future.result()

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

