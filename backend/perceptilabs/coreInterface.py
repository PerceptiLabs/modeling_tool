import queue
import numpy as np
import time
import psutil
import os
import pprint
import logging
import GPUtil
import collections
import math


from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.core_new.compatibility import CompatibilityCore
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
        self._session_id = session_id
        self._core_mode = 'v2'

        self.networkName=networkName
        self.cThread=None
        self.status="Created"
        self.resultDict=None

        self.setupLogic()
        self.plLicense = LicenseV2()

        self.issue_handler = issue_handler
        self._running_mode = None
        self._save_counter = 0

        self.headless_state = False
        self._data_metadata_cache = get_data_metadata_cache().for_compound_keys()

    def setupLogic(self):
        self.commandQ=queue.Queue()
        self.resultQ=queue.Queue()

        self.trainResults=None
        self.testResults=None
        self.paused=False

        self.status="Created"
        self.headlessFlag=False
        self.core=None

        self.savedResultsDict={}

    def _logAndWarningQueue(self, msg):
        user_logger.info(msg)

    def gpu_list(self):
        try:
            gpus = GPUtil.getGPUs()
        except:
            logger.error("No compatible nvidia GPU drivers available. Defaulting to 0 GPUs")
            gpus = []

        if self.plLicense.is_expired():
            self._logAndWarningQueue(f"Your license is in demo mode. Limiting to one GPU.")
            gpus = gpus[:1]

        print(f"GPU limit: {self.plLicense.gpu_limit()}")
        limit = self.plLicense.gpu_limit()
        if limit > len(gpus):
            self._logAndWarningQueue(f"Your license limits training to {limit}.")
            gpus = gpus[:limit]

        print(f"GPU count: {len(gpus)}")
        return gpus

    def isDistributable(self, gpus):
        print(f"Core limit: {self.plLicense.core_limit()}")
        if len(gpus) <= 1:
            self._logAndWarningQueue(f"Not enough GPUs to distribute training. Using one core.")
            return False

        if self.plLicense.core_limit() <= 1:
            self._logAndWarningQueue(f"Your license limits you to one core.")
            return False

        if self.plLicense.is_expired():
            self._logAndWarningQueue(f"Your license is in demo mode. Limiting to one core.")
            return False

        return True


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
        key = ['pipelines', user_email, dataset_settings.compute_hash()]

        data_metadata = self._data_metadata_cache.get(key)

        if data_metadata is not None:
            logger.info(f"Found metadata for dataset with key {key}")

        data_loader = DataLoader.from_settings(dataset_settings, num_repeats=num_repeats, metadata=data_metadata)

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
            self.resultQ,
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

    def set_headless(self, active):
        """ Enable/disable headless """
        if active != self.headless_state:
            self.headless_state = active

            if self._core_mode == 'v1':
                if active:
                    self.commandQ.put("headlessOn")
                else:
                    self.commandQ.put("headlessOff")
            else:
                self.commandQ.put(
                    CoreCommand(
                        type='headless',
                        parameters={'on': active},
                        allow_override=True
                    )
                )

    def headless(self, On):
        """ Alias for set_headless """
        self.set_headless(active=On)

    def headlessOn(self):
        """ Deprecated. Use set_headless """
        self.set_headless(active=True)

    def headlessOff(self):
        """ Deprecated. Use set_headless """
        self.set_headless(active=False)

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

    def isRunning(self):
        if self.cThread is not None and self.cThread.isAlive():
            return { "content": True }
        else:
            return { "content": False }

    def isTrained(self):
        is_trained = (
            (self._core_mode == 'v2' and self.core is not None and self.resultDict is not None)
        )
        return {"content": is_trained}

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

    def skipValidation(self):
        self.commandQ.put("skip")
        logger.warning('skipValidation called... incompatible with core v2')
        #Check if validation was skipped or not before returning message
        return {"content":"skipped validation"}

    def get_cpu_and_mem(self):
        cpu = psutil.cpu_percent()
        mem = dict(psutil.virtual_memory()._asdict())["percent"]
        return cpu, mem

    def get_gpu(self):
        try:
            gpus = GPUtil.getGPUs()
            loadList = [gpu.load*100 if not math.isnan(gpu.load) else 0 for gpu in gpus]
        except:
            loadList = None
        if loadList:
            return np.average(loadList)
        else:
            return ""

    def getStatus(self):
        try:
            cpu, mem = self.get_cpu_and_mem()
            gpu = self.get_gpu()
            if gpu and int(gpu) == 0:
                gpu = 1

            progress = self.savedResultsDict.get('progress')
            if progress is None:
                progress = (self.savedResultsDict["epoch"]*self.savedResultsDict["maxIter"]+self.savedResultsDict["iter"])/(max(self.savedResultsDict["maxEpochs"]*self.savedResultsDict["maxIter"],1))


            if self.status=="Running":
                result = {
                    "Status":"Paused" if self.paused else self.savedResultsDict["trainingStatus"],
                    "Iterations": self.savedResultsDict["iter"],
                    "Epoch": self.savedResultsDict["epoch"],
                    "Progress": progress,
                    "CPU": cpu,
                    "GPU": gpu,
                    "Memory": mem,
                    "Training_Duration": self.savedResultsDict["training_duration"]
                }
                return result
            else:
                return {
                    "Status":self.status,
                    "Iterations":self.savedResultsDict["iter"],
                    "Epoch":self.savedResultsDict["epoch"],
                    "Progress": progress,
                    "CPU":cpu,
                    "GPU": gpu,
                    "Memory":mem
                }
        except KeyError as e:
            logger.debug(f"Key Error in getStatus: {repr(e)}")
            return {}


    def updateResults(self):
        #TODO: Look from the back and go forward if we find a test instead of going through all of them
        tmp=None
        while not self.resultQ.empty():
            tmp = self.resultQ.get()
        if tmp:
            self.savedResultsDict.update(tmp)

        return {"content":"Results saved"}

    def get_global_training_statistics(self):
        """ Returns the global stats """
        if not self.savedResultsDict:
            return {}

        stats = self.savedResultsDict['global_stats']
        output = stats.get_data_objects()
        return output

    def getTrainingStatistics(self,value):
        layer_id = value["layerId"]
        layer_type = value["layerType"]
        view = value["view"]
        if not self.savedResultsDict:
            return {}

        try:
            self.iter=self.savedResultsDict["iter"]
            self.epoch=self.savedResultsDict["epoch"]
            self.maxIter=self.savedResultsDict["maxIter"]
            self.maxEpochs=self.savedResultsDict["maxEpochs"]
            self.batch_size=self.savedResultsDict["batch_size"]
            self.trainingIterations=self.savedResultsDict["trainingIterations"]
            self.resultDict=self.savedResultsDict["inner_layers_stats"]
        except KeyError:
            message = "Error in getTrainingStatistics."
            if logger.isEnabledFor(logging.DEBUG):
                message += " savedResultsDict: " + pprint.pformat(self.savedResultsDict)
            logger.exception(message)
            return {}
        try:
            layer_statistics = self.getLayerStatistics(layer_id, layer_type, view)
            return layer_statistics
        except:
            message = f"Error in getTrainingStatistics. layer_id = {layer_id}, layer_type = {layer_type}, view = {view}."
            if logger.isEnabledFor(logging.DEBUG):
                message += " savedResultsDict: " + pprint.pformat(self.savedResultsDict)
            logger.exception(message)

    def getEndResults(self):
        #TODO: Show in frontend results for each end layer, not just for one.
        end_results={}
        #global stats
        global_stats = self.savedResultsDict['global_stats']
        end_results['global_stats'] = global_stats.get_end_results()
        #layer specific stats
        for layer_spec in self.graph_spec.layers:
            if layer_spec.is_target_layer:
                layer_stats = self.savedResultsDict['output_stats'][layer_spec.id_]
                end_results[layer_spec.name] = layer_stats.get_end_results()
        return end_results

    def getLayerStatistics(self, layerId, layerType, view):
        logger.debug("getLayerStatistics for layer '{}' with type '{}' and view: '{}'".format(layerId, layerType, view))

        if layerType == 'IoInput':
            return self._get_stats_ioinput(layerId)
        elif layerType == 'IoOutput':
            return self._get_stats_iooutput(layerId, view)
        else:
            stats = self.savedResultsDict['inner_layers_stats'][layerId]
            output = stats.get_data_objects(view)
            return output

    def _get_stats_ioinput(self, layer_id):
        try:
            stats = self.savedResultsDict['input_stats']
            output_value = stats.get_sample_by_layer_id(layer_id)
        except:
            output_value = 0.0  # Default value
        data_object = createDataObject([output_value])
        return {"Data": data_object}

    def _get_stats_iooutput(self, layer_id, view):
        stats = self.savedResultsDict['output_stats'][layer_id]
        output = stats.get_data_objects()
        if view:
            output = output[view]
        return output
