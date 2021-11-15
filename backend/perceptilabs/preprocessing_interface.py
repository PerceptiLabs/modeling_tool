import os
import logging
import pandas as pd

import perceptilabs.settings as settings    
from perceptilabs.resources.files import FileAccess
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.resources.files import FileAccess
from perceptilabs.utils import KernelError
import perceptilabs.data.utils as data_utils
import perceptilabs.utils as utils


logger = logging.getLogger(__name__)


class PreprocessingSessionInterface:
    def __init__(self, results_access):
        self._results_access = results_access

    def run(self, dataset_settings_dict, preprocessing_session_id):
        try:        
            self._run_internal(dataset_settings_dict, preprocessing_session_id)
        except Exception as e:
            logger.exception("Exception in preprocessing session interface!")

            error = KernelError.from_exception(e, message="Error during preprocessing!")            
            self._results_access.set_results(
                preprocessing_session_id, 'failed', error=error.to_dict())

    def _run_internal(self, dataset_settings_dict, preprocessing_session_id):
        dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
        csv_file = utils.get_file_path(dataset_settings_dict)  # TODO. move one level up

        num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (anton.k): remove when frontend solution exists
        
        self._results_access.set_results(
            preprocessing_session_id, 'Initializing preprocessing...')
        
        file_access = FileAccess(os.path.dirname(csv_file))                            
        df = pd.read_csv(csv_file)
        df = data_utils.localize_file_based_features(df, dataset_settings, file_access)

        def on_status_updated(status, feature_name, total_steps, steps_completed, index=None, size=None):
            if index is not None and size:
                status_message =  f"Step {steps_completed}/{total_steps} for feature \'{feature_name}\': building {status} pipeline' [{index} / {size} samples processed]"
            else:
                status_message = f"Step {steps_completed}/{total_steps} for feature \'{feature_name}\': building {status} pipeline"
            
            self._results_access.set_results(preprocessing_session_id, status_message, metadata=None)

            
        metadata = DataLoader.compute_metadata(
            df,
            dataset_settings,
            num_repeats=num_repeats,
            on_status_updated=on_status_updated
        )
            
        self._results_access.set_results(
            preprocessing_session_id, 'complete', metadata=metadata)

