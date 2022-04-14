import os
import logging

import pandas as pd

import perceptilabs.settings as settings
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.utils import KernelError
import perceptilabs.data.utils as data_utils
import perceptilabs.utils as utils
from perceptilabs.data.resolvers import DataFrameResolver

logger = logging.getLogger(__name__)


class PreprocessingSessionInterface:
    def __init__(self, dataset_access, results_access):
        self._dataset_access = dataset_access
        self._results_access = results_access

    def run(
        self,
        call_context,
        dataset_settings_dict,
        preprocessing_session_id,
        logrocket_url="",
    ):
        try:
            self._run_internal(
                call_context, dataset_settings_dict, preprocessing_session_id
            )
        except Exception as e:
            logger.exception("Exception in preprocessing session interface!")

            error = KernelError.from_exception(e, message="Error during preprocessing!")
            self._results_access.set_results(
                preprocessing_session_id, "failed", error=error.to_dict()
            )

            call_context = call_context.push(
                preprocessing_session_id=preprocessing_session_id,
                dataset_settings_dict=dataset_settings_dict,
                logrocket_url=logrocket_url,
            )
            utils.send_ex_to_sentry(e, call_context)

    def _run_internal(
        self, call_context, dataset_settings_dict, preprocessing_session_id
    ):
        dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)

        self._results_access.set_results(
            preprocessing_session_id, "Initializing preprocessing..."
        )

        df = self._dataset_access.get_dataframe(
            call_context,
            dataset_settings.dataset_id,
            fix_paths_for=dataset_settings.file_based_features,
        )

        df = DataFrameResolver.resolve_dataframe(df, dataset_settings_dict)

        if df is None:
            raise ValueError("Invalid dataframe!")

        def on_status_updated(
            status, feature_name, total_steps, steps_completed, index=None, size=None
        ):
            if index is not None and size:
                status_message = f"Step {steps_completed}/{total_steps} for feature '{feature_name}': building {status} pipeline' [{index} / {size} samples processed]"
            else:
                status_message = f"Step {steps_completed}/{total_steps} for feature '{feature_name}': building {status} pipeline"

            self._results_access.set_results(
                preprocessing_session_id, status_message, metadata=None
            )

        metadata = DataLoader.compute_metadata(
            df,
            dataset_settings,
            num_repeats=dataset_settings.num_recommended_repeats,
            on_status_updated=on_status_updated,
        )

        self._results_access.set_results(
            preprocessing_session_id, "complete", metadata=metadata
        )
