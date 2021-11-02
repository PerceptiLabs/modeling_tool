import logging
import functools
from abc import ABC, abstractmethod
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.utils import get_file_path

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
def training_task(dataset_settings_dict, model_id, graph_spec_dict, training_session_id, training_settings, load_checkpoint, user_email, is_retry=False):
    
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

    csv_file = get_file_path(dataset_settings_dict)  # TODO: move one level up        
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
        model_id,
        graph_spec_dict,
        training_session_id,
        training_settings,
        load_checkpoint,
        user_email,
        results_interval=settings.TRAINING_RESULTS_REFRESH_INTERVAL,
        is_retry=is_retry
    )
    

@log_exceptions    
def testing_task(testing_session_id, models_info, tests, user_email, is_retry=False):
    import perceptilabs.settings as settings        
    from perceptilabs.testInterface import TestingSessionInterface
    from perceptilabs.messaging.base import get_message_broker
    from perceptilabs.caching.utils import get_data_metadata_cache    
    from perceptilabs.script.base import ScriptFactory    
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.files import FileAccess
    from perceptilabs.resources.testing_results import TestingResultsAccess 
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    import perceptilabs.utils as utils
    import os
    
    message_broker = get_message_broker()
    data_metadata_cache = get_data_metadata_cache().for_compound_keys()
    
    model_access = ModelAccess(ScriptFactory())
    epochs_access = EpochsAccess()
    results_access = TestingResultsAccess()

    models = {}
    for model_id in models_info.keys():
        dataset_settings_dict = models_info[model_id]['datasetSettings']
        csv_file = get_file_path(dataset_settings_dict)  # TODO: move one level up
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

        graph_dict = models_info[model_id]['layers'] 
        graph_spec = model_access.get_graph_spec(model_id=graph_dict)  # TODO: f/e should send an ID        
        models[model_id] = {
            'graph_spec': graph_spec,
            'data_loader': data_loader,
            'model_name': models_info[model_id]['model_name'],
            'training_session_id': models_info[model_id]['training_session_id']
        }

    interface = TestingSessionInterface(
        message_broker, model_access, epochs_access, results_access)

    interface.run(
        testing_session_id,
        models,
        tests,
        user_email=user_email,
        results_interval=settings.TESTING_RESULTS_REFRESH_INTERVAL        
    )
     

@log_exceptions    
def serving_task(serving_type, dataset_settings_dict, graph_spec_dict, training_session_id, model_name, user_email, serving_session_id, is_retry=False):
    
    import perceptilabs.settings as settings    
    from perceptilabs.serving.interface import ServingSessionInterface
    from perceptilabs.caching.utils import get_data_metadata_cache    
    from perceptilabs.script.base import ScriptFactory    
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.files import FileAccess
    from perceptilabs.resources.serving_results import ServingResultsAccess
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    from perceptilabs.messaging.base import get_message_broker    
    import perceptilabs.utils as utils
    import os

    message_broker = get_message_broker()    
    data_metadata_cache = get_data_metadata_cache().for_compound_keys()
    
    model_access = ModelAccess(ScriptFactory())
    epochs_access = EpochsAccess()
    results_access = ServingResultsAccess()        

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
    
    interface = ServingSessionInterface(
        message_broker, model_access, epochs_access, results_access)

    interface.run(
        data_loader,
        graph_spec_dict,
        training_session_id,
        serving_session_id,
        model_name,
        user_email,
        results_interval=settings.SERVING_RESULTS_REFRESH_INTERVAL,
        is_retry=is_retry
    )
    
