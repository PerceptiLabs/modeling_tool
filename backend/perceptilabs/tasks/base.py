import logging
import functools
from abc import ABC, abstractmethod
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


def log_exceptions(function):
    @functools.wraps(function)
    def func(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logger.exception("Exception in task")
            raise
    return func


class TaskExecutor(ABC):
    @abstractmethod
    def enqueue(self, task_name, *args, **kwargs):    
        raise NotImplementedError
    

@log_exceptions    
def training_task(dataset_settings_dict, graph_spec_dict, training_session_id, training_settings, load_checkpoint, user_email, is_retry=False):
    
    import perceptilabs.settings as settings    
    from perceptilabs.coreInterface import TrainingSessionInterface
    from perceptilabs.messaging.base import get_message_broker
    from perceptilabs.caching.utils import get_data_metadata_cache    
    from perceptilabs.script.base import ScriptFactory    
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.files import FileAccess
    from perceptilabs.resources.training_results import TrainingResultsAccess
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    import perceptilabs.utils as utils
    import os

    message_broker = get_message_broker()
    data_metadata_cache = get_data_metadata_cache().for_compound_keys()
    
    model_access = ModelAccess(ScriptFactory())
    epochs_access = EpochsAccess()
    results_access = TrainingResultsAccess()        

    csv_file = dataset_settings_dict['filePath']  # TODO: move one level up        
    num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (anton.k): remove when frontend solution exists

    dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
    key = ['pipelines', user_email, csv_file, dataset_settings.compute_hash()]
    data_metadata = data_metadata_cache.get(key)

    file_access = FileAccess(os.path.dirname(csv_file))        
    data_loader = DataLoader.from_csv(
        file_access,
        csv_file,
        dataset_settings,
        num_repeats=num_repeats,
        metadata=data_metadata
    )
    
    interface = TrainingSessionInterface(
        message_broker, model_access, epochs_access, results_access)

    interface.run(
        data_loader,
        graph_spec_dict,
        training_session_id,
        training_settings,
        load_checkpoint,
        user_email,
        results_interval=settings.TRAINING_RESULTS_REFRESH_INTERVAL,
        is_retry=is_retry
    )
    
