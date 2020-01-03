import sys
import os

# class webInterface():
#     def __init__():
#         pass

# class desktopInterface(Interface):
#     def __init__():
#         pass

#     reciever=self.request.get("reciever")
#     action = self.request.get("action")
#     startTime=time.time()

#     if not reciever in self.dataDict:
#         self.dataDict[reciever]=dict()

#     if reciever not in self.cores:
#         core=coreLogic(reciever)
#         self.cores[reciever]=core
#     else:
#         core=self.cores[reciever]

#     warnings=core.warningQueue
#     warningList=[]

#     errors=core.errorQueue
#     errorList=[]

#     content=""

    
#     coreCalls=["Close", "updateResults", "checkCore", "headless", "getTrainingStatistics", "getTestingStatistics", "Start", "startTest", "resetTest", "getTestStatus",
#     "nextStep", "previousStep", "playTest", "getIter", "getEpoch", "Stop", "Pause", "SkipToValidation", "Export", "getStatus"]
#     lwCalls=["getDataPlot", "getDataMeta", "deleteData", "removeReciever", "getNetworkData", "getNetworkInputDim", "getNetworkOutputDim", "getPreviewSample"]
#     parseCalls=["Parse"]
#     with configure_scope() as scope:
#         scope.set_extra("reciever",reciever)
#         scope.set_extra("action",action)
#         scope.set_extra("value",self.request.get("value"))
#         #Check what the request is for and then get the properties needed for that function
#         if action in coreCalls:
#             # scope.set_extra("Core properties", core.core.__dict__)
#             # coreProperties=dict()
#             # for key, value in core.core.__dict__.items():
#             #     if type(value).__name__!="dict":
#             #         coreProperties[key]=value
#             # scope.set_extra("Core properties", coreProperties)
#             scope.set_extra("Saved Results Dict", core.savedResultsDict)
#             scope.set_extra("Network", core.network)
        

#         elif action in lwCalls:
#             for dataId, dataValue in self.dataDict[reciever].items():
#                 scope.set_extra("data object for layer: "+str(dataId), dataValue.__dict__)
#         elif action in parseCalls:
#             pass
#         else:
#             # scope.set_extra("Core properties", core.core.__dict__)
#             for dataId, dataValue in self.dataDict[reciever].items():
#                 scope.set_extra("data object for layer: "+str(dataId), dataValue.__dict__)

#     #####################################B4End###################################
    

# queue_function_translation=[("stop-request","stop-response", "Stop"),
#     ("start-request","start-response", "Start"),  #Might have to be a frontend call to cloud, where core then starts as soon as the VM is on
#     ("cloud-close-vm-request","cloud-close-vm-response", "empty"),
#     ("model-save-request","model-save-response", "saveTrained"),
#     ("update-results-request","update-results-response", "updateResults"),
#     ("get-status-request", "get-status-response", "getStatus"),    #TODO: Not yet exists as an endpoint!!!!
#     ("headless-request","headless-response", "headless"),
#     ("get-training-statistics-request","get-training-statistics-response", "getTrainingStatistics"),
#     ("get-testing-statistics-request","get-testing-statistics-response", "getTestingStatistics"),
#     ("start-test-request","start-test-response", "startTest"),
#     ("reset-test-request","reset-test-response", "resetTest"),
#     ("get-test-status-request","get-test-status-response", "getTestStatus"),
#     ("next-step-request","next-step-response", "nextStep"),
#     ("previous-step-request","previous-step-response", "previousStep"),
#     ("play-test-request","play-test-response", "playTest"),
#     ("pause-request","pause-response", "Pause"),
#     ("skip-validation-request","skip-validation-response", "SkipToValidation"),
#     ("check-core-request","check-core-response", "checkAlive"),
#     ("export-request","export-response", "Export")    #Might have to be moved to LW Core and let that one store all internal variables for open tabs
# ]

# class azureInterface():
#     def __init__(self):
#         pass

from lwInterface import getDataMeta, getPartitionSummary, getCode, getNetworkInputDim, getNetworkOutputDim, getPreviewSample, getPreviewVariableList, Parse

class Interface():
    def __init__(self, cores, dataDict, checkpointDict, lwNetworks):
        self._cores=cores
        self._dataDict=dataDict
        self._checkpointDict=checkpointDict
        self._lwNetworks=lwNetworks

    def _addCore(self, reciever):
        from coreLogic import coreLogic
        core=coreLogic(reciever)
        self._cores[reciever] = core

    def _setCore(self, reciever):
        if reciever not in self._cores:
            self._addCore(reciever)
        self._core = self._cores[reciever]

    def shutDown(self):
        for c in self._cores.values():
            c.Close()
            del c
        sys.exit(1)

    # def globalErrors(self):
    #     errorList = []
    #     errors = self._core.errorQueue
    #     while not errors.empty():
    #         message = errors.get(timeout=0.05)
    #         errorList.append(message)
    #     if errorList:
    #         self._core.Close()
    #     return errorList

    # def globalWarnings(self):
    #     warningList = []
    #     warnings = self._core.warningQueue
    #     while not warnings.empty():
    #         message = warnings.get(timeout=0.05)
    #         warningList.append(message)
    #     return warningList

    def getCheckpointDict(self):
        return self._checkpointDict.copy()

    def add_to_checkpointDict(self, content):
        if content["checkpoint"][-1] not in self._checkpointDict:
            from extractVariables import extractCheckpointInfo
            ckptObj=extractCheckpointInfo(content["endPoints"], *content["checkpoint"])
            self._checkpointDict[content["checkpoint"][-1]]=ckptObj.getVariablesAndConstants()
            ckptObj.close()

    def _create_lw_core(self, jsonNetwork):
        from graph import Graph
        from core_new.core import DataContainer
        from core_new.history import SessionHistory
        from core_new.errors import LightweightErrorHandler
        from core_new.extras import LayerExtrasReader
        from core_new.lightweight import LightweightCore, LW_ACTIVE_HOOKS
        from modules import ModuleProvider
        from core_new.cache import get_cache

        if reciever not in self.lwDict:
            self.lwDict[reciever]=NetworkCache()
        else:
            deleteList=[]
            for layer_id in self.lwDict[reciever].get_layers():
                if layer_id not in jsonNetwork:
                    deleteList.append(layer_id)
            log.info("Deleting these layers: " + str(deleteList))
            for layer_id in deleteList:
                self.lwDict[reciever].remove_layer(layer_id)

        graph = Graph(jsonNetwork)
        
        graph_dict = graph.graphs

        for value in graph_dict.values():
            if "checkpoint" in value["Info"] and value["Info"]["checkpoint"]:
                self.add_to_checkpointDict(value["Info"])

        data_container = DataContainer()
            
        extras_reader = LayerExtrasReader()

        from codehq import CodeHqNew as CodeHq

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
        
        for hook_target, hook_func in LW_ACTIVE_HOOKS.items():
            module_provider.install_hook(hook_target, hook_func)

        error_handler = LightweightErrorHandler()
        
        global session_history_lw
        cache = get_cache()
        session_history_lw = SessionHistory(cache) # TODO: don't use global!!!!        
        lw_core = LightweightCore(CodeHq, graph_dict,
                                  data_container, session_history_lw,
                                  module_provider, error_handler,
                                  extras_reader, checkpointValues=self.checkpointDict.copy(),
                                  network_cache=self.lwDict[reciever])
        
        return lw_core, extras_reader, data_container

    def create_response(self, request):
        reciever = request.get('reciever')
        action = request.get('action')
        value = request.get('value')

        self._setCore(reciever)
        self._create_response(action, value)

        return self._create_response, self._core.warningQueue, self._core.errorQueue

    def _create_response(self, action, value):
        #Parse the value and send it to the correct function
        if action == "getDataMeta":
            Id = value['Id']
            jsonNetwork = value['Network']
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            return getDataMeta(id_=Id, 
            network=jsonNetwork, 
            lw_func=self._create_lw_core).exec()

        elif action == "getPartitionSummary":
            Id=value["Id"]
            jsonNetwork=value["Network"]
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            return getPartitionSummary(id_=Id, 
            network=jsonNetwork, 
            lw_func=self._create_lw_core).exec()

        elif action == "getCode":
            jsonNetwork=value['Network']
            Id = value['Id']
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            return getCode(id_=Id, 
            network=jsonNetwork).exec()

        elif action == "getNetworkInputDim":
            jsonNetwork=value

            return getNetworkInputDim(network=jsonNetwork, 
            lw_func=self._create_lw_core).exec()

        elif action == "getNetworkOutputDim":
            jsonNetwork=value

            return getNetworkOutputDim(network=jsonNetwork, 
            lw_func=self._create_lw_core).exec()

        elif action == "getPreviewSample":
            LayerId=value["Id"]
            jsonNetwork=value["Network"]
            try:
                Variable=value["Variable"]
            except:
                Variable=None

            return getPreviewSample(id_=LayerId, 
            network=jsonNetwork, 
            lw_func=self._create_lw_core, 
            variable=Variable).exec()

        elif action == "getPreviewVariableList":
            LayerId=value["Id"]
            jsonNetwork=value["Network"]
            
            return getPreviewVariableList(id_=LayerId,
            network=jsonNetwork, 
            lw_func=self._create_lw_core).exec()

        elif action == "Parse":
            if value["Pb"]:
                pb=value["Pb"][0]
            else:
                pb=value["Pb"]

            if value["Checkpoint"]:
                ckpt=value["Checkpoint"][0]
            else:
                ckpt=value["Checkpoint"]

            trainableFlag=value["Trainable"]
            end_points=value["EndPoints"]
            containers=value["Containers"]

            return Parse(pb=pb, 
            checkpointDict=self._checkpointDict, 
            checkpoint=ckpt, 
            make_trainable=trainableFlag, 
            end_points=end_points, 
            containerize=containers).exec()

        elif action == "Close":
            self.shutDown()

        elif action == "updateResults":
            self._core.updateResults()

        elif action == "checkCore":
            self._core.checkCore()

        elif action == "headless":
            On=value    #bool value
            self._core.headless(On)

        elif action == "getTrainingStatistics":
            self._core.getTrainingStatistics()

        elif action == "getTestingStatistics":
            self._core.getTestingStatistics()

        elif action == "getS3Keys":
            self._core.getS3Keys()

        elif action == "Start":
            self._core.Start()

        elif action == "startTest":
            self._core.startTest()

        elif action == "resetTest":
            self._core.resetTest()

        elif action =="getTestStatus":
            self._core.getTestStatus()

        elif action == "nextStep":
            self._core.nextStep()

        elif action == "previousStep":
            self._core.previousStep()

        elif action == "playTest":
            self._core.playTest()

        elif action == "getIter":
            self._core.getIter()

        elif action == "getEpoch":
            self._core.getEpoch()

        elif action == "Stop":
            self._core.Stop()

        elif action == "Pause":
            self._core.Pause()

        elif action == "Unpause":
            self._core.Unpause()

        elif action == "SkipToValidation":
            self._core.SkipToValidation()

        elif action == "Export":
            self._core.Export()

        elif action == "isTrained":
            self._core.isTrained()

        elif action == "SaveTrained":
            self._core.SaveTrained()

        elif action == "getEndResults":
            self._core.getEndResults()

        elif action == "getStatus":
            self._core.getStatus()

        else:
            raise LookupError("The requested action does not exist")