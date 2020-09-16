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

from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.networkExporter import exportNetwork
from perceptilabs.networkSaver import saveNetwork
import perceptilabs.utils as utils
from perceptilabs.api.data_container import DataContainer
from perceptilabs.core_new.errors import CoreErrorHandler
from perceptilabs.CoreThread import CoreThread
from perceptilabs.createDataObject import createDataObject
from perceptilabs.messaging import MessageProducer
from perceptilabs.aggregation import AggregationRequest, AggregationEngine
from typing import List

from perceptilabs.license_checker import LicenseV2

logger = logging.getLogger(APPLICATION_LOGGER)


CoreCommand = collections.namedtuple('CoreCommand', ['type', 'parameters', 'allow_override'])


class coreLogic():
    def __init__(self,networkName, issue_handler, session_id=None):
        logger.info(f"Created coreLogic for network '{networkName}'")
        self._session_id = session_id
        self._core_mode = 'v2'
        
        self.networkName=networkName
        self.cThread=None
        self.status="Created"
        self.resultDict=None

        self.setupLogic()
        self.plLicense = LicenseV2()
        
        self._save_counter = 0
        self._aggregation_futures = []

        self.issue_handler = issue_handler

    def setupLogic(self):
        #self.warningQueue=queue.Queue()
        
        self.commandQ=queue.Queue()
        # self.resultQ=queue.LifoQueue()
        self.resultQ=queue.Queue()

        self.trainResults=None
        self.testResults=None
        self.paused=False

        self.status="Created"
        self.core=None

        self.testIter=0
        self.maxTestIter=0
        self.testList=[]
        self.playCounter=None
        self.playing=False

        self.saver=None

        self.savedResultsDict={}

    def _logAndWarningQueue(self, msg):
        logger.warning(msg)
        self.issue_handler.put_warning(msg)        
        
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

    def startCore(self, graph_spec, checkpointValues, model_id):
        self.graph_spec = graph_spec

        self.Close()
        self.setupLogic()
        
        logger.debug('printing network .......\n')

        if logger.isEnabledFor(logging.DEBUG):        
            import json
            with open('net.json_', 'w') as f:
                json.dump(graph_spec.to_dict(), f, indent=4) 

        if logger.isEnabledFor(logging.DEBUG):        
            import json
            with open('net.json_', 'w') as f:
                json.dump(graph_spec.to_dict(), f, indent=4)
                
        def backprop(layer_id):
            backward_connections = network['Layers'][layer_id]['backward_connections']
            if backward_connections:
                id_, name = backward_connections[0]
                return backprop(id_)
            else:
                return layer_id


        gpus = self.gpu_list()
        distributed = self.isDistributable(gpus)

        use_cpu_only = True

        # ----- 
        network = graph_spec.to_dict()
        for _id, layer in network.items():
            if 'Train' in layer['Type']:
                if not 'Use_CPU' in layer['Properties']:
                    layer['Properties']['Use_CPU'] = use_cpu_only

            if layer['Type'] == 'TrainNormal':
                layer['Properties']['Distributed'] = distributed
        graph_spec = graph_spec.from_dict(network)
        # -----

        if self._core_mode == 'v1':
            raise NotImplementedError
        elif self._core_mode == 'v2':
            from perceptilabs.core_new.compatibility import CompatibilityCore
            from perceptilabs.messaging.zmq_wrapper import ZmqMessagingFactory  
            from perceptilabs.messaging.simple import SimpleMessagingFactory          
            from perceptilabs.core_new.graph.builder import GraphBuilder
            from perceptilabs.script import ScriptFactory

            from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP                

            replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}                
            graph_builder = GraphBuilder(replica_by_name)
            
            script_factory = ScriptFactory(simple_message_bus=True)
            messaging_factory = SimpleMessagingFactory()#ZmqMessagingFactory()
            
            self.core = CompatibilityCore(
                self.commandQ,
                self.resultQ,
                graph_builder,
                script_factory,
                messaging_factory,
                graph_spec,
                threaded=True,
                issue_handler=self.issue_handler,
                model_id=model_id
            )            
            
        try:
            logger.debug("Starting core..." + repr(self.core))                                
            self.cThread=CoreThread(self.core.run, self.issue_handler)
            self.cThread.daemon = True
            self.cThread.start_with_traces()
            # self.cThread.start()
        except Exception as e:
            message = "Could not boot up the new thread to run the computations on because of: " + str(e)
            with self.issue_handler.create_issue(message, e) as issue:
                self.issue_handler.put_error(issue.frontend_message)
                logger.error(issue.internal_message)
                
        self.status="Running"
            
        return {"content":"core started"}

    def Pause(self):
        if self._core_mode == 'v1':
            self.commandQ.put('pause')
        else:
            self.commandQ.put(
                CoreCommand(
                    type='pause',
                    parameters={'paused': True},
                    allow_override=True
                )
            )
            
        self.paused=True
        return {"content": "Paused"}
        
    def Unpause(self):
        if self._core_mode == 'v1':
            self.commandQ.put('unpause')
        else:
            self.commandQ.put(
                CoreCommand(
                    type='pause',
                    parameters={'paused': False},
                    allow_override=True
                )
            )
        self.paused=False
        return {"content":"Unpaused"}

    def headless(self, On):
        if self._core_mode == 'v1':
            if On:
                self.commandQ.put("headlessOn")
            else:
                self.commandQ.put("headlessOff")                
        else:        
            self.commandQ.put(
                CoreCommand(
                    type='headless',
                    parameters={'on': On},
                    allow_override=True
                )
            )

    def headlessOn(self):
        if self._core_mode == 'v1':
            self.commandQ.put("headlessOn")
        else:
            self.commandQ.put(
                CoreCommand(
                    type='headless',
                    parameters={'on': True},
                    allow_override=True
                )
        )        

    def headlessOff(self):
        if self._core_mode == 'v1':
            self.commandQ.put("headlessOff")
        else:
            self.commandQ.put(
                CoreCommand(
                    type='headless',
                    parameters={'on': False},
                    allow_override=True
                )
            )        
        
    def Close(self):
        if self._core_mode == 'v1':
            self.Stop()
        else:
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

    def Stop(self):
        self.status="Stop"

        if self._core_mode == 'v1':
            self.commandQ.put('stop')
        else:
            self.commandQ.put(
                CoreCommand(
                    type='stop',
                    parameters=None,
                    allow_override=False
                )
            )
        return {"content":"Stopping"}

    def checkCore(self):
        return {"content":"Alive"}

    def isRunning(self):
        if self.cThread is not None and self.cThread.isAlive():
            return { "content": True }
        else:
            return { "content": False }

    def isTrained(self):
        is_trained = (
            (self._core_mode == 'v1' and self.saver is not None) or
            (self._core_mode == 'v2' and self.core is not None and self.resultDict is not None)
        )
        return {"content": is_trained}

    def exportNetwork(self,value):
        logger.debug(f"exportNetwork called. Value = {pprint.pformat(value)}")

        # Keys in 'value' : 
        # ['Location', 'Type', 'Compressed', 'frontendNetwork', 'NotebookJson']

        if value["Type"] == 'ipynb':
            return self.saveIpynbToDisk(value)

        # For value["Type"] = 'TFModel'
        if self._core_mode == 'v1':
            return self.exportNetworkV1(value)
        else:
            return self.exportNetworkV2(value)            

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

    def exportNetworkV2(self, value):
        path = os.path.join(value["Location"], value.get('frontendNetwork', self.networkName))
        path = os.path.abspath(path)

        mode = 'TFModel+checkpoint' # Default mode. # TODO: perhaps all export modes should be exposed to frontend?
        if value["Compressed"]:
            mode = 'TFLite+checkpoint'         

        self.commandQ.put(
            CoreCommand(
                type='export',
                parameters={'path': path, 'mode': mode},
                allow_override=False
            )
        )
        return {"content": f"Exporting model to path {path}"}
        
    def exportNetworkV1(self,value):        
        if self.saver is None:
            self._logAndWarningQueue("Export failed.\nMake sure you have started running the network before you try to Export it.")
            return {"content":"Export Failed.\nNo trained weights to Export."}
        try:
            exporter = exportNetwork(self.saver)
            if value["Type"]=="TFModel":
                if "frontendNetwork" in value:
                    path=os.path.abspath(value["Location"]+"/"+value["frontendNetwork"])
                else:
                    path=os.path.abspath(value["Location"]+"/"+str(self.networkName))
                if value["Compressed"]:
                    exporter.asCompressedTfModel(path)
                else:
                    exporter.asTfModel(path,self.epoch)
                return {"content":"Export success!\nSaved as:\n" + path}
            
        except Exception as e:
            message = "Export failed with this error: " + str(e)
            with self.issue_handler.create_issue(message, e) as issue:
                self.issue_handler.put_warning(issue.frontend_message)
                logger.warning(issue.internal_message)
                return {"content": self.issue_handler.frontend_message}

    def saveNetwork(self, value):
        """ Saves json network to disk and exports tensorflow model+checkpoints. """
        self._save_counter += 1
        path = os.path.abspath(value["Location"][0])
        
        if not os.path.exists(path):   
            os.mkdir(path)
            
        frontend_network = value['frontendNetwork'].copy()

        if self.isTrained():
            #export_path = os.path.join(path, '1')            
            self.core.core_v2.export(path, mode='TFModel+checkpoint') # TODO: will all types of graphs support this?

            # The following is used to restore the checkpoint when the saved network is loaded again.. networkElementList is the usual json_network, but with some extra frontend stuff.
            for id_ in frontend_network['networkElementList'].keys():
                frontend_network['networkElementList'][id_]['checkpoint'] = [None, os.path.join(path, 'model.ckpt-'+str(self._save_counter))] 

        with open(os.path.join(path, 'model.json'), 'w') as json_file:
            json.dump(frontend_network, json_file, indent=4)        
            
        return {"content": f"Saving to: {path}"}            
        

    def skipValidation(self):
        self.commandQ.put("skip")
        logger.warning('skipValidation called... incompatible with core v2')
        #Check if validation was skipped or not before returning message
        return {"content":"skipped validation"}

    def getTestStatus(self):
        try:
            if self.savedResultsDict["maxTestIter"]!=0:
                if self.status=="Running":
                    return {"Status":self.savedResultsDict["trainingStatus"],"Iterations":self.testIter, "Progress": self.testIter/(self.savedResultsDict["maxTestIter"]-1)}
                else:
                    return {"Status":self.status,"Iterations":self.testIter, "Progress": self.testIter/(self.savedResultsDict["maxTestIter"]-1)}
            else:
                return {"content":"Max Test Iterations are 0"}
        except KeyError:
            return {}

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
        except KeyError:
            return {}

    def startTest(self):
        #TODO: Remove this function
        if self.savedResultsDict["trainingStatus"]=='Testing' or self.savedResultsDict["trainingStatus"]=='Finished':
            return {"content":"Started Testing"}
        else:
            return {"content":"No test data"}

    def nextStep(self):
        if self.testIter<self.maxTestIter-1:
            self.testIter+=1
        else:
            self.resetTest()
        return {"content":"Current sample is: "+str(self.testIter)}
    
    def previousStep(self):
        if self.testIter>0:
            self.testIter-=1
        return {"content":"Current sample is: "+str(self.testIter)}

    def resetTest(self):
        self.testIter=0
        return {"content":"Test is now back to iter 1"}

    def isTestPlaying(self):
        return self.playing

    def increaseStep(self):
        while self.testIter<self.maxTestIter-1:
            if not self.playing:
                return
            self.testIter+=1
            time.sleep(2.0)
        self.playing=False
        return

    def playTest(self):
        if self.playCounter:
            self.playing=False
            self.playCounter.join()
            self.playCounter=None
        else:
            self.playing=True
            self.playCounter=threading.Thread(target=self.increaseStep)
            self.playCounter.start()

        return {"content": "Play started"}
        
    def scheduleAggregations(self, engine: AggregationEngine, requests: List[AggregationRequest]):
        """ Schedules a batch of metric aggregations 
        
        Args:
            engine: Aggregation Engine to computate
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
        
        # if not self.resultQ.empty():
        #     self.savedResultsDict.update(self.resultQ.get())
        #     with self.resultQ.mutex:
        #         self.resultQ.queue.clear()

        #TODO: Look from the back and go forward if we find a test instead of going through all of them
        tmp=None

        count = 0
        while not self.resultQ.empty():
            tmp = self.resultQ.get()

            if "saver" in tmp:
                self.saver=tmp.pop("saver")

            if "testDict" in tmp:
                self.testList.append(tmp["testDict"])
                if not self.maxTestIter:
                    self.maxTestIter = tmp['maxTestIter']

            if 'testDicts' in tmp:
                self.testList = tmp["testDicts"]
                self.maxTestIter = tmp['maxTestIter']

            count += 1

        if count > 0:
            logger.debug(f"Got {count} items from resultQ. len(tmp) == {len(tmp)}")        
            
        if tmp:
            self.savedResultsDict.update(tmp)
            

        return {"content":"Results saved"}

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


    def getTestingStatistics(self,value):
        layer_id = value["layerId"]
        layer_type = value["layerType"]
        view = value["view"]
        
        try:
            self.batch_size=1
            self.resultDict=self.testList[self.testIter]
        except IndexError:
            #TODO: There should never be able to be an index error here.
            logger.exception("Error in getTestingStatistics")
            return {}
        except KeyError:
            logger.exception("Error in getTestingStatistics")
            return {}

        try:
            layer_statistics = self.getLayerStatistics(layer_id, layer_type, view)            
            return layer_statistics
        except:
            message = f"Error in getTestingStatistics. layer_id = {layer_id}, layer_type = {layer_type}, view = {view}."            
            if logger.isEnabledFor(logging.DEBUG):
                message += " savedResultsDict: " + pprint.pformat(self.savedResultsDict)
            logger.exception(message)

    def getEndResults(self):
        #TODO: Show in frontend results for each end layer, not just for one.
        end_results={}
        for id_, layer_spec in self.graph_spec.items():
            if layer_spec.type_ == "TrainNormal":
                acc_train=self.getStatistics({"layerId":id_, "variable":"acc_training_epoch","innervariable":""})
                acc_val=self.getStatistics({"layerId":id_, "variable":"acc_validation_epoch","innervariable":""})
                loss_train=self.getStatistics({"layerId":id_, "variable":"loss_training_epoch","innervariable":""})
                loss_val=self.getStatistics({"layerId":id_, "variable":"loss_validation_epoch","innervariable":""})
                end_results.update({1:{"Training": {"Accuracy Training":float(acc_train[-1]*100), "Loss Training":float(loss_train[-1])}}, 2:{"Validation": {"Accuracy Validation":float(acc_val[-1]*100), "Loss Validation":float(loss_val[-1])}}})
            elif layer_spec.type_ == "TrainDetector":
                acc_train=self.getStatistics({"layerId":id_, "variable":"acc_training_epoch","innervariable":""})
                acc_val=self.getStatistics({"layerId":id_, "variable":"acc_validation_epoch","innervariable":""})
                loss_train=self.getStatistics({"layerId":id_, "variable":"loss_training_epoch","innervariable":""})
                loss_val=self.getStatistics({"layerId":id_, "variable":"loss_validation_epoch","innervariable":""})
                end_results.update({1:{"Training": {"Accuracy Training":float(acc_train[-1]*100), "Loss Training":float(loss_train[-1])}}, 2:{"Validation": {"Accuracy Validation":float(acc_val[-1]*100), "Loss Validation":float(loss_val[-1])}}})
            elif layer_spec.type_ == "TrainReinforce":
                loss_train=self.getStatistics({"layerId":id_, "variable":"loss_training_episode","innervariable":""})
                reward_train=self.getStatistics({"layerId":id_, "variable":"reward_training_episode","innervariable":""})
                end_results.update({1:{"Training": {"loss_train":float(loss_train[-1]), "reward_train":float(reward_train[-1])}}})
            elif layer_spec.type_ == "TrainGan":
                gen_loss_train=self.getStatistics({"layerId":id_, "variable":"gen_loss_training_epoch","innervariable":""})
                gen_loss_val=self.getStatistics({"layerId":id_, "variable":"gen_loss_validation_epoch","innervariable":""})
                dis_loss_train=self.getStatistics({"layerId":id_, "variable":"dis_loss_training_epoch","innervariable":""})
                dis_loss_val=self.getStatistics({"layerId":id_, "variable":"dis_loss_validation_epoch","innervariable":""})
                end_results.update({1:{"Training":{"Generator Loss Training":float(gen_loss_train[-1]), "Discriminator Loss Training":float(dis_loss_train[-1])}}, 2:{"Validation":{"Generator Loss Validation":float(gen_loss_val[-1]), "Discriminator Loss Validation":float(dis_loss_val[-1])}}})
            elif layer_spec.type_ == "TrainRegression":
                r_sq_train=self.getStatistics({"layerId":id_, "variable":"r_sq_train_epoch","innervariable":""})
                r_sq_val=self.getStatistics({"layerId":id_, "variable":"r_sq_validation_epoch","innervariable":""})
                loss_train=self.getStatistics({"layerId":id_, "variable":"loss_train_epoch","innervariable":""})
                loss_val=self.getStatistics({"layerId":id_, "variable":"loss_validation_epoch","innervariable":""})
                end_results.update({1: {"Training": {"R Squared Training":float(r_sq_train[-1]) * 100, "Loss Training":float(loss_train[-1])}}, 2: {"Validation":{"R Squared Validation":float(r_sq_val[-1]) * 100, "Loss Validation":float(loss_val[-1])}}})
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
        # elif layerType=="MathSwitch":
        #     D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})           
        #     dataObj = createDataObject([D[-1]])      
        #     return {"Data":dataObj}
        elif layerType=="DeepLearningFC":
            if view=="Output":
                D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
                dataObject = createDataObject([D])                
                output = {"Output": dataObject}
                return output
            if view=="Weights&Bias":
                w=self.getStatistics({"layerId":layerId,"variable":"W","innervariable":""})
                w=np.average(w,axis=0)
                dataObjectWeights = createDataObject([w], typeList=['line'])
                
                b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                dataObjectBias = createDataObject([b], typeList=['line'])
                
                output = {"Bias": dataObjectBias, "Weights": dataObjectWeights}
                return output
            if view=="Gradients":
                minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})

                dataObj = createDataObject([minD, maxD, avD],
                                           typeList=3*['line'],
                                           nameList=['Min', 'Max', 'Average'],
                                           styleList=[{"color":"#83c1ff"},
                                                      {"color":"#0070d6"},
                                                      {"color":"#6b8ff7"}])
                output = {"Gradients": dataObj}
                return output
        elif layerType=="DeepLearningConv":
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
                outputs=outputs[:, :, 0]
                    
                dataObjWeights = createDataObject([weights], typeList=['heatmap'])
                dataObjOutput = createDataObject([outputs])                

                obj = {"Weights":dataObjWeights, "Output": dataObjOutput}
                return obj
            if view=="Bias":
                b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                dataObj = createDataObject([b], typeList=['line'])
                output = {"Bias": dataObj}
                return output
            if view=="Gradients":
                minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})

                dataObj = createDataObject([minD, maxD, avD],
                                           typeList=3*['line'],
                                           nameList=['Min', 'Max', 'Average'],
                                           styleList=[{"color":"#83c1ff"},
                                                      {"color":"#0070d6"},
                                                      {"color":"#6b8ff7"}])
                output = {"Gradients": dataObj}
                return output
        elif layerType=="DeepLearningDeconv":
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
                outputs=outputs[:, :, 0]
                    
                dataObjWeights = createDataObject([weights], typeList=['heatmap'])
                dataObjOutput = createDataObject([outputs])                

                obj = {"Weights":dataObjWeights, "Output": dataObjOutput}
                return obj
            if view=="Bias":
                b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                dataObj = createDataObject([b], typeList=['line'])
                output = {"Bias": dataObj}
                return output
            if view=="Gradients":
                minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})

                dataObj = createDataObject([minD, maxD, avD],
                                           typeList=3*['line'],
                                           nameList=['Min', 'Max', 'Average'],
                                           styleList=[{"color":"#83c1ff"},
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

            # if view=="Weights&Bias":
            #     # w=self.getStatistics({"layerId":layerId,"variable":"W","innervariable":""})
            #     # w=np.average(w,axis=0)
            #     w=np.array([])
            #     # b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
            #     b=np.array([])
                
            #     dataObjectWeights = createDataObject([w], typeList=['line'])
            #     dataObjectBias = createDataObject([b], typeList=['line'])
                
            #     output = {"Bias": dataObjectBias, "Weights": dataObjectWeights}
            #     return output
            # if view=="Gradients":
            #     # minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
            #     # maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
            #     # avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})
            #     minD=np.array([])
            #     maxD=np.array([])
            #     avD=np.array([])

            #     dataObj = createDataObject([minD, maxD, avD],
            #                                typeList=3*['line'],
            #                                nameList=['Min', 'Max', 'Average'],
            #                                styleList=[{"color":"#83c1ff"},
            #                                           {"color":"#0070d6"},
            #                                           {"color":"#6b8ff7"}])
            #     output = {"Gradients": dataObj}
                # return output

        elif layerType in ["MathMerge", "MathSoftmax", "MathArgmax", "MathSwitch", "ProcessOneHot", "ProcessCrop", "ProcessReshape", "ProcessRescale"]:
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

        elif layerType=="TrainRegression":
            if view=="Prediction":
                #Make sure that all the inputs are sent to frontend!!!!!!!!!!!!!!!
                inputs=[self.getStatistics({"layerId": node.id_,"variable":"Y","innervariable":""}) for node in self.graph_spec.get_start_nodes()]
                D = [createDataObject([input_]) for input_ in inputs]
                
                X = self.getStatistics({"layerId": layerId, "variable":"X", "innervariable":""})

                if type(X) is dict and type(list(X.values())[0]) is dict and len(list(X.values()))==2:
                    input1_name, input2_name = X.keys()

                    labels_spec = self.graph_spec[self.graph_spec[layerId].connection_labels.src_id]
                    preds_spec = self.graph_spec[self.graph_spec[layerId].connection_predictions.src_id]

                    network_output = X[labels_spec.name]['Y']
                    labels = X[labels_spec.name]['Y']

                    output_id = preds_spec.id_
                    labels_id = labels_spec.id_
                    
                    labels_data_id = self.graph_spec.get_origin(labels_spec)[0].id_
                    input_data_id = self.graph_spec.get_origin(preds_spec)[0].id_
                        
                    label_data = self.getStatistics({"layerId": labels_data_id, "variable":"Y", "innervariable":""})
                    input_data = self.getStatistics({"layerId": input_data_id, "variable":"Y", "innervariable":""})


                    cType=self.getPlot(network_output[-1])
                    if cType=="bar" or cType=="line" or cType=='scatter':
                        PvG = createDataObject([network_output[-1], labels[-1]], nameList=['Prediction', 'True Output'])                        
                        # average over samples
                        # network_average=np.average(network_output,axis=0)
                        # labels_average = np.average(labels, axis=0)
                        
                        output = self.getStatistics({"layerId": output_id, "variable":"W", "innervariable":""})
                        bias = self.getStatistics({"layerId": output_id, "variable":"b", "innervariable":""})

                        # line=np.arange(np.min(input_data),np.max(input_data))*output+bias
                        minval = np.min(input_data) if np.min(input_data)<0 else 0
                        maxval = np.max(input_data) if np.max(input_data)>0 else 0
                        # line=[[minval, minval*output+bias], [maxval, maxval*output+bias]]
                        x = np.asarray([minval, maxval]).reshape(1,-1)
                        # import pdb; pdb.set_trace()
                        if(len(output) > 0 and len(bias) > 0):
                            y = x*output+bias
                        elif len(output) > 0 and len(bias) == 0:
                            y = x * output
                        elif len(bias) > 0 and len(output) == 0:
                            y = x + bias
                        else:
                            y = x
                        line = np.concatenate((x,y)).transpose().tolist()
                        

                        APvT = {
                            "xLength": float(maxval),
                            "series": [
                                {
                                "data": np.asarray([input_data,label_data]).reshape(-1,2).tolist(),
                                "type": 'scatter'
                            },
                            {
                                "data": line,
                                "type": 'line'
                            }
                            ]
                        }

                        
                        # PIE
                        r_sq_train=self.getStatistics({"layerId":layerId,"variable":"r_sq_train_iter","innervariable":""})
                        r_sq_val=self.getStatistics({"layerId":layerId,"variable":"r_sq_validation_iter","innervariable":""})

                        if r_sq_val!=[]:
                            r_sq=r_sq_val
                        else:
                            r_sq=r_sq_train

                        try:
                            last_r_sq=r_sq[-1]
                        except:
                            last_r_sq=r_sq

                        # r_sq_list = [[('R_Squared', last_r_sq), ('Empty', (1-last_r_sq))]]
                        R_Squared = createDataObject([last_r_sq], typeList=['bar'])
                        returnDict={"Input":D[0],"PvG":PvG,"AveragePvT":APvT,"R_Squared":R_Squared}


                    elif cType=="grayscale" or cType=="RGB" or cType=="heatmap":
                        pass

                    else:
                        chartType="line"
                        if np.shape(X[-1])[0]<10:
                            chartType="bar"

                        APvGD=np.average(X,axis=0)
                        PvG = createDataObject([X[-1]], typeList=[chartType])
                        APvG = createDataObject([APvGD], typeList=[chartType])
                        returnDict={"Input":D[0],"PvG":PvG,"AveragePvG":APvG}

                    return returnDict

            if view == "Loss":
                loss_train=self.getStatistics({"layerId":layerId,"variable":"loss_train_iter","innervariable":""})
                loss_val=self.getStatistics({"layerId":layerId,"variable":"loss_validation_iter","innervariable":""})

                currentTraining=loss_train
                if isinstance(loss_train,np.ndarray):
                    currentValidation=np.concatenate((loss_train,np.asarray(loss_val)))
                elif isinstance(loss_train,list):
                    if isinstance(loss_val,list):
                        currentValidation=loss_train+loss_val
                    else:
                        currentValidation=loss_train+list(loss_val)

                totalTraining=self.getStatistics({"layerId":layerId,"variable":"loss_train_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"loss_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                    typeList=['line', 'line'],
                                                    nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                typeList=['line', 'line'],
                                                nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output

            if view == "R_Squared":
                r_sq_train=self.getStatistics({"layerId":layerId,"variable":"r_sq_train_iter","innervariable":""})
                r_sq_val=self.getStatistics({"layerId":layerId,"variable":"r_sq_validation_iter","innervariable":""})
                currentTraining=r_sq_train

                if isinstance(r_sq_train,np.ndarray):
                    currentValidation=np.concatenate((r_sq_train,np.asarray(r_sq_val)))
                elif isinstance(r_sq_train,list):
                    if isinstance(r_sq_val,list):
                        currentValidation=r_sq_train+r_sq_val
                    else:
                        currentValidation=r_sq_train+list(r_sq_val)

                totalTraining=self.getStatistics({"layerId":layerId,"variable":"r_sq_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"r_sq_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                    typeList=['line', 'line'],
                                                    nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                typeList=['line', 'line'],
                                                nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output                   

        elif layerType=="TrainNormal":
            if view=="Prediction":
                #Make sure that all the inputs are sent to frontend!!!!!!!!!!!!!!!
                inputs=[self.getStatistics({"layerId": node.id_,"variable":"Y","innervariable":""})[-1] for node in self.graph_spec.get_start_nodes()]
                D = [createDataObject([input_]) for input_ in inputs]
                
                X = self.getStatistics({"layerId": layerId, "variable":"X", "innervariable":""})

                if type(X) is dict and type(list(X.values())[0]) is dict and len(list(X.values()))==2:
                    input1_name, input2_name = X.keys()

                    labels_id = self.graph_spec[self.graph_spec[layerId].connection_labels.src_id].name
                    preds_id = self.graph_spec[self.graph_spec[layerId].connection_predictions.src_id].name

                    network_output = X[preds_id]['Y']
                    labels = X[labels_id]['Y']                    
                    
                    
                    '''
                    bw_cons = {name: id_ for id_, name in self.graphObj[layerId]['backward_connections']}                    
                    input1_id = bw_cons[input1_name]
                    input2_id = bw_cons[input2_name]

                    if input1_id == self.graphObj[layerId]["Properties"]["Labels"]:
                        labels = X[input1_name]['Y']
                        network_output = X[input2_name]['Y']
                    else:
                        network_output = X[input1_name]['Y']
                        labels = X[input2_name]['Y']                        
                    '''
                    
                    cType=self.getPlot(network_output[-1])
                    if cType=="bar" or cType=="line" or cType=='scatter':
                        PvG = createDataObject([network_output[-1], labels[-1]], nameList=['Prediction', 'Ground Truth'])                        
                        # average over samples
                        network_average=np.average(network_output,axis=0)
                        labels_average = np.average(labels, axis=0)
                        APvG = createDataObject([network_average, labels_average], nameList=['Prediction', 'Ground Truth'])
                        
                        # PIE
                        acc_train=self.getStatistics({"layerId":layerId,"variable":"acc_train_iter","innervariable":""})
                        acc_val=self.getStatistics({"layerId":layerId,"variable":"acc_val_iter","innervariable":""})

                        if acc_val!=[]:
                            acc=acc_val
                        else:
                            acc=acc_train

                        try:
                            lastAcc=acc[-1]
                        except:
                            lastAcc=acc

                        accList = [[('Accuracy', lastAcc*100.0), ('Empty', (1-lastAcc)*100.0)]]
                        Accuracy = createDataObject(accList, typeList=['pie'])
                        returnDict={"Input":D[0],"PvG":PvG,"AveragePvG":APvG,"Accuracy":Accuracy}

                    elif cType=="grayscale" or cType=="RGB" or cType=="heatmap":
                        pass
                        # network_output=self.subsample(network_output)
                        # Labels=self.subsample(labels)
                        # (height,width)=network_output.shape[0:2]
                        # Mask = createDataObject([network_output], typeList=['heatmap'])
                        # Prediction = createDataObject([labels], typeList=['heatmap'])
                        
                        # # PIE
                        # acc=self.getStatistics({"layerId":layerId,"variable":"accuracy","innervariable":""})
                        # try:
                        #     lastAcc=acc[-1]
                        # except:
                        #     lastAcc=acc

                        # accList = [[('Accuracy', lastAcc*100.0), ('Empty', (1-lastAcc)*100.0)]]
                        # Accuracy = createDataObject(accList, typeList=['pie'])
                        # returnDict={"Input":D[0],"PvG":Mask,"AveragePvG":Prediction,"Accuracy":Accuracy}    
                                    
                else:
                    chartType="line"
                    if np.shape(X[-1])[0]<10:
                        chartType="bar"

                    APvGD=np.average(X,axis=0)
                    PvG = createDataObject([X[-1]], typeList=[chartType])
                    APvG = createDataObject([APvGD], typeList=[chartType])
                    returnDict={"Input":D[0],"PvG":PvG,"AveragePvG":APvG}
                return returnDict

            if view=="Accuracy":
                acc_train=self.getStatistics({"layerId":layerId,"variable":"acc_train_iter","innervariable":""})
                acc_val=self.getStatistics({"layerId":layerId,"variable":"acc_val_iter","innervariable":""})

                currentTraining=acc_train
                if isinstance(acc_train,np.ndarray):
                    currentValidation=np.concatenate((acc_train,np.asarray(acc_val)))
                elif isinstance(acc_train,list):
                    if isinstance(acc_val,list):
                        currentValidation=acc_train+acc_val
                    else:
                        currentValidation=acc_train+list(acc_val)
                
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"acc_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"acc_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
                
            if view=="Loss":
                loss_train=self.getStatistics({"layerId":layerId,"variable":"loss_train_iter","innervariable":""})
                loss_val=self.getStatistics({"layerId":layerId,"variable":"loss_val_iter","innervariable":""})

                currentTraining=loss_train
                if isinstance(loss_train,np.ndarray):
                    currentValidation=np.concatenate((loss_train,np.asarray(loss_val)))
                elif isinstance(loss_train,list):
                    if isinstance(loss_val,list):
                        currentValidation=loss_train+loss_val
                    else:
                        currentValidation=loss_train+list(loss_val)

                totalTraining=self.getStatistics({"layerId":layerId,"variable":"loss_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"loss_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view=="F1":
                f1_train=self.getStatistics({"layerId":layerId,"variable":"f1_train_iter","innervariable":""})
                f1_val=self.getStatistics({"layerId":layerId,"variable":"f1_val_iter","innervariable":""})

                currentTraining=f1_train
                if isinstance(f1_train,np.ndarray):
                    currentValidation=np.concatenate((f1_train,np.asarray(f1_val)))
                elif isinstance(f1_train,list):
                    if isinstance(f1_val,list):
                        currentValidation=f1_train+f1_val
                    else:
                        currentValidation=f1_train+list(f1_val)
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"f1_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"f1_validation_epoch","innervariable":""})



                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view=="Precision&Recall":
                pr=self.getStatistics({"layerId":layerId,"variable":"p_and_r","innervariable":""})

                currentTraining=pr[:self.trainingIterations]
                currentValidation=pr[:self.maxIter]
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"epochTrainPandR","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"epochValFPandR","innervariable":""})
                
                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view=="ROC":
                roc=self.getStatistics({"layerId":layerId,"variable":"roc","innervariable":""})

                currentTraining=roc[:self.trainingIterations]
                currentValidation=roc[:self.maxIter]
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"epochTrainROC","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"epochValROC","innervariable":""})
                
                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output            
            if view=="AUC":
                auc_train=self.getStatistics({"layerId":layerId,"variable":"auc_train_iter","innervariable":""})
                auc_val=self.getStatistics({"layerId":layerId,"variable":"auc_val_iter","innervariable":""})

                currentTraining=auc_train
                if isinstance(auc_train,np.ndarray):
                    currentValidation=np.concatenate((auc_train,np.asarray(auc_val)))
                elif isinstance(auc_train,list):
                    if isinstance(auc_val,list):
                        currentValidation=auc_train+auc_val
                    else:
                        currentValidation=auc_train+list(auc_val)
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"auc_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"auc_validation_epoch","innervariable":""})


                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output

        elif layerType=="TrainDetector":
            if view=="Prediction":
                #Make sure that all the inputs are sent to frontend!!!!!!!!!!!!!!!
                
                image = self.getStatistics({"layerId": layerId, "variable":"image_bboxes", "innervariable":""})
                # image = np.random.randint(0,255,[224,224,3])
                Bboxes = createDataObject([image])    


                # Confidence of the boxes in sample
                confidence_scores = self.getStatistics({"layerId":layerId,"variable":"confidence_scores","innervariable":""})
                Confidence = createDataObject([confidence_scores], typeList=['bar'])
                
                # PIE
                acc=self.getStatistics({"layerId":layerId,"variable":"image_accuracy","innervariable":""})[0]
                accList = [[('Accuracy', acc*100.0), ('Empty', (1-acc)*100.0)]]
                Accuracy = createDataObject(accList, typeList=['pie'])

                returnDict={"Bboxes":Bboxes,"Confidence":Confidence,"Accuracy":Accuracy}
                return returnDict
                
            if view=="Accuracy":
                acc_train=self.getStatistics({"layerId":layerId,"variable":"acc_train_iter","innervariable":""})
                acc_val=self.getStatistics({"layerId":layerId,"variable":"acc_val_iter","innervariable":""})

                currentTraining=acc_train
                if isinstance(acc_train,np.ndarray):
                    currentValidation=np.concatenate((acc_train,np.asarray(acc_val)))
                elif isinstance(acc_train,list):
                    if isinstance(acc_val,list):
                        currentValidation=acc_train+acc_val
                    else:
                        currentValidation=acc_train+list(acc_val)
                
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"acc_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"acc_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
                
            if view=="Loss":
                loss_train=self.getStatistics({"layerId":layerId,"variable":"loss_train_iter","innervariable":""})
                loss_val=self.getStatistics({"layerId":layerId,"variable":"loss_val_iter","innervariable":""})

                currentTraining=loss_train
                if isinstance(loss_train,np.ndarray):
                    currentValidation=np.concatenate((loss_train,np.asarray(loss_val)))
                elif isinstance(loss_train,list):
                    if isinstance(loss_val,list):
                        currentValidation=loss_train+loss_val
                    else:
                        currentValidation=loss_train+list(loss_val)

                totalTraining=self.getStatistics({"layerId":layerId,"variable":"loss_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"loss_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            
            if view=="ClassificationLoss":
                classification_loss_train=self.getStatistics({"layerId":layerId,"variable":"classification_loss_train_iter","innervariable":""})
                classification_loss_val=self.getStatistics({"layerId":layerId,"variable":"classification_loss_val_iter","innervariable":""})

                currentTraining=classification_loss_train
                if isinstance(classification_loss_train,np.ndarray):
                    currentValidation=np.concatenate((classification_loss_train,np.asarray(classification_loss_val)))
                elif isinstance(classification_loss_train,list):
                    if isinstance(classification_loss_val,list):
                        currentValidation=classification_loss_train+classification_loss_val
                    else:
                        currentValidation=classification_loss_train+list(classification_loss_val)
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"classification_loss_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"classification_loss_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            
            if view=="BoundingBoxesLoss":
                bbox_loss_train=self.getStatistics({"layerId":layerId,"variable":"bboxes_loss_train_iter","innervariable":""})
                bbox_loss_val=self.getStatistics({"layerId":layerId,"variable":"bboxes_loss_val_iter","innervariable":""})

                currentTraining=bbox_loss_train
                if isinstance(bbox_loss_train,np.ndarray):
                    currentValidation=np.concatenate((bbox_loss_train,np.asarray(bbox_loss_val)))
                elif isinstance(bbox_loss_train,list):
                    if isinstance(bbox_loss_val,list):
                        currentValidation=bbox_loss_train+bbox_loss_val
                    else:
                        currentValidation=bbox_loss_train+list(bbox_loss_val)
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"bboxes_loss_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"bboxes_loss_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output

        elif layerType=="TrainGan":
            
            if view=="Generator_Loss":
                loss_train=self.getStatistics({"layerId":layerId,"variable":"gen_loss_train_iter","innervariable":""})
                loss_val=self.getStatistics({"layerId":layerId,"variable":"gen_loss_val_iter","innervariable":""})

                currentTraining=loss_train
                if isinstance(loss_train,np.ndarray):
                    currentValidation=np.concatenate((loss_train,np.asarray(loss_val)))
                elif isinstance(loss_train,list):
                    if isinstance(loss_val,list):
                        currentValidation=loss_train+loss_val
                    else:
                        currentValidation=loss_train+list(loss_val)

                totalTraining=self.getStatistics({"layerId":layerId,"variable":"gen_loss_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"gen_loss_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            
            if view=="Discriminator_Loss":
                loss_train=self.getStatistics({"layerId":layerId,"variable":"dis_loss_train_iter","innervariable":""})
                loss_val=self.getStatistics({"layerId":layerId,"variable":"dis_loss_val_iter","innervariable":""})

                currentTraining=loss_train
                if isinstance(loss_train,np.ndarray):
                    currentValidation=np.concatenate((loss_train,np.asarray(loss_val)))
                elif isinstance(loss_train,list):
                    if isinstance(loss_val,list):
                        currentValidation=loss_train+loss_val
                    else:
                        currentValidation=loss_train+list(loss_val)

                totalTraining=self.getStatistics({"layerId":layerId,"variable":"dis_loss_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"dis_loss_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view == "Images":
                generated_sample=self.getStatistics({"layerId":layerId,"variable":"generated_image","innervariable":""})

                dataObjectOutput = createDataObject([generated_sample])
                
                real_sample=self.getStatistics({"layerId":layerId,"variable":"real_image","innervariable":""})

                dataObjectInput = createDataObject([real_sample])
            
    
                output = { "Real_Input":dataObjectInput, "Generated_Output": dataObjectOutput}

                return output
            
            if view=="Data_distribution":
                data_distribution = self.getStatistics({"layerId":layerId,"variable":"data_distribution","innervariable":""})
                dataObjectOutput = createDataObject([data_distribution])
    
                output = {"Data_distribution": dataObjectOutput}
                return output
                  
        elif layerType=="TrainReinforce":
            if view=="Prediction":
                state = self.getStatistics({"layerId":layerId,"variable":"state","innervariable":""})
                state_ = createDataObject([state])

                prediction = self.getStatistics({"layerId":layerId,"variable":"pred","innervariable":""})
                probs = self.getStatistics({"layerId":layerId,"variable":"probs","innervariable":""})
                prediction = createDataObject([prediction, probs], 
                                            typeList=['bar', 'line'], 
                                            nameList= ['taken action', 'probabilities'],
                                            styleList=[{"color":"#83c1ff"},
                                                      {"color":"#0070d6"}])
                
                output = {"Input":state_, "Prediction": prediction}
                return output

            if view=="Reward":
                currentReward=self.getStatistics({"layerId":layerId,"variable":"reward_train_iter","innervariable":""})
                totalReward=self.getStatistics({"layerId":layerId,"variable":"reward_training_episode","innervariable":""})
                current_reward = createDataObject([currentReward],
                                                typeList=['line'])
                total_reward = createDataObject([totalReward],
                                                typeList=['line'])
                obj = {"Current": current_reward, "Total": total_reward}
                return obj
            if view=="Loss":
                loss_train=self.getStatistics({"layerId":layerId,"variable":"loss_train_iter","innervariable":""})
                currentTraining=loss_train

                totalTraining=self.getStatistics({"layerId":layerId,"variable":"loss_training_episode","innervariable":""})
            
                dataObjectCurrent = createDataObject([currentTraining],
                                                     typeList=['line'],
                                                     nameList=['Training'])
            
                dataObjectTotal = createDataObject([totalTraining],
                                                   typeList=['line'],
                                                   nameList=['Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view=="Steps":
                steps=self.getStatistics({"layerId":layerId,"variable":"Steps","innervariable":""})
                steps = createDataObject([steps])
                obj = {"Steps": steps}
                return obj
        else:
            return "FieldError: Does not recognize the layerType. " + layerType + " is not in [Train, Fc, Conv, Deconv, Argmax, Softmax, Merge, OneHot, Crop, Reshape, Grayscale]"

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

    # def recursive_items(self,dictionary):
    #     for key, value in dictionary.items():
    #         if type(value) is dict:
    #             yield from self.recursive_items(value)
    #         else:
    #             yield (key, value)

    def getStatistics(self,statSpec):
        if self.resultDict is not None:
            logger.debug(f"ResultDict has entries for layers {list(self.resultDict.keys())}")

        layerId=statSpec["layerId"]
        variable=statSpec["variable"]
        innervariable=statSpec["innervariable"]
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
        
        message = f"getStatistics called with:\n" \
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
