from flask import request, jsonify, make_response
from flask.views import View
import pandas as pd
import logging

from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class PutData(View):
    def __init__(self, executor, data_metadata_cache=None):
        self._executor = executor
        self._data_metadata_cache = data_metadata_cache

    def dispatch_request(self):
        json_data = request.get_json()        
        dataset_settings = DatasetSettings.from_dict(json_data['datasetSettings'])        
        dataset_hash = dataset_settings.compute_hash()
        
        def on_submit(dataset_settings, metadata_cache):
            df = pd.read_csv(dataset_settings.file_path)            
            metadata = DataLoader.compute_metadata(df, dataset_settings)

            metadata_cache[dataset_hash] = metadata
            logger.info(f"Inserted metadata with hash '{dataset_hash}'")            

        if self._data_metadata_cache is not None:
            self._executor.submit(on_submit, dataset_settings, self._data_metadata_cache)
        else:
            logger.warning("Metadata cache not set! Metadata wont be computed")

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



    
