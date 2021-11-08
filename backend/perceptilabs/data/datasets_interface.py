import os
import logging
import pandas as pd

from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.resources.files import FileAccess
import perceptilabs.utils as utils
import perceptilabs.data.utils as data_utils


logger = logging.getLogger(APPLICATION_LOGGER)


class DatasetsInterface:
    def __init__(self, task_executor, results_access):
        self._task_executor = task_executor
        self._results_access = results_access
        
    def start_preprocessing(self, settings_dict, user_email):
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        preprocessing_session_id = dataset_settings.compute_hash()
        
        self._task_executor.enqueue(
            'preprocessing_task', settings_dict, preprocessing_session_id)

        return preprocessing_session_id
    
    def get_preprocessing_status(self, preprocessing_session_id):
        results = self._results_access.get_results(preprocessing_session_id)

        status_message = results.get('status') if results else None
        is_present = status_message is not None
        is_complete = status_message == 'complete'        
        error = results.get('error') if results else None        
        
        if status_message is None:
            status_message = 'Waiting for data...'

        return status_message, is_present, is_complete, error
