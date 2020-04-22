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

from perceptilabs.networkExporter import exportNetwork
from perceptilabs.networkSaver import saveNetwork

from perceptilabs.modules import ModuleProvider
from perceptilabs.core_new.core import *
from perceptilabs.core_new.data import DataContainer
from perceptilabs.core_new.cache import get_cache
from perceptilabs.core_new.errors import CoreErrorHandler
from perceptilabs.core_new.history import SessionHistory
from perceptilabs.analytics.scraper import get_scraper
from perceptilabs.CoreThread import CoreThread
from perceptilabs.createDataObject import createDataObject
from perceptilabs.core_new.core_distr import DistributedCore

from perceptilabs.license_checker import LicenseV2

log = logging.getLogger(__name__)
scraper = get_scraper()


CoreCommand = collections.namedtuple('CoreCommand', ['type', 'parameters', 'allow_override'])


class coreLogic():
    def __init__(self,networkName, core_mode='v1'):
        log.info(f"Created coreLogic for network '{networkName}' with core mode '{core_mode}'")
        
        assert core_mode in ['v1', 'v2']
        self._core_mode = core_mode
        
        self.networkName=networkName
        self.cThread=None
        self.status="Created"
        self.network=None

        self.setupLogic()
        self.plLicense = LicenseV2()
        
        self._save_counter = 0

    def setupLogic(self):
        self.warningQueue=queue.Queue()
        self.errorQueue=queue.Queue()
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
        log.warning(msg)
        self.warningQueue.put(msg)

    def gpu_list(self):
        try:
            gpus = GPUtil.getGPUs()
        except:
            log.error("No compatible nvidia GPU drivers available. Defaulting to 0 GPUs")
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

    def _dump_deployment_script(self, target_file, graph_spec):
        """
            Export code to a file. Support is limited to image classification example
            and the code will differ from the code visible in the frontend.
        """
        try:
            graph_spec = copy.deepcopy(graph_spec)

            for id_, layer in graph_spec['Layers'].items():
                if layer['Type'] == 'TrainNormal' and 'Distributed' not in layer['Properties']:
                    layer['Properties']['Distributed'] = False 
            log.info("Creating deployment script...")            
            config = {'session_id': '1234567'}
            
            from perceptilabs.core_new.graph.builder import GraphBuilder
            from perceptilabs.script.factory import ScriptFactory
            from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP                

            replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}                
            graph_builder = GraphBuilder(replica_by_name)
            graph = graph_builder.build_from_spec(graph_spec)
            
            script_factory = ScriptFactory()        
            code = script_factory.make(graph, config)
            with open(target_file, 'w') as f:
                f.write(code)
            log.info("wrote deployment script to disk...")                            
        except:
            log.exception("Failed creating deployment script...")

    def startCore(self,network, checkpointValues):
        #Start the backendthread and give it the network

        self.setupLogic()
        self.network=network
        log.debug('printing network .......\n')

        if log.isEnabledFor(logging.DEBUG):        
            import json
            with open('net.json_', 'w') as f:
                json.dump(network, f, indent=4) 

        if log.isEnabledFor(logging.DEBUG):        
            import json
            with open('net.json_', 'w') as f:
                json.dump(network, f, indent=4)
            
        data_container = DataContainer()

        def backprop(layer_id):
            backward_connections = network['Layers'][layer_id]['backward_connections']
            if backward_connections:
                id_, name = backward_connections[0]
                return backprop(id_)
            else:
                return layer_id

        #TODO: Replace len(gpus) with a frontend choice of how many GPUs (if any) they want to use
        gpus = self.gpu_list()
        distributed = self.isDistributable(gpus)
        #distributed = True

        for _id, layer in network['Layers'].items():
            if layer['Type'] == 'DataData':
                layer['Properties']['accessProperties']['Sources'][0]['path'] = layer['Properties']['accessProperties']['Sources'][0]['path'].replace('\\','/')
            if layer['Type'] == 'TrainNormal':
                layer['Properties']['Distributed'] = distributed
                if distributed:
                    targets_id = layer['Properties']['Labels']

                    for id_, name in layer['backward_connections']:
                        if id_ != targets_id:
                            outputs_id = id_
                    
                    input_data_layer = backprop(outputs_id)
                    labels_data_layer = backprop(targets_id)
                    layer['Properties']['InputDataId'] = input_data_layer
                    layer['Properties']['TargetDataId'] = labels_data_layer

                else:
                    layer['Properties']['InputDataId'] = ''
                    layer['Properties']['TargetDataId'] = ''


        self.graphObj = Graph(network['Layers'])
        graph_dict=self.graphObj.graphs

        from perceptilabs.codehq import CodeHqNew as CodeHq

        error_handler = CoreErrorHandler(self.errorQueue)
        
        module_provider = ModuleProvider()
        module_provider.load('tensorflow', as_name='tf')
        module_provider.load('numpy', as_name='np')
        module_provider.load('pandas', as_name='pd')
        module_provider.load('gym')
        module_provider.load('json')       
        module_provider.load('os')  
        module_provider.load('skimage')
        module_provider.load('dask.array', as_name='da')
        module_provider.load('dask.dataframe', as_name='dd')                  

        cache = get_cache()
        session_history = SessionHistory(cache)
        session_proc_handler = SessionProcessHandler(graph_dict, data_container, self.commandQ, self.resultQ)


        #self._dump_deployment_script('deploy.py', network) 
        


        if self._core_mode == 'v1':
            if not distributed:
                self.core = Core(CodeHq, graph_dict, data_container, session_history, module_provider,
                                error_handler, session_proc_handler, checkpointValues)
            else:
                from perceptilabs.core_new.core_distr import DistributedCore
                self.core = DistributedCore(CodeHq, graph_dict, data_container, session_history, module_provider,
                                            error_handler, session_proc_handler, checkpointValues)
        elif self._core_mode == 'v2':
            from perceptilabs.core_new.compability import CompabilityCore
            from perceptilabs.core_new.graph.builder import GraphBuilder
            from perceptilabs.core_new.deployment import InProcessDeploymentPipe, LocalEnvironmentPipe
            from perceptilabs.core_new.layers.script import ScriptFactory

            from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP                

            replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}                
            graph_builder = GraphBuilder(replica_by_name)
            
            script_factory = ScriptFactory()
            deployment_pipe = InProcessDeploymentPipe(script_factory)
            #deployment_pipe = LocalEnvironmentPipe('/home/anton/Source/perceptilabs/backend/venv-user/bin/python', script_factory)

            
            self.core = CompabilityCore(
                self.commandQ,
                self.resultQ,
                graph_builder,
                deployment_pipe,
                network,
                threaded=True,
                error_queue=self.errorQueue
            )            
            
        if self.cThread is not None and self.cThread.isAlive():
            self.Stop()

            while self.cThread.isAlive():
                time.sleep(0.05)

                
            try:
                log.debug("Starting core..." + repr(self.core))                
                self.cThread=CoreThread(self.core.run,self.errorQueue)
                self.cThread.daemon = True
                self.cThread.start_with_traces()
                # self.cThread.start()
            except Exception as e:
                message = "Could not boot up the new thread to run the computations on because of: " + str(e)
                self.errorQueue.put(message)
                log.exception(message)                
        else:
            try:
                log.debug("Starting core..." + repr(self.core))                                
                self.cThread=CoreThread(self.core.run,self.errorQueue)
                self.cThread.daemon = True
                self.cThread.start_with_traces()
                # self.cThread.start()
            except Exception as e:
                message = "Could not boot up the new thread to run the computations on because of: " + str(e)
                self.errorQueue.put(message)
                log.exception(message)
                
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
        return self.cThread is not None and self.cThread.isAlive()

    def isTrained(self):
        is_trained = (
            (self._core_mode == 'v1' and self.saver is not None) or
            (self._core_mode == 'v2' and self.core is not None and len(self.core.core_v2.graphs) > 0)
        )
        return {"content": is_trained}

    def exportNetwork(self,value):
        log.debug(f"exportNetwork called. Value = {pprint.pformat(value)}")
        if self._core_mode == 'v1':
            return self.exportNetworkV1(value)
        else:
            return self.exportNetworkV2(value)            

    def exportNetworkV2(self, value):
        path = os.path.join(value["Location"], value.get('frontendNetwork', self.networkName), '1')
        path = os.path.abspath(path)
            
        if os.path.exists(path):
            shutil.rmtree(path)

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
            self.warningQueue.put("Export failed.\nMake sure you have started running the network before you try to Export it.")
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
            self.warningQueue.put("Export Failed with this error: ")
            self.warningQueue.put(str(e))
            log.exception("Export failed")
            return {"content":"Export Failed with this error: " + str(e)}

    def saveNetwork(self, value):
        if self._core_mode == 'v1':
            return self.saveNetworkV1(value)
        else:
            return self.saveNetworkV2(value)            

    def saveNetworkV2(self, value):
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
        
    def saveNetworkV1(self, value):
        if self.saver is None:
            self.warningQueue.put("Save failed.\nMake sure you have started running the network before you try to Export it.")
            return {"content":"Save Failed.\nNo trained weights to Export."}
        try:
            if "all_tensors" not in self.saver:
                raise Exception("'all_tensors' was not found so the Saver could not create any references to the exported checkpoints.\nTry adding 'api.data.store(all_tensors=api.data.get_tensors())' to your Training Layer.")
            elif self.saver["all_tensors"]==[]:
                raise Exception("'all_tensors' was found but contained no variables.")
            exporter = exportNetwork(self.saver)
            path=os.path.abspath(value["Location"][0])
            frontendNetwork=value["frontendNetwork"]
            if not os.path.exists(path):   
                os.mkdir(path)
            checkpoint=[None, os.path.relpath(exporter.asTfModel(path,self.epoch),path)]

            newPath=os.path.abspath(path+"/"+"model.json")
            saveNetwork(newPath, self.saver["all_tensors"], self.graphObj, frontendNetwork, checkpoint)

            return {"content":"Save succeeded!"}
        except Exception as e:
            self.errorQueue.put("Save Failed with this error: ")
            self.errorQueue.put(str(e))
            log.exception("Save failed")
            return {"content":"Save Failed with this error: " + str(e)}

    def skipValidation(self):
        self.commandQ.put("skip")
        log.warning('skipValidation called... incompatible with core v2')
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
        scraper.submit('cpu_and_mem', {'cpu': cpu, 'mem': mem})
        return cpu, mem

    def get_gpu(self):
        try:
            gpus = GPUtil.getGPUs()
            loadList = [gpu.load*100 for gpu in gpus]
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
                    "Memory": mem
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
        while self.testIter<self.maxTestIter:
            if not self.playing:
                return
            self.testIter+=1
            time.sleep(0.5)
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
            log.debug(f"Got {count} items from resultQ. len(tmp) == {len(tmp)}")        
            
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
            if log.isEnabledFor(logging.DEBUG):
                message += " savedResultsDict: " + pprint.pformat(self.savedResultsDict)
            log.exception(message)
            return {}


        try:
            layer_statistics = self.getLayerStatistics(layer_id, layer_type, view)
            return layer_statistics
        except:
            message = f"Error in getTrainingStatistics. layer_id = {layer_id}, layer_type = {layer_type}, view = {view}."
            if log.isEnabledFor(logging.DEBUG):
                message += " savedResultsDict: " + pprint.pformat(self.savedResultsDict)
            log.exception(message)


    def getTestingStatistics(self,value):
        layer_id = value["layerId"]
        layer_type = value["layerType"]
        view = value["view"]
        
        try:
            self.batch_size=1
            self.resultDict=self.testList[self.testIter]
        except IndexError:
            #TODO: There should never be able to be an index error here.
            log.exception("Error in getTestingStatistics")
            return {}
        except KeyError:
            log.exception("Error in getTestingStatistics")            
            return {}

        try:
            layer_statistics = self.getLayerStatistics(layer_id, layer_type, view)            
            return layer_statistics
        except:
            message = f"Error in getTestingStatistics. layer_id = {layer_id}, layer_type = {layer_type}, view = {view}."            
            if log.isEnabledFor(logging.DEBUG):
                message += " savedResultsDict: " + pprint.pformat(self.savedResultsDict)
            log.exception(message)

    def getEndResults(self):
        #TODO: Show in frontend results for each end layer, not just for one.
        end_results={}
        for id_, value in self.graphObj.graphs.items():
            if value["Info"]["Type"]=="TrainNormal":
                acc_train=self.getStatistics({"layerId":id_, "variable":"acc_training_epoch","innervariable":""})
                acc_val=self.getStatistics({"layerId":id_, "variable":"acc_validation_epoch","innervariable":""})
                loss_train=self.getStatistics({"layerId":id_, "variable":"loss_training_epoch","innervariable":""})
                loss_val=self.getStatistics({"layerId":id_, "variable":"loss_validation_epoch","innervariable":""})
                end_results.update({"acc_train":float(acc_train[-1]*100), "acc_val":float(acc_val[-1]*100), "loss_train":float(loss_train[-1]), "loss_val":float(loss_val[-1])})

        return end_results

    
    def getLayerStatistics(self, layerId, layerType, view):
        log.debug("getLayerStatistics for layer '{}' with type '{}' and view: '{}'".format(layerId, layerType, view))
        
        if layerType=="DataEnvironment":
            state = self.getStatistics({"layerId":layerId,"variable":"state","innervariable":""})
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
        elif layerType=="MathSwitch":
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})           
            dataObj = createDataObject([D[-1]])      
            return {"Data":dataObj}
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
        elif layerType in ["MathMerge", "MathSoftmax", "MathArgmax", "ProcessOneHot", "ProcessCrop", "ProcessReshape"]:
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
            output = createDataObject([np.squeeze(D)])
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
        elif layerType=="TrainNormal":
            if view=="Prediction":
                #Make sure that all the inputs are sent to frontend!!!!!!!!!!!!!!!
                inputs=[self.getStatistics({"layerId":i,"variable":"Y","innervariable":""})[-1] for i in self.graphObj.start_nodes]
                D = [createDataObject([input_]) for input_ in inputs]
                
                X = self.getStatistics({"layerId": layerId, "variable":"X", "innervariable":""})

                if type(X) is dict and type(list(X.values())[0]) is dict and len(list(X.values()))==2:

                    input1_name, input2_name = X.keys()
                    
                    bw_cons = {name: id_ for id_, name in self.graphObj.graphs[layerId]['Info']['backward_connections']}                    
                    input1_id = bw_cons[input1_name]
                    input2_id = bw_cons[input2_name]

                    if input1_id == self.graphObj.graphs[layerId]["Info"]["Properties"]["Labels"]:
                        labels = X[input1_name]['Y']
                        network_output = X[input2_name]['Y']
                    else:
                        network_output = X[input1_name]['Y']
                        labels = X[input2_name]['Y']                        
                    
                    '''
                    for input_name, input_value in X.items():
                        input_id = next((bw_con_id for bw_con_id, bw_con_name in backward_cons if bw_con_name == input_name), None)

                        if input_id is None:
                            log.error("
                        
                        if input_id == labels_id

                    
                    for key, value in X.items():
                        try:
                            key_id = [x[0] for x in self.graphObj.graphs[layerId]['Info']['backward_connections'] if x[1] == key][0]
                            if key_id == self.graphObj.graphs[layerId]["Info"]["Properties"]["Labels"]:
                                Labels=value['Y']
                            else:
                                Network_output=value['Y']
                        except:
                            log.exception("Error when matching training layer inputs to assigned labels")
                            if log.isEnabledFor(logging.DEBUG):
                                
                                log.debug(
                                    f'X = {pprint.pformat(X))}'
                                    f'key = {key}'                                    
                                    f'backward_connections = {self.graphObj.graphs[layerId]["Info"]["backward_connections"]}'
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

            if view=="Generated_output":
                generated_sample=self.getStatistics({"layerId":layerId,"variable":"generated_image","innervariable":""})

                dataObjectOutput = createDataObject(generated_sample)
            
    
                output = {"generated_output": dataObjectOutput}
                return output

            if view=="Real_input":
                real_sample=self.getStatistics({"layerId":layerId,"variable":"real_image","innervariable":""})

                dataObjectOutput = createDataObject(real_sample)
            
    
                output = {"real_input": dataObjectOutput}
                return output
            
            if view=="Data_distribution":
                data_distribution = self.getStatistics({"layerId":layerId,"variable":"data_distribution","innervariable":""})
                dataObjectOutput = createDataObject(data_distribution)
    
                output = {"Data_distribution": dataObjectOutput}
                return output
        

        elif layerType=="TrainDetector":
            if view=="Prediction":
                #Make sure that all the inputs are sent to frontend!!!!!!!!!!!!!!!
                
                image = self.getStatistics({"layerId": layerId, "variable":"image_bboxes", "innervariable":""})
                # image = np.random.randint(0,255,[224,224,3])
                Bboxes = createDataObject([image])    


                # Confidence of the boxes in sample
                confidence_scores = self.getStatistics({"layerId":layerId,"variable":"confidence_scores","innervariable":""})
                Confidence = createDataObject([confidence_scores])
                
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

            if view=="Generated_output":
                generated_sample=self.getStatistics({"layerId":layerId,"variable":"gen_output_train","innervariable":""})

                dataObjectOutput = createDataObject(generated_sample)
            
    
                output = {"generated_output": dataObjectOutput}
                return output

            if view=="Real_input":
                real_sample=self.getStatistics({"layerId":layerId,"variable":"real_input_train","innervariable":""})

                dataObjectOutput = createDataObject(real_sample)
            
    
                output = {"real_input": dataObjectOutput}
                return output
            
            if view=="Generator_distribution":
                generator_distribution = self.getStatistics({"layerId":layerId,"variable":"generator_distribution","innervariable":""})

                dataObjectOutput = createDataObject(generator_distribution)
    
                output = {"generator_distribution": dataObjectOutput}
                return output
            
            if view=="Real_distribution":
                real_distribution = self.getStatistics({"layerId":layerId,"variable":"real_distribution","innervariable":""})

                dataObjectOutput = createDataObject(real_distribution)

                output = {"real_distribution": dataObjectOutput}
                return output
                  
        elif layerType=="TrainReinforce":
            if view=="Prediction":
                state = self.getStatistics({"layerId":layerId,"variable":"state","innervariable":""})
                state_ = createDataObject([state])

                prediction = self.getStatistics({"layerId":layerId,"variable":"pred","innervariable":""})
                
                prediction = createDataObject([prediction], typeList=['line'])
                
                output = {"Input":state_, "Prediction": prediction}
                return output

            if view=="Reward":
                currentReward=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":"Reward"})
                totalReward=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":"epochTotalReward"})


                # doneState=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":"Done"})
                # allDones=np.where(doneState==True)[0]
                # if allDones.size>0:
                #     for i in range(len(allDones)):
                #         if i>0:
                #             r[allDones[i-1]:allDones[i]]=np.cumsum(r[allDones[i-1]:allDones[i]])
                #         else:
                #             r[0:allDones[i]]=np.cumsum(r[0:allDones[i]])
                #     r[allDones[-1]:]=np.cumsum(r[allDones[i]:])
                # else:
                #     r=np.cumsum(r)

                # currentReward=r[int(allDones[-1] if allDones.size>0 else 0):int(doneState.size)]
                # totalReward=np.array([r[int(i-1)] for i in allDones]) if allDones.size>0 else np.array([])
                current_reward = createDataObject([currentReward],
                                                typeList=['line'])
                total_reward = createDataObject([totalReward],
                                                typeList=['line'])
                obj = {"Current": current_reward, "Total": total_reward}
                return obj
            if view=="Loss":
                currentLoss=self.getStatistics({"layerId":layerId,"variable":"loss","innervariable":""})
                totalLoss=self.getStatistics({"layerId":layerId,"variable":"epochTrainLoss","innervariable":""})
                
                current_loss = createDataObject([currentLoss],
                                                typeList=['line'])
                total_loss = createDataObject([totalLoss],
                                               typeList=['line'])
                obj = {"Current": current_loss, "Total": total_loss}
                return obj
            if view=="Steps":
                steps=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":"epochTotalSteps"})
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
        #print(sess.run([outputVariables["6"]["accuracy"]],feed_dict=dict(zip(keys, values))))

        layerId=statSpec["layerId"]
        variable=statSpec["variable"]
        innervariable=statSpec["innervariable"]
        log.debug("getStatistics for layer {}, variable {}, innervariable {}".format(layerId,
                                                                                     variable,
                                                                                     innervariable))
        
        if self.resultDict is not None:
            # print("All keys available: ",str(list(self.resultDict.keys())))
            if innervariable!="":
                try:
                    result=self.resultDict[layerId][variable][innervariable]
                except:
                    try:
                        log.debug("FieldError, only keys available are: "+str(list(self.resultDict[layerId][variable].keys()))+" |||| Expected: "+str(innervariable))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId][variable].keys()))+" |||| Expected: "+str(innervariable))
                    except:
                        try:
                            log.debug("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                            self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                        except:
                            log.debug("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                            self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))

                    result=[]
            elif variable!="":
                try:
                    result=self.resultDict[layerId][variable]
                except:
                    try:
                        log.debug("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                    except:
                        log.debug("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    result=[]
            else:
                try:
                    result=self.resultDict[layerId]
                except:
                    log.debug("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    result=[]
        else:
            log.debug("ResultDict is empty :'(")
            self.warningQueue.put("There are no results to fetch")
            result=[]

        if log.isEnabledFor(logging.DEBUG):
            self._get_statistics_debug_info(layerId, variable, innervariable, result)
            
        if type(result).__name__!='dict':
            result=np.asarray(result)

        return result

    def _get_statistics_debug_info(self, layer_id, variable, innervariable, result):
        layer_type = self.graphObj.graphs[layer_id]["Info"]["Type"]            
        layer_name = self.graphObj.graphs[layer_id]["Info"]["Name"]
        
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
            
        log.debug(message)
        

    # def subsample(self,sample):
    #     endSize=500
    #     if len(sample.shape)==1:
    #         length=sample.size
    #         if length>endSize:
    #             lenRatio=length/endSize
    #         else:
    #             lenRatio=1
    #         result=sample[::int(lenRatio)]

    #     elif len(sample.shape)>=2:
    #         height,width=sample.shape[0:2]
    #         if height>endSize or width>endSize:
    #             if height>width:
    #                 heightRatio=widthRatio=height/endSize
    #             else:
    #                 heightRatio=widthRatio=width/endSize
    #         else:
    #             heightRatio=widthRatio=1
    #         result=sample[::int(np.ceil(heightRatio)),::int(np.ceil(widthRatio))]
    #     else:
    #         result=sample

    #     return result

    # def rgb2gray(rgb):
    #     return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

    # def convertToList(self,npy):
    #     if len(npy.shape)==0:
    #         if isinstance(npy, np.integer):
    #             npy=[int(npy)]
    #         elif isinstance(npy, np.floating):
    #             npy=[float(npy)]
    #     elif len(npy.shape)==1:
    #         # npy=list(npy)
    #         npy=npy.tolist()
    #     elif len(npy.shape)>1:
    #         npy=npy.tolist()
    #     return npy

    # def grayscale2RGBa(self,data):
    #     data=np.squeeze(data)
    #     (w,h)=np.shape(data)
    #     newData=np.empty((w, h, 4))
        
    #     if data.max()!=0:
    #         normalizedData=np.around((data/data.max())*255)
    #     else:
    #         normalizedData=data
    #     newData[:, :, 0] = normalizedData
    #     newData[:, :, 1] = newData[:, :, 2] = newData[:, :, 0]
    #     newData[:,:,3]=255
    #     flatData=np.reshape(newData,-1)

    #     return flatData

    # def RGB2RGBa(self,data):
    #     data=np.squeeze(data)
    #     (w,h,d)=np.shape(data)
    #     newData=np.empty((w, h, 4))
    #     normalizedData=np.around((data/data.max(0).max(0))*255)
    #     newData[:, :, 0:3] = normalizedData
    #     newData[:,:,3]=255
    #     flatData=np.reshape(newData,-1)
    #     return flatData
