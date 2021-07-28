import json
import queue
import numpy as np
import time
import psutil
import shutil
import copy
import traceback
import os
import threading
import pprint
import logging
import skimage
import GPUtil
import collections
import math
import sys
import tensorflow as tf
from typing import List

from perceptilabs.core_new.compatibility import CompatibilityCore
from perceptilabs.script import ScriptFactory
from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER
from perceptilabs.networkExporter import exportNetwork
from perceptilabs.networkSaver import saveNetwork
import perceptilabs.utils as utils
from perceptilabs.api.data_container import DataContainer
from perceptilabs.core_new.errors import CoreErrorHandler
from perceptilabs.CoreThread import CoreThread
from perceptilabs.createDataObject import createDataObject
from perceptilabs.messaging import MessageProducer
from perceptilabs.aggregation import AggregationRequest, AggregationEngine
from perceptilabs.license_checker import LicenseV2
from perceptilabs.trainer import Trainer, TrainingModel
from perceptilabs.automation.modelrecommender.base import ModelRecommender
from perceptilabs.data.base import DataLoader, FeatureSpec

from perceptilabs.data.settings import DatasetSettings
from perceptilabs.exporter.base import Exporter
import perceptilabs.cache_utils as cache_utils

logger = logging.getLogger(APPLICATION_LOGGER)
user_logger = logging.getLogger(USER_LOGGER)

CoreCommand = collections.namedtuple('CoreCommand', ['type', 'parameters', 'allow_override'])


CPU_GPU_POLICY = 'force-gpu' # {'use-spec', 'force-gpu', 'force-cpu'}


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

        self._aggregation_futures = []

        self.issue_handler = issue_handler
        self._running_mode = None
        self._save_counter = 0

        self.headless_state = False
        self._data_metadata_cache = cache_utils.get_data_metadata_cache()

    def setupLogic(self):
        #self.warningQueue=queue.Queue()

        self.commandQ=queue.Queue()
        # self.resultQ=queue.LifoQueue()
        self.resultQ=queue.Queue()

        self.trainResults=None
        self.testResults=None
        self.paused=False

        self.status="Created"
        self.headlessFlag=False
        self.core=None

        self.testIter=0
        self.maxTestIter=0
        self.testList= None

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

    def _override_graph_spec(self, graph_spec):
        """ Returns a new GraphSpec with certain settings modified """
        gpus = self.gpu_list()
        distributed = self.isDistributable(gpus)

        assert CPU_GPU_POLICY in {'use-spec', 'force-gpu', 'force-cpu'}

        network = graph_spec.to_dict()
        for _id, layer in network.items():
            if 'Train' in layer['Type']:
                if CPU_GPU_POLICY == 'force-cpu':
                    layer['Properties']['Use_CPU'] = True
                if CPU_GPU_POLICY == 'force-gpu':
                    layer['Properties']['Use_CPU'] = False

            if layer['Type'] == 'TrainNormal':
                layer['Properties']['Distributed'] = distributed

        return graph_spec.from_dict(network)

    @property
    def running_mode(self):
        return self._running_mode

    def set_running_mode(self, mode):
        self._running_mode = mode
        logger.info(f"Running mode {mode} set for coreLogic w\ network '{self.networkName}'")

    def _get_trainer(self, script_factory, graph_spec, training_settings, dataset_settings_dict, checkpoint_directory, load_checkpoint, model_id, user_email):
        """ Creates a Trainer for the IoInput/IoOutput workflow """
        num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (anton.k): remove when frontend solution exists

        dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)
        dataset_hash = cache_utils.format_key(['pipelines', user_email, dataset_settings.compute_hash()])
        data_metadata = self._data_metadata_cache.get(dataset_hash) if self._data_metadata_cache else None

        if data_metadata is not None:
            logger.info(f"Found metadata for dataset with hash {dataset_hash}")

        data_loader = DataLoader.from_settings(dataset_settings, num_repeats=num_repeats, metadata=data_metadata)

        if load_checkpoint:
            exporter = Exporter.from_disk(
                checkpoint_directory, graph_spec, script_factory, data_loader,
                model_id=model_id, user_email=user_email
            )
            trainer = Trainer.restore_latest_epoch(
                data_loader,
                training_settings,
                exporter,
                model_id=model_id,
                user_email=user_email
            )
            return trainer
        else:
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
            return trainer

    def start_core(self, graph_spec, model_id, user_email, training_settings, dataset_settings, checkpoint_directory, load_checkpoint):
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

        logger.debug('printing network .......\n')

        if logger.isEnabledFor(logging.DEBUG) and os.access(os.getcwd(), os.W_OK):
            import json
            with open('net.json_', 'w') as f:
                json.dump(graph_spec.to_dict(), f, indent=4)

        graph_spec = self._override_graph_spec(graph_spec)

        script_factory = ScriptFactory(
            simple_message_bus=True,
            running_mode=self._running_mode
        )
        trainer = self._get_trainer(script_factory, graph_spec, training_settings, dataset_settings, checkpoint_directory, load_checkpoint, model_id, user_email)

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
        self._start_training_thread(core)

        self.status = "Running"
        self.graph_spec = graph_spec

        return {"content":"core started"}

    def _start_training_thread(self, core):
        """ Spins up a thread for the trainer """
        try:
            logger.debug("Starting core..." + repr(core))
            self.cThread=CoreThread(core.run, self.issue_handler)
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

    def saveIpynbToDisk(self, value):
        path = value.get('Location')
        if path is None or not path:
            return {"content": 'Location not specified'}

        notebook_json = value.get('NotebookJson')
        if notebook_json is None or not notebook_json:
            return {"content": 'Cannot export empty network'}

        filepath = os.path.abspath(path + '/' + value.get("frontendNetwork") + '.ipynb')

        with open(filepath, 'w') as json_file:
            json.dump(notebook_json, json_file)

        return {"content":"Export success!\nSaved as:\n" + filepath}

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

        return {"content": f"Exporting of model requested to the path {path}"}

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

    def scheduleAggregations(self, engine: AggregationEngine, requests: List[AggregationRequest]):
        """ Schedules a batch of metric aggregations

        Args:
            engine: Aggregation Engine to compute
            requests: A list of AggregationRequests to computate
        """
        future = engine.request_batch(requests)
        self._aggregation_futures.append(future)

        def prune_futures(future):
            """ Retain only the most recently completed future (and not-yet-completed futures) """
            while len(self._aggregation_futures) >= 2 and self._aggregation_futures[1].done():
                del self._aggregation_futures[0]

        future.add_done_callback(prune_futures)

    def getAggregationResults(self, result_names: list) -> dict:
        """ Retrieve results of scheduled aggregations

        Args:
            result_names: names of the results to get from Aggregation Engine once computation is finished

        Returns:
            retrieved: a dictionary of by result_names queried
        """
        if len(self._aggregation_futures) == 0:
            return {}

        future = self._aggregation_futures[0]
        if not future.done():
            return {}

        retrieved = {}
        results, _, _ = future.result()
        for result_name in result_names:
            value, _, _ = results.get(result_name, (None, None, None))
            retrieved[result_name] = value
        return retrieved

    def updateResults(self):
        #TODO: Look from the back and go forward if we find a test instead of going through all of them
        tmp=None
        while not self.resultQ.empty():
            tmp = self.resultQ.get()

            if 'testDict' in tmp:
                self.testList = tmp["testDict"]
                self.maxTestIter = tmp['maxTestIter']
                if self.testIter != self.maxTestIter-1:
                    self.testIter += 1
                else:
                    self.testIter = 1
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
            self.resultDict=self.savedResultsDict["trainDict"]
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

        if layerType=="DataEnvironment":
            state = self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1,:,:,:3]
            dataObj = createDataObject([state])
            return {"Data":dataObj}
        elif layerType=="DataData":
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})
            dataObj = createDataObject([D[-1]])
            return {"Data":dataObj}
        elif layerType=="DataRandom":
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})
            dataObj = createDataObject([D[-1]])
            return {"Data":dataObj}
        elif layerType == 'IoInput':
            return self._get_stats_ioinput(layerId)
        elif layerType == 'IoOutput':
            return self._get_stats_iooutput(layerId, view)
        elif layerType=="LayerCustom":
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})
            dataObj = createDataObject([D[-1]])
            return {"Output":dataObj}
        elif layerType=="DeepLearningFC":
            if view=="Output":
                D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
                dataObject = createDataObject([D])
                output = {"Output": dataObject}
                return output
            if view=="Weights&Bias":
                w=self.getStatistics({"layerId":layerId,"variable":"W","innervariable":""})
                w=np.average(w,axis=0)
                dataObjectWeights = createDataObject([w], type_list=['line'])

                b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                dataObjectBias = createDataObject([b], type_list=['line'])

                output = {"Bias": dataObjectBias, "Weights": dataObjectWeights}
                return output
            if view=="Gradients":
                minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})

                dataObj = createDataObject([minD, maxD, avD],
                                            type_list=3*['line'],
                                            name_list=['Min', 'Max', 'Average'],
                                            style_list=[{"color":"#83c1ff"},
                                                        {"color":"#0070d6"},
                                                        {"color":"#6b8ff7"}])

                output = {"Gradients": dataObj}
                return output
        elif layerType=="DeepLearningConv" or layerType=="UNet":
            if view=="Weights&Output":
                weights=self.getStatistics({"layerId":layerId,"variable":"W","innervariable":""})
                Wshapes=weights.shape
                if len(Wshapes)==3:
                    weights=np.expand_dims(np.average(weights[:,:,-1],1),axis=0)
                elif len(Wshapes)==4:
                    weights=np.average(weights[:,:,:,-1],2)
                elif len(Wshapes)==5:
                    weights=np.average(weights[:,:,:,:,-1],3)
                outputs=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]


                dataObjWeights = createDataObject([weights], type_list=['heatmap'])
                dataObjOutput = self._process_conv_layer_output(outputs)

                obj = {"Weights":dataObjWeights, "Output": dataObjOutput}
                return obj
            if view=="Bias":
                b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                dataObj = createDataObject([b], type_list=['line'])
                output = {"Bias": dataObj}
                return output
            if view=="Gradients":
                minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})

                dataObj = createDataObject([minD, maxD, avD],
                                            type_list=3*['line'],
                                            name_list=['Min', 'Max', 'Average'],
                                            style_list=[{"color":"#83c1ff"},
                                                        {"color":"#0070d6"},
                                                        {"color":"#6b8ff7"}])
                output = {"Gradients": dataObj}
                return output
        elif layerType=="DeepLearningRecurrent":

            # if view=="Output":
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
            dataObject = createDataObject([D])
            dataObject = {"Output": dataObject}
            return dataObject

        elif layerType=="PreTrainedResNet50":
            return self._get_viewbox_pretrained(layerId, view)

        elif layerType=="PreTrainedInceptionV3":
            return self._get_viewbox_pretrained(layerId, view)

        elif layerType=="PreTrainedMobileNetV2":
            return self._get_viewbox_pretrained(layerId, view)

        elif layerType=="PreTrainedVGG16":
            return self._get_viewbox_pretrained(layerId, view)

        elif layerType=="MathMerge":
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
            if len(D.shape) == 3:
                output = self._process_conv_layer_output(D)
            else:
                output = createDataObject([np.squeeze(D).astype(np.float32)])
            return {"Output":output}
        elif layerType in ["MathSoftmax", "MathArgmax", "MathSwitch", "ProcessOneHot", "ProcessCrop", "ProcessReshape", "ProcessRescale"]:
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
            output = createDataObject([np.squeeze(D).astype(np.float32)])
            return {"Output":output}
        elif layerType == "ProcessGrayscale":
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
            if len(D.shape) == 3:
                if D.shape[-1] == 1:
                    output = createDataObject([D])
                else:
                    output = createDataObject([D[:,:,0]])
            elif len(D.shape)>3:
                output = createDataObject([D[0]])
            else:
                output = createDataObject([D])
            return {"Output":output}


        else:
            return "FieldError: Does not recognize the layerType. " + layerType + " is not in [Train, Fc, Conv, Argmax, Softmax, Merge, OneHot, Crop, Reshape, Grayscale]"

    def getPlot(self,D):
        shape=np.squeeze(D).shape
        if len(shape)==0:
            t="scatter"
        elif len(shape)==1:
            if shape[0]<25:
                t="bar"
            else:
                t="line"
        elif len(shape)==2:
            t="grayscale"
        elif len(shape)==3:
            if shape[-1]==1:
                t="grayscale"
            elif shape[-1]==3:
                t="RGB"    #Assume RGB, Replace with a button later on
            # elif np.shape(np.squeeze(self.variables[self.currentView]["input"]))[0]==np.shape(np.squeeze(self.variables[self.currentView]["input"]))[1]==np.shape(np.squeeze(self.variables[self.currentView]["input"]))[2]:
            #     pass
            else:
                t="heatmap"
            #     self.plot1.imshow(self.variables[self.currentView]["input"][:,:,0])
        else:
            t="scatter" #Just something which works for all
        return t

    def getStatistics(self,statSpec):
        layerId=statSpec["layerId"]
        variable=statSpec["variable"]
        innervariable=statSpec["innervariable"]
        return self._get_layer_statistics_internal(layerId, variable, innervariable)

    def _get_layer_statistics_internal(self, layerId, variable="", innervariable=""):
        if self.resultDict is not None:
            logger.debug(f"ResultDict has entries for layers {list(self.resultDict.keys())}")

        logger.debug("getStatistics for layer {}, variable {}, innervariable {}".format(
            layerId,
            variable,
            innervariable
        ))

        if self.resultDict is None:
            return np.array([])
        elif layerId != "" and variable != "" and innervariable != "":
            result = self.resultDict.get(layerId, {}).get(variable, {}).get(innervariable, [])
            if not isinstance(result, dict):
                result = np.asarray(result)
            return result
        elif layerId != "" and variable != "":
            result = self.resultDict.get(layerId, {}).get(variable, [])
            if not isinstance(result, dict):
                result = np.asarray(result)
            return result
        elif layerId != "":
            result = self.resultDict.get(layerId, [])
            if not isinstance(result, dict):
                result = np.asarray(result)
            return result
        else:
            return np.array([])

    def _get_statistics_debug_info(self, layer_id, variable, innervariable, result):
        layer_type = self.graph_spec[layer_id].type_
        layer_name = self.graph_spec[layer_id].name

        message =   f"getStatistics called with:\n" \
                    f"    layerId       = '{layer_id}' [{layer_name}: {layer_type}]\n"\
                    f"    variable      = '{variable}'\n"\
                    f"    innervariable = '{innervariable}'\n "

        if isinstance(result, np.ndarray):
            message += f"output: ndarray of shape {result.shape} and dtype {result.dtype}"
        elif isinstance(result, dict):
            type_map = {k: type(v) for k, v in result.items()}
            message += f"output: dict with keys and types: {type_map}"
        elif isinstance(result, list):
            len_ = len(result)
            type_ = type(result[0]) if len_ > 0 else '<unknown>'
            message += f"output: list with length {len_} and types: {type_}"
        else:
            message += f"output: {type(result)}"

        logger.debug(message)

    def _process_conv_layer_output(self, output):
        if len(output.shape) != 2:
            output=output[:, :, 0]

        processed_output = createDataObject([output])

        return processed_output

    def _get_stats_ioinput(self, layer_id):
        output_batch = self._get_layer_statistics_internal(layer_id, variable="Y")
        try:
            output_value = output_batch[-1]
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

    def _get_viewbox_pretrained(self, layer_id, view):
        if view=="Output":
            D=self.getStatistics({"layerId":layer_id,"variable":"Y","innervariable":""})[-1]
            dataObject = createDataObject([D])
            output = {"Output": dataObject}
            return output
        if view=="Weights&Bias":
            w=self.getStatistics({"layerId":layer_id,"variable":"W","innervariable":""})
            w=np.squeeze(w)
            w_shape = w.shape
            if len(w_shape) == 4:
                w=w[-1,-1,:,:]
            elif len(w_shape) == 3:
                w=w[-1,:,:]
            w=np.mean(w, axis=1)
            dataObjectWeights = createDataObject([w], type_list=['line'])

            b=self.getStatistics({"layerId":layer_id,"variable":"b","innervariable":""})

            if b is not None:
                dataObjectBias = createDataObject([b], type_list=['line'])
                output = {"Bias": dataObjectBias, "Weights": dataObjectWeights}
            else:
                output = {"Weights": dataObjectWeights}

            return output
        if view=="Gradients":
            minD=self.getStatistics({"layerId":layer_id,"variable":"Gradient","innervariable":"Min"})
            maxD=self.getStatistics({"layerId":layer_id,"variable":"Gradient","innervariable":"Max"})
            avD=self.getStatistics({"layerId":layer_id,"variable":"Gradient","innervariable":"Average"})

            dataObj = createDataObject([minD, maxD, avD],
                                        type_list=3*['line'],
                                        name_list=['Min', 'Max', 'Average'],
                                        style_list=[{"color":"#83c1ff"},
                                                    {"color":"#0070d6"},
                                                    {"color":"#6b8ff7"}])

            output = {"Gradients": dataObj}
            return output

