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
    def __init__(self, executor, results_access):
        self._executor = executor
        self._results_access = results_access
        
    def start_wrangling(self, settings_dict, user_email):
        num_repeats = utils.get_num_data_repeats(settings_dict)
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        csv_file = settings_dict['filePath']  # TODO. move one level up

        session_id = dataset_settings.compute_hash()
        self._results_access.set_results(
            session_id, 'Initializing preprocessing...')
        
        def on_status_updated(status, feature_name, total_steps, steps_completed, index=None, size=None):
            if index is not None and size:
                status_message =  f"Step {steps_completed}/{total_steps} for feature \'{feature_name}\': building {status} pipeline' [{index} / {size} samples processed]"
            else:
                status_message = f"Step {steps_completed}/{total_steps} for feature \'{feature_name}\': building {status} pipeline"
                
            self._results_access.set_results(session_id, status_message, metadata=None)
            
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
                
                dataset_hash = self._results_access.set_results(
                    session_id, 'complete', metadata=metadata)
            except:
                logger.exception("Exception while computing metadata")
                raise

            logger.info(f"Inserted metadata with hash '{dataset_hash}'")

        _ = self._executor.submit(on_submit, csv_file, dataset_settings)
        return session_id
    
    def get_wrangling_status(self, session_id):
        status_message = self._results_access.get_status(session_id)
        is_present = status_message is not None
        is_complete = status_message == 'complete'        

        if status_message is None:
            status_message = 'Waiting for data...'

        return status_message, is_present, is_complete
