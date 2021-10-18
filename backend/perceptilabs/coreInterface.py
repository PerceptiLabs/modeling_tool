import queue
import numpy as np
import time
import os
import pprint
import logging
import GPUtil
import collections
import math


from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.resources.training_results import TrainingResultsAccess
from perceptilabs.compatibility import CompatibilityCore
from perceptilabs.resources.files import FileAccess
from perceptilabs.script import ScriptFactory
from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER
from perceptilabs.CoreThread import CoreThread
from perceptilabs.createDataObject import createDataObject
from perceptilabs.license_checker import LicenseV2
from perceptilabs.trainer import Trainer, TrainingModel
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.exporter.base import Exporter
from perceptilabs.caching.utils import get_data_metadata_cache
import perceptilabs.utils as utils


logger = logging.getLogger(APPLICATION_LOGGER)
user_logger = logging.getLogger(USER_LOGGER)


CoreCommand = collections.namedtuple('CoreCommand', ['type', 'parameters', 'allow_override'])


    
class coreLogic():
    def __init__(self, networkName, issue_handler, session_id=None):
        logger.info(f"Created coreLogic for network '{networkName}'")

        self._results_access = TrainingResultsAccess()
        self._core_mode = 'v2'

        self.networkName=networkName
        self.cThread=None
        self.status="Created"

        self.setupLogic()

        self.issue_handler = issue_handler
        self._running_mode = None

        self._data_metadata_cache = get_data_metadata_cache().for_compound_keys()

    def setupLogic(self):
        self.commandQ=queue.Queue()
        self.results_queue = queue.Queue()

        self.paused=False

        self.status="Created"
        self.core=None

    @property
    def running_mode(self):
        return self._running_mode

    def set_running_mode(self, mode):
        self._running_mode = mode
        logger.info(f"Running mode {mode} set for coreLogic w\ network '{self.networkName}'")

    def _get_restored_trainer(self, data_loader, script_factory, graph_spec, training_settings, checkpoint_directory, load_checkpoint, model_id, user_email):
        epochs_access = EpochsAccess()        
        epoch_id = epochs_access.get_latest(
            training_session_id=checkpoint_directory,  # TODO: Frontend needs to send ID
            require_checkpoint=True,
            require_trainer_state=True
        )

        checkpoint_path = epochs_access.get_checkpoint_path(
            training_session_id=checkpoint_directory,
            epoch_id=epoch_id
        )
        
        training_model = ModelAccess(script_factory).get_training_model(
            graph_spec, checkpoint_path=checkpoint_path)

        exporter = Exporter(
            graph_spec, training_model, data_loader, model_id=model_id, user_email=user_email)

        initial_state = epochs_access.load_state_dict(epoch_id)

        if initial_state:
            logger.info(f"Restoring trainer from epoch ID {epoch_id}")
        else:
            logger.warning(f"Restoring trainer from epoch ID {epoch_id}, but no state data found")

        trainer = Trainer(
            data_loader,
            exporter.training_model,
            training_settings,
            checkpoint_directory=os.path.dirname(checkpoint_path),
            exporter=exporter,
            model_id=model_id,
            user_email=user_email,
            initial_state=initial_state
        )
        logger.info("Restored trainer successfully")
        return trainer

    def _get_new_trainer(self, data_loader, script_factory, graph_spec, training_settings, checkpoint_directory, load_checkpoint, model_id, user_email):
        training_model = TrainingModel(script_factory, graph_spec)
        exporter = Exporter(
            graph_spec, training_model, data_loader,
            model_id=model_id, user_email=user_email
        )
        
        trainer = Trainer(
            data_loader,
            training_model,
            training_settings,
            checkpoint_directory=checkpoint_directory,
            exporter=exporter,
            model_id=model_id,
            user_email=user_email
        )
        logger.info("Created new trainer")
        return trainer

    def _get_trainer(self, script_factory, graph_spec, training_settings, dataset_settings_dict, checkpoint_directory, load_checkpoint, model_id, user_email, is_retry):
        """ Creates a Trainer for the IoInput/IoOutput workflow """

        num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (anton.k): remove when frontend solution exists

        dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
        csv_file = dataset_settings_dict['filePath']  # TODO: move one level up
        
        key = ['pipelines', user_email, csv_file, dataset_settings.compute_hash()]
        data_metadata = self._data_metadata_cache.get(key)

        if data_metadata is not None:
            logger.info(f"Found metadata for dataset with key {key}")

        file_access = FileAccess(os.path.dirname(csv_file))        
        data_loader = DataLoader.from_csv(
            file_access,
            csv_file,
            dataset_settings,
            num_repeats=num_repeats,
            metadata=data_metadata
        )
        
        if load_checkpoint or is_retry:
            logger.info(f"Restoring trainer from disk (load_checkpoint={load_checkpoint} and is_retry={is_retry})")
            try:
                trainer = self._get_restored_trainer(
                    data_loader, script_factory, graph_spec, training_settings,
                    checkpoint_directory, load_checkpoint, model_id, user_email
                )
                return trainer
            except:
                logger.exception(f"Tried to restore trainer from disk but failed (load_checkpoint={load_checkpoint} and is_retry={is_retry})")

        return self._get_new_trainer(
            data_loader, script_factory, graph_spec, training_settings, checkpoint_directory, load_checkpoint, model_id, user_email)

    def start_core(self, graph_spec, model_id, user_email, training_settings, dataset_settings, checkpoint_directory, load_checkpoint, on_finished, is_retry):
        """ Spins up a core for training (or exporting in the pre-data wizard case)

        Arguments:
            graph_spec: the specification of the model being trained
            model_id: the ID of the model
            user_email: the users email
            training_settings: only required for post-data wizard mode. A dict with things like number of epochs, type of optimizer, etc
            dataset_settings: only required for post-data wizard mode. A dict with things like train/test/val split, column data types, etc
            checkpoint_directory: where the trainer should look for checkpoints
            load_checkpoint: if true, the training model will be loaded from an existing checkpoint
        """
        try:
            self.Close()
        except:
            pass
        self.setupLogic()

        script_factory = ScriptFactory(
            simple_message_bus=True,
            running_mode=self._running_mode
        )
        trainer = self._get_trainer(script_factory, graph_spec, training_settings, dataset_settings, checkpoint_directory, load_checkpoint, model_id, user_email, is_retry)

        #if not self._validate_trainer(trainer):  # TODO(anton.k): uncomment once metadata caching is fixed
        #    return None

        core = self.core = CompatibilityCore(
            self.commandQ,
            self.results_queue,
            graph_spec,
            trainer,
            threaded=True,
            model_id=model_id
        )
        self._start_training_thread(core, on_finished)
        self.status = "Running"
        self.graph_spec = graph_spec
        return {"content":"core started"}

    def _start_training_thread(self, core, on_finished):
        """ Spins up a thread for the trainer """
        try:
            logger.debug("Starting core..." + repr(core))
            self.cThread=CoreThread(core.run, self.issue_handler, on_finished)
            self.cThread.daemon = True
            self.cThread.start_with_traces()
            # self.cThread.start()
        except Exception as e:
            message = "Could not boot up the new thread to run the computations on because of: " + str(e)
            with self.issue_handler.create_issue(message, e) as issue:
                self.issue_handler.put_error(issue.frontend_message)
                logger.error(issue.internal_message)
        else:
            logger.info(f"Started core for network {self.networkName}. Mode: {self._running_mode}")

    def _validate_trainer(self, trainer):
        """ Calls the validate method of the trainer """
        try:
            trainer.validate()
        except Exception as e:
            message = "Trainer raised an error on validation: " + repr(e)
            with self.issue_handler.create_issue(message, exception=e, as_bug=False) as issue:
                self.issue_handler.put_error(issue.frontend_message)
                logger.error(issue.internal_message)
            return False
        else:
            return True

    def Pause(self):
        self.commandQ.put(
            CoreCommand(
                type='pause',
                parameters={'paused': True},
                allow_override=True
            )
        )

        self.paused=True
        return  {"content": "Paused"}

    def Unpause(self):

        self.commandQ.put(
            CoreCommand(
                type='pause',
                parameters={'paused': False},
                allow_override=True
            )
        )
        self.paused=False
        return {"content":"Unpaused"}

    def Close(self):  # TODO: refactor this
        self.commandQ.put(
            CoreCommand(
                type='close',
                parameters=None,
                allow_override=False
            )
        )
        time.sleep(1.5) # Give the Core some time to close the training server before killing the thread...
        
        if self.cThread and self.cThread.isAlive():
            self.cThread.kill()
        return {"content":"closed core %s" % str(self.networkName)}

    def Stop(self): # TODO: refactor this
        self.status="Stop"
        self.commandQ.put(
            CoreCommand(
                type='stop',
                parameters=None,
                allow_override=False
            )
        )
        return {"content":"Stopping"}

    def export_network(self, settings):
        path = os.path.join(settings["Location"], settings["name"])
        path = os.path.abspath(path)
        mode = 'TFModel' # Default mode. # TODO: perhaps all export modes should be exposed to frontend?
        if settings["Quantized"]:
            mode = 'TFQuantized'
        elif settings['Compressed']:
            mode = 'TFLite'

        self.commandQ.put(
            CoreCommand(
                type='export',
                parameters={'path': path, 'mode': mode},
                allow_override=False
            )
        )

    def updateResults(self, value):
        training_session_id = value['trainingSessionId']
        
        results = None
        while not self.results_queue.empty():
            results = self.results_queue.get()
            
        if results:
            self._results_access.store(training_session_id, results)
            
        return {"content":"Results saved"}

