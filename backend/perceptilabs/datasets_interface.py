import os
import logging
import pandas as pd

from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.data.type_inference import TypeInferrer
from perceptilabs.utils import KernelError
import perceptilabs.tracking as tracking
import perceptilabs.utils as utils
import perceptilabs.data.utils as data_utils


logger = logging.getLogger(__name__)


class DatasetsInterface:
    def __init__(self, task_executor, event_tracker, results_access, dataset_access):
        self._task_executor = task_executor
        self._event_tracker = event_tracker
        self._results_access = results_access
        self._dataset_access = dataset_access


    def start_preprocessing(self, call_context, settings_dict, logrocket_url=''):
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        preprocessing_session_id = dataset_settings.compute_hash()

        self._task_executor.enqueue(
            'preprocessing_task',
            call_context,
            settings_dict,
            preprocessing_session_id,
            logrocket_url=logrocket_url
        )
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


    def infer_datatypes(self, call_context, dataset_id):
        try:
            df = self._dataset_access.get_dataframe(call_context, dataset_id)

            inferrer = TypeInferrer.with_default_settings()
            datatypes = inferrer.get_valid_and_default_datatypes_for_dataframe(df)

        except ValueError as e:
            raise KernelError.from_exception(
                e, message="Couldn't get data types because the Kernel responded with an error")
        else:
            if call_context.user_unique_id and dataset_id:
                is_plabs_sourced = self._dataset_access.is_perceptilabs_sourced(call_context, dataset_id)
                path = self._dataset_access.get_location(call_context, dataset_id)

                tracking.send_data_selected(
                    self._event_tracker,
                    call_context,
                    path,
                    is_plabs_sourced,
                    dataset_id)

            return datatypes


