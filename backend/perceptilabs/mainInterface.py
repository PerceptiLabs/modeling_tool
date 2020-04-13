import sys
import os
import logging
import pprint
from sentry_sdk import configure_scope
from perceptilabs.extractVariables import extractCheckpointInfo
from perceptilabs.s3buckets import S3BucketAdapter

#core interface
from perceptilabs.coreInterface import coreLogic

from perceptilabs.utils import stringify
from perceptilabs.graph import Graph
from perceptilabs.core_new.core import DataContainer
from perceptilabs.core_new.history import SessionHistory
from perceptilabs.core_new.errors import LightweightErrorHandler
from perceptilabs.core_new.extras import LayerExtrasReader
from perceptilabs.core_new.lightweight import LightweightCore, LW_ACTIVE_HOOKS
from perceptilabs.modules import ModuleProvider
from perceptilabs.core_new.cache import get_cache
from perceptilabs.core_new.networkCache import NetworkCache
from perceptilabs.codehq import CodeHqNew as CodeHq
from perceptilabs.core_new.lightweight2 import LightweightCoreAdapter
from perceptilabs.core_new.cache2 import LightweightCache

        
#LW interface
from perceptilabs.lwInterface import getFolderContent, saveJsonModel, getJsonModel, getGraphOrder, getDataMeta, getPartitionSummary, getCodeV1, getCodeV2, getNetworkInputDim, getNetworkOutputDim, getPreviewSample, getPreviewVariableList, Parse

log = logging.getLogger(__name__)


LW_CACHE_MAX_ITEMS = 25 # Only for '--core-mode v2'


class Interface():
    def __init__(self, cores, dataDict, checkpointDict, lwDict, core_mode):
        self._cores=cores
        self._dataDict=dataDict
        self._checkpointDict=checkpointDict
        self._lwDict=lwDict
        self._core_mode = core_mode
        assert core_mode in ['v1', 'v2']

        if core_mode == 'v2':
            self._lw_cache_v2 = LightweightCache(max_size=LW_CACHE_MAX_ITEMS)        

    def _addCore(self, reciever):
        core=coreLogic(reciever, self._core_mode)
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

    def close_core(self, reciever):
        if reciever in self._cores:
            msg = self._cores[reciever].Close()
            del self._cores[reciever]
            return msg
        else:
            return "No core called %s" %reciever

    def getCheckpointDict(self):
        return self._checkpointDict.copy()

    def _add_to_checkpointDict(self, content):
        if content["checkpoint"][-1] not in self._checkpointDict:
            ckptObj=extractCheckpointInfo(content["endPoints"], *content["checkpoint"])
            self._checkpointDict[content["checkpoint"][-1]]=ckptObj.getVariablesAndConstants()
            ckptObj.close()

    def create_lw_core(self, reciever, jsonNetwork):
        if self._core_mode == 'v1':
            return self._create_lw_core_v1(reciever, jsonNetwork)
        else:
            return self._create_lw_core_v2(reciever, jsonNetwork)

    def _create_lw_core_v2(self, reciever, jsonNetwork):
        data_container = DataContainer()
        extras_reader = LayerExtrasReader()
        error_handler = LightweightErrorHandler()
        
        lw_core = LightweightCoreAdapter(jsonNetwork, extras_reader, error_handler, self._core.issue_handler, self._lw_cache_v2)
        return lw_core, extras_reader, data_container

    def _create_lw_core_v1(self, reciever, jsonNetwork):                
        if reciever not in self._lwDict:
            self._lwDict[reciever]=NetworkCache()
        else:
            deleteList=[]
            for layer_id in self._lwDict[reciever].get_layers():
                if layer_id not in jsonNetwork:
                    deleteList.append(layer_id)
            log.info("Deleting these layers: " + str(deleteList))
            for layer_id in deleteList:
                self._lwDict[reciever].remove_layer(layer_id)

        graph = Graph(jsonNetwork)
        
        graph_dict = graph.graphs

        for value in graph_dict.values():
            if "checkpoint" in value["Info"] and value["Info"]["checkpoint"]:
                info = value["Info"].copy()

                ckpt_path = info['checkpoint'][1]
                if '//' in ckpt_path:
                    new_ckpt_path = os.path.sep+ckpt_path.split(2*os.path.sep)[1] # Sometimes frontend repeats the directory path. /<dir-path>//<dir-path>/model.ckpt-1
                    log.warning(
                        f"Splitting malformed checkpoint path: '{ckpt_path}'. "
                        f"New path: '{new_ckpt_path}'"
                    )
                    info['checkpoint'][1] = new_ckpt_path
                    
                self._add_to_checkpointDict(info)

        if log.isEnabledFor(logging.DEBUG):
            log.debug("create_lw_core: checkpoint dict: \n" + stringify(self._checkpointDict))

        data_container = DataContainer()
        extras_reader = LayerExtrasReader()

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


        lw_core = LightweightCore(
            CodeHq, graph_dict,
            data_container, session_history_lw,
            module_provider, error_handler,
            extras_reader, checkpointValues=self._checkpointDict.copy(),
            network_cache=self._lwDict[reciever],
            core_mode=self._core_mode
        )

        
        return lw_core, extras_reader, data_container

    def create_response(self, request):
        reciever = request.get('reciever')
        action = request.get('action')
        value = request.get('value')

        if log.isEnabledFor(logging.DEBUG):
            log.debug("creating response for action: {}. \nFull request:\n{}".format(
                action,
                pprint.pformat(request, depth=3)
            ))

        with configure_scope() as scope:
            scope.set_extra("reciever",reciever)
            scope.set_extra("action",action)
            scope.set_extra("value",value)

        self._setCore(reciever)
        
        #try:
        response = self._create_response(reciever, action, value)
        #except Exception as e:
        #    with self._core.issue_handler.create_issue('Error in create_response', e) as issue:
        #        self._core.issue_handler.put_error(issue.frontend_message)
        #        response = {'content': issue.frontend_message}                
        #        log.error(issue.internal_message)

        if log.isEnabledFor(logging.DEBUG):
            log.debug("created response for action: {}. \nFull request:\n{}\nResponse:\n{}".format(
                action,
                pprint.pformat(request, depth=3),
                stringify(response)
            ))

                
        return response, self._core.issue_handler

    def _create_response(self, reciever, action, value):
        #Parse the value and send it to the correct function
        if action == "getDataMeta":
            Id = value['Id']
            jsonNetwork = value['Network']
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)

            return getDataMeta(id_=Id, 
                            lw_core=lw_core, 
                            data_container=data_container).run()

        elif action == "getFolderContent":
            current_path = value
            return getFolderContent(current_path=current_path).run()
        
        elif action == "getJsonModel":
            json_path = value
            return getJsonModel(json_path=json_path).run()

        elif action == "saveJsonModel":
            save_path = value["path"]
            json_model = value["json"]
            network_name = value["name"]
            return saveJsonModel(save_path=save_path, json_model=json_model, network_name=network_name).run()

        elif action == "getPartitionSummary":
            Id=value["Id"]
            jsonNetwork=value["Network"]
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)

            return getPartitionSummary(id_=Id, 
                                    lw_core=lw_core, 
                                    data_container=data_container).run()

        elif action == "getCode":
            jsonNetwork=value['Network']
            Id = value['Id']
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            if self._core_mode == 'v1':
                get_code = getCodeV1(id_=Id, network=jsonNetwork)
            else:
                get_code = getCodeV2(id_=Id, network=jsonNetwork)                
            
            return get_code.run()

        elif action == "getNetworkInputDim":
            jsonNetwork=value

            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)

            return getNetworkInputDim(network=jsonNetwork, 
                                    lw_core=lw_core, 
                                    extras_reader=extras_reader).run()

        elif action == "getNetworkOutputDim":
            jsonNetwork=value

            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)

            return getNetworkOutputDim(lw_core=lw_core, 
                                    extras_reader=extras_reader).run()

        elif action == "getPreviewSample":
            LayerId=value["Id"]
            jsonNetwork=value["Network"]
            try:
                Variable=value["Variable"]
            except:
                Variable=None

            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)

            return getPreviewSample(id_=LayerId, 
                                    lw_core=lw_core, 
                                    extras_reader=extras_reader, 
                                    data_container=data_container, 
                                    variable=Variable).run()

        elif action == "getPreviewVariableList":
            LayerId=value["Id"]
            jsonNetwork=value["Network"]

            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)
            
            return getPreviewVariableList(id_=LayerId, 
                                        network=jsonNetwork, 
                                        lw_core=lw_core, 
                                        extras_reader=extras_reader).run()

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

            try:
                return Parse(pb=pb, 
                checkpointDict=self._checkpointDict, 
                checkpoint=ckpt, 
                make_trainable=trainableFlag, 
                end_points=end_points, 
                containerize=containers).run()
            except Exception as e:
                return {"content":"Parser Failed","errorMessage":"Parser got this Exception:\n" + str(e)}

        elif action == "getGraphOrder":
            jsonNetwork = value
            return getGraphOrder(jsonNetwork=jsonNetwork).run()         

        elif action == "Close":
            self.shutDown()

        elif action == "closeSession":
            return self.close_core(reciever)

        elif action == "updateResults":
            response = self._core.updateResults()
            return response

        elif action == "isRunning":
            response = self._core.isRunning()
            return response

        elif action == "checkCore":
            response = self._core.checkCore()
            return response

        elif action == "headless":
            On=value    #bool value
            response = self._core.headless(On)
            return response

        elif action == "getTrainingStatistics":
            response = self._core.getTrainingStatistics(value)
            return response

        elif action == "getTestingStatistics":
            response = self._core.getTestingStatistics(value)
            return response

        elif action == "getS3Keys":
            adapter = S3BucketAdapter(value['bucket'],
                                value['aws_access_key_id'], value['aws_secret_access_key'])
            response = adapter.get_keys(value['delimiter'], value['prefix'])
            return response

        elif action == "Start":
            network = value
            for value in network['Layers'].values():
                if "checkpoint" in value and value["checkpoint"] and self._core_mode == 'v1':
                    self._add_to_checkpointDict(value)
            response = self._core.startCore(network, self._checkpointDict.copy())
            return response

        elif action == "startTest":
            response = self._core.startTest()
            return response

        elif action == "isTestPlaying":
            return self._core.isTestPlaying()

        elif action == "resetTest":
            response = self._core.resetTest()
            return response

        elif action =="getTestStatus":
            response = self._core.getTestStatus()
            return response

        elif action == "nextStep":
            response = self._core.nextStep()
            return response

        elif action == "previousStep":
            response = self._core.previousStep()
            return response

        elif action == "playTest":
            response = self._core.playTest()
            return response

        elif action == "getIter":
            response = self._core.getIter()
            return response

        elif action == "getEpoch":
            response = self._core.getEpoch()
            return response

        elif action == "Stop":
            response = self._core.Stop()
            return response

        elif action == "Pause":
            response = self._core.Pause()
            return response

        elif action == "Unpause":
            response = self._core.Unpause()
            return response

        elif action == "SkipToValidation":
            response = self._core.skipToValidation()
            return response

        elif action == "Export":
            response = self._core.exportNetwork(value)
            return response

        elif action == "isTrained":
            response = self._core.isTrained()
            return response

        elif action == "SaveTrained":
            response = self._core.saveNetwork(value)
            return response

        elif action == "getEndResults":
            response = self._core.getEndResults()
            return response

        elif action == "getStatus":
            response = self._core.getStatus()
            return response

        elif action == "setUser":
            user = value
            with configure_scope() as scope:
                scope.user = {"email" : user}
                log.info("User has been set to %s" %str(value))

            return "User has been set to " + value

        else:
            raise LookupError(f"The requested action '{action}' does not exist")
