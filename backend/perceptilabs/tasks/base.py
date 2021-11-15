import logging
import functools
from abc import ABC, abstractmethod
from perceptilabs.utils import get_file_path


logger = logging.getLogger(__name__)


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
    from perceptilabs.training_interface import TrainingSessionInterface
    from perceptilabs.messaging.base import get_message_broker
    from perceptilabs.caching.utils import get_data_metadata_cache    
    from perceptilabs.script.base import ScriptFactory    
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.files import FileAccess
    from perceptilabs.resources.training_results import TrainingResultsAccess
    from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess    
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    import perceptilabs.utils as utils
    import os

    message_broker = get_message_broker()
    
    model_access = ModelAccess(ScriptFactory())
    epochs_access = EpochsAccess()
    training_results_access = TrainingResultsAccess()
    preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())            

    # TODO: all this data setup should be moved into the coreInteraface!!!
    
    csv_file = get_file_path(dataset_settings_dict)  # TODO: move one level up        
    num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (anton.k): remove when frontend solution exists

    dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
    data_metadata = preprocessing_results_access.get_metadata(dataset_settings.compute_hash())

    file_access = FileAccess(os.path.dirname(csv_file))        
    data_loader = DataLoader.from_csv(
        file_access,
        csv_file,
        dataset_settings,
        num_repeats=num_repeats,
        metadata=data_metadata
    )
    
    interface = TrainingSessionInterface(
        message_broker, model_access, epochs_access, training_results_access)
    
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
    from perceptilabs.testing_interface import TestingSessionInterface
    from perceptilabs.messaging.base import get_message_broker
    from perceptilabs.caching.utils import get_data_metadata_cache    
    from perceptilabs.script.base import ScriptFactory    
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.files import FileAccess
    from perceptilabs.resources.testing_results import TestingResultsAccess
    from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess        
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    import perceptilabs.utils as utils
    import os
    
    message_broker = get_message_broker()
    data_metadata_cache = get_data_metadata_cache().for_compound_keys()
    
    model_access = ModelAccess(ScriptFactory())
    epochs_access = EpochsAccess()
    testing_results_access = TestingResultsAccess()
    preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())                


    # TODO: all this data loader etup should be moved into the test interface!!!
    models = {}
    for model_id in models_info.keys():
        dataset_settings_dict = models_info[model_id]['datasetSettings']
        csv_file = get_file_path(dataset_settings_dict)  # TODO: move one level up
        num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (anton.k): remove when frontend solution exists

        dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
        data_metadata = preprocessing_results_access.get_metadata(dataset_settings.compute_hash())

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
        message_broker, model_access, epochs_access, testing_results_access)

    interface.run(
        testing_session_id,
        models,
        tests,
        user_email=user_email,
        results_interval=settings.TESTING_RESULTS_REFRESH_INTERVAL        
    )
     

@log_exceptions    
def serving_task(serving_type, dataset_settings_dict, graph_spec_dict, model_id, training_session_id, model_name, user_email, serving_session_id, is_retry=False):
    
    import perceptilabs.settings as settings    
    from perceptilabs.serving_interface import ServingSessionInterface
    from perceptilabs.caching.utils import get_data_metadata_cache    
    from perceptilabs.script.base import ScriptFactory    
    from perceptilabs.resources.models import ModelAccess
    from perceptilabs.resources.epochs import EpochsAccess
    from perceptilabs.resources.files import FileAccess
    from perceptilabs.resources.serving_results import ServingResultsAccess
    from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess        
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings
    from perceptilabs.messaging.base import get_message_broker    
    import perceptilabs.utils as utils
    import os

    message_broker = get_message_broker()    
    data_metadata_cache = get_data_metadata_cache().for_compound_keys()
    
    model_access = ModelAccess(ScriptFactory())
    epochs_access = EpochsAccess()
    serving_results_access = ServingResultsAccess()
    preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())                

    csv_file = get_file_path(dataset_settings_dict)  # TODO: move one level up        
    num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (anton.k): remove when frontend solution exists

    dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
    data_metadata = preprocessing_results_access.get_metadata(dataset_settings.compute_hash())    

    file_access = FileAccess(os.path.dirname(csv_file))        
    data_loader = DataLoader.from_csv(
        file_access,
        csv_file,
        dataset_settings,
        num_repeats=num_repeats,
        metadata=data_metadata
    )
    
    interface = ServingSessionInterface(
        message_broker, model_access, epochs_access, serving_results_access)

    interface.run(
        data_loader,
        graph_spec_dict,
        model_id,
        training_session_id,
        serving_session_id,
        model_name,
        user_email,
        results_interval=settings.SERVING_RESULTS_REFRESH_INTERVAL,
        is_retry=is_retry
    )
    

@log_exceptions    
def preprocessing_task(dataset_settings_dict, preprocessing_session_id):
    from perceptilabs.preprocessing_interface import PreprocessingSessionInterface  # TODO: should preprocessing_interface have a better name??
    from perceptilabs.caching.utils import get_data_metadata_cache    
    from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess        
    from perceptilabs.messaging.base import get_message_broker    

    preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())
    interface = PreprocessingSessionInterface(preprocessing_results_access)

    interface.run(dataset_settings_dict, preprocessing_session_id)
    
    
