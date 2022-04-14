import logging
import functools
from abc import ABC, abstractmethod

from perceptilabs.call_context import CallContext
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.utils import setup_sentry, send_ex_to_sentry
from perceptilabs.data.resolvers import DataFrameResolver


logger = logging.getLogger(__name__)


def handle_exceptions(function):
    @functools.wraps(function)
    def func(call_context_dict, *args, **kwargs):
        call_context = CallContext(call_context_dict)
        try:
            setup_sentry()  # Ensures sentry is configured in a multiprocessing environment
            return function(call_context, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Exception in task: {function.__name__}")
            send_ex_to_sentry(e, call_context)
            raise

    return func


class TaskExecutor(ABC):
    @abstractmethod
    def enqueue(self, task_name, *args, **kwargs):
        raise NotImplementedError


@handle_exceptions
def training_task(
    call_context,
    dataset_settings_dict,
    model_id,
    training_session_id,
    training_settings,
    load_checkpoint,
    is_retry=False,
    logrocket_url="",
    graph_settings=None,
):
    import perceptilabs.settings as settings
    from perceptilabs.training_interface import TrainingSessionInterface
    from perceptilabs.messaging.base import get_message_broker
    from perceptilabs.tracking.base import EventTracker
    from perceptilabs.caching.utils import get_data_metadata_cache
    from perceptilabs.script.base import ScriptFactory
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.training_results import TrainingResultsAccess
    from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess
    from perceptilabs.resources.tf_support_access import TensorflowSupportAccess
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    from perceptilabs.resources.datasets import DatasetAccess
    from perceptilabs.rygg import RyggWrapper
    import perceptilabs.utils as utils
    import os

    rygg = RyggWrapper.with_default_settings()
    message_broker = get_message_broker()

    model_access = ModelAccess(rygg)
    epochs_access = EpochsAccess(rygg)
    training_results_access = TrainingResultsAccess(rygg)
    preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())

    # TODO: all this data setup should be moved into the coreInteraface!!!

    dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
    data_metadata = preprocessing_results_access.get_metadata(
        dataset_settings.compute_hash()
    )

    dataset_access = DatasetAccess(rygg)

    tensorflow_support_access = TensorflowSupportAccess(
        rygg, enable_tf_gpu_memory_growth=settings.ENABLE_TF_GPU_MEMORY_GROWTH
    )

    df = dataset_access.get_dataframe(
        call_context,
        dataset_settings.dataset_id,
        fix_paths_for=dataset_settings.file_based_features,
    )

    df = DataFrameResolver.resolve_dataframe(df, dataset_settings_dict)

    data_loader = DataLoader(
        df,
        dataset_settings,
        metadata=data_metadata,
        num_repeats=dataset_settings.num_recommended_repeats,
    )
    event_tracker = EventTracker()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access,
        epochs_access,
        training_results_access,
        tensorflow_support_access,
    )

    interface.run(
        call_context,
        data_loader,
        model_id,
        training_session_id,
        training_settings,
        load_checkpoint,
        results_interval=settings.TRAINING_RESULTS_REFRESH_INTERVAL,
        is_retry=is_retry,
        logrocket_url=logrocket_url,
        graph_settings=graph_settings,
    )


@handle_exceptions
def testing_task(
    call_context,
    testing_session_id,
    models_info,
    tests,
    is_retry=False,
    logrocket_url="",
):
    import perceptilabs.settings as settings
    from perceptilabs.testing_interface import TestingSessionInterface
    from perceptilabs.messaging.base import get_message_broker
    from perceptilabs.caching.utils import get_data_metadata_cache
    from perceptilabs.script.base import ScriptFactory
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.testing_results import TestingResultsAccess
    from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess
    from perceptilabs.resources.tf_support_access import TensorflowSupportAccess
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    from perceptilabs.tracking.base import EventTracker
    from perceptilabs.resources.datasets import DatasetAccess
    from perceptilabs.rygg import RyggWrapper
    import perceptilabs.utils as utils
    import os

    rygg = RyggWrapper.with_default_settings()
    message_broker = get_message_broker()
    data_metadata_cache = get_data_metadata_cache().for_compound_keys()

    model_access = ModelAccess(rygg)
    epochs_access = EpochsAccess(rygg)
    testing_results_access = TestingResultsAccess()
    preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())

    dataset_access = DatasetAccess(rygg)
    tensorflow_support_access = TensorflowSupportAccess(
        rygg, enable_tf_gpu_memory_growth=settings.ENABLE_TF_GPU_MEMORY_GROWTH
    )

    event_tracker = EventTracker()
    interface = TestingSessionInterface(
        message_broker,
        event_tracker,
        dataset_access,
        model_access,
        epochs_access,
        testing_results_access,
        tensorflow_support_access,
        preprocessing_results_access,
    )

    interface.run(
        call_context,
        testing_session_id,
        models_info,
        tests,
        results_interval=settings.TESTING_RESULTS_REFRESH_INTERVAL,
        logrocket_url=logrocket_url,
    )


@handle_exceptions
def serving_task(
    call_context,
    serving_settings,
    dataset_settings_dict,
    model_id,
    training_session_id,
    model_name,
    serving_session_id,
    ttl,
    graph_settings=None,
    is_retry=False,
    logrocket_url="",
):
    import perceptilabs.settings as settings
    from perceptilabs.serving_interface import ServingSessionInterface
    from perceptilabs.caching.utils import get_data_metadata_cache
    from perceptilabs.script.base import ScriptFactory
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.model_archives import ModelArchivesAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.serving_results import ServingResultsAccess
    from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess
    from perceptilabs.resources.tf_support_access import TensorflowSupportAccess
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    from perceptilabs.messaging.base import get_message_broker
    from perceptilabs.tracking.base import EventTracker
    from perceptilabs.resources.datasets import DatasetAccess
    from perceptilabs.rygg import RyggWrapper
    import perceptilabs.utils as utils
    import os

    rygg = RyggWrapper.with_default_settings()
    message_broker = get_message_broker()
    data_metadata_cache = get_data_metadata_cache().for_compound_keys()

    model_access = ModelAccess(rygg)
    epochs_access = EpochsAccess(rygg)

    serving_results_access = ServingResultsAccess(rygg)
    preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())

    dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
    data_metadata = preprocessing_results_access.get_metadata(
        dataset_settings.compute_hash()
    )

    rygg = RyggWrapper.with_default_settings()

    dataset_access = DatasetAccess(rygg)
    tensorflow_support_access = TensorflowSupportAccess(
        rygg, enable_tf_gpu_memory_growth=settings.ENABLE_TF_GPU_MEMORY_GROWTH
    )

    df = dataset_access.get_dataframe(
        call_context,
        dataset_settings.dataset_id,
        fix_paths_for=dataset_settings.file_based_features,
    )

    df = DataFrameResolver.resolve_dataframe(df, dataset_settings_dict)

    data_loader = DataLoader(
        df,
        dataset_settings,
        metadata=data_metadata,
        num_repeats=dataset_settings.num_recommended_repeats,
    )

    event_tracker = EventTracker()
    model_archives_access = ModelArchivesAccess()

    interface = ServingSessionInterface(
        serving_settings,
        message_broker,
        event_tracker,
        model_access,
        model_archives_access,
        epochs_access,
        serving_results_access,
        tensorflow_support_access,
        ttl,
    )

    interface.run(
        call_context,
        data_loader,
        model_id,
        training_session_id,
        serving_session_id,
        model_name,
        results_interval=settings.SERVING_RESULTS_REFRESH_INTERVAL,
        is_retry=is_retry,
        logrocket_url=logrocket_url,
        graph_settings=graph_settings,
    )


@handle_exceptions
def preprocessing_task(
    call_context, dataset_settings_dict, preprocessing_session_id, logrocket_url=""
):
    from perceptilabs.preprocessing_interface import (
        PreprocessingSessionInterface,
    )  # TODO: should preprocessing_interface have a better name??
    from perceptilabs.messaging.base import get_message_broker
    from perceptilabs.caching.utils import get_data_metadata_cache
    from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess
    from perceptilabs.resources.datasets import DatasetAccess
    from perceptilabs.rygg import RyggWrapper

    rygg = RyggWrapper.with_default_settings()
    dataset_access = DatasetAccess(rygg)
    preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())
    interface = PreprocessingSessionInterface(
        dataset_access, preprocessing_results_access
    )

    interface.run(
        call_context,
        dataset_settings_dict,
        preprocessing_session_id,
        logrocket_url=logrocket_url,
    )
