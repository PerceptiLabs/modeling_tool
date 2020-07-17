import logging
import sys
import os
import logging
import pprint
from sentry_sdk import configure_scope
from concurrent.futures import ThreadPoolExecutor
import time

from perceptilabs.extractVariables import extractCheckpointInfo
from perceptilabs.s3buckets import S3BucketAdapter
from perceptilabs.aggregation import AggregationRequest, AggregationEngine
from perceptilabs.coreInterface import coreLogic
from perceptilabs.extractVariables import extractCheckpointInfo
from perceptilabs.s3buckets import S3BucketAdapter
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
from perceptilabs.logconf import APPLICATION_LOGGER, set_user_email
from perceptilabs.core_new.lightweight2 import LightweightCoreAdapter
from perceptilabs.core_new.cache2 import LightweightCache
import perceptilabs.logconf
import perceptilabs.autosettings.utils as autosettings_utils


#LW interface
from perceptilabs.lwInterface import getRootFolder, getNotebookImports, getNotebookRunscript, getFolderContent, createFolder, saveJsonModel, getJsonModel, getGraphOrder, getDataMeta, getDataMetaV2, getPartitionSummary, getCodeV1, getCodeV2, getNetworkInputDim, getNetworkOutputDim, getPreviewSample, getPreviewVariableList, Parse

logger = logging.getLogger(APPLICATION_LOGGER)


LW_CACHE_MAX_ITEMS = 25 # Only for '--core-mode v2'
AGGREGATION_ENGINE_MAX_WORKERS = 2


class Interface():
    def __init__(self, cores, dataDict, checkpointDict, lwDict, core_mode):
        self._cores=cores
        self._dataDict=dataDict
        self._checkpointDict=checkpointDict
        self._lwDict=lwDict
        self._core_mode = core_mode
        assert core_mode in ['v1', 'v2']

        self._lw_cache_v2 = LightweightCache(max_size=LW_CACHE_MAX_ITEMS)
        self._settings_engine = None
        self._aggregation_engine = self._setup_aggregation_engine()
        
    def _setup_aggregation_engine(self):
        
        class DummyContainer():
            def get_metric(self, experiment_name, metric_name, start, end):
                if isinstance(start, int) and isinstance(end, int) and end - start > 0:
                    return (None,) * (end - start)
                else:
                    return (None,)                
        data_container = DummyContainer()
        
        agg_engine = AggregationEngine(
            ThreadPoolExecutor(max_workers=AGGREGATION_ENGINE_MAX_WORKERS),
            data_container,
            aggregates={}
        )
        return agg_engine
    
    def _addCore(self, reciever):
        core=coreLogic(reciever, self._core_mode)
        self._cores[reciever] = core

    def _setCore(self, reciever):
        if reciever not in self._cores:
            self._addCore(reciever)
        self._core = self._cores[reciever]

        self._settings_engine = autosettings_utils.setup_engine(self._lw_cache_v2)

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
        data_container = DataContainer()
        extras_reader = LayerExtrasReader()
        error_handler = LightweightErrorHandler()
        
        lw_core = LightweightCoreAdapter(jsonNetwork, extras_reader, error_handler, self._core.issue_handler, self._lw_cache_v2, data_container)
        return lw_core, extras_reader, data_container

    def create_response(self, request):
        reciever = request.get('reciever')
        action = request.get('action')
        value = request.get('value')

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("creating response for action: {}. \nFull request:\n{}".format(
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
        #        logger.error(issue.internal_message)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("created response for action: {}. \nFull request:\n{}\nResponse:\n{}".format(
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


            if self._core_mode == 'v1':
                get_data_meta = getDataMeta(
                    id_=Id, 
                    lw_core=lw_core, 
                    data_container=data_container
                )
            elif self._core_mode == 'v2':
                get_data_meta = getDataMetaV2(
                    id_=Id, 
                    lw_core=lw_core, 
                    extras_reader=extras_reader
                )

            return get_data_meta.run()

        elif action == "getSettingsRecommendation":
            json_network = value["Network"]

            if self._settings_engine is not None:
                new_json_network = autosettings_utils.get_recommendation(json_network, self._settings_engine)
            else:
                new_json_network = {}
                logger.warning("Settings engine is not set. Cannot make recommendations")
                
            return new_json_network
                
        elif action == "getFolderContent":
            current_path = value
            return getFolderContent(current_path=current_path).run()
        
        elif action == "getJsonModel":
            json_path = value
            return getJsonModel(json_path=json_path).run()
        
        elif action == "isDirExist":
            path_to_folder = value["path"]
            return os.path.isdir(path_to_folder)

        elif action == 'isFileExist':
            path_to_file = value['path']
            return os.path.isfile(path_to_file)

        elif action == "getRootFolder":
            return getRootFolder().run()

        elif action == "saveJsonModel":
            save_path = value["path"]
            json_model = value["json"]
            return saveJsonModel(save_path=save_path, json_model=json_model).run()

        elif action == "createFolder":
            folder_path = value['folder_path']
            return createFolder(folder_path=folder_path).run()

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

        elif action == "getNotebookImports":
            jsonNetwork = value
            return getNotebookImports(jsonNetwork=jsonNetwork).run()          

        elif action == "getNotebookRunscript":
            jsonNetwork = value
            return getNotebookRunscript(jsonNetwork=jsonNetwork).run()

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
            # time.sleep(3)
            response = self._core.getEndResults()
            return response

        elif action == "getStatus":
            response = self._core.getStatus()
            return response

        elif action == "setUser":
            user = value
            with configure_scope() as scope:
                scope.user = {"email" : user}

            perceptilabs.logconf.set_user_email(user)
            logger.info("User has been set to %s" %str(value))
            
            return "User has been set to " + value

        elif action == "scheduleAggregations":
            requests = [
                AggregationRequest(
                    result_name=raw_request['result_name'],
                    aggregate_name=raw_request['aggregate_name'],
                    experiment_name=raw_request['experiment_name'],
                    metric_names=raw_request['metric_names'],
                    start=raw_request['start'],
                    end=raw_request['end'],
                    aggregate_kwargs=raw_request['aggregate_kwargs']
                )
                for raw_request in value
            ]
            response = self._core.scheduleAggregations(self._aggregation_engine, requests)
            return response
        elif action == "getAggregationResults":
            result_names = value
            response = self._core.getAggregationResults(result_names)
            return response
        else:
            raise LookupError(f"The requested action '{action}' does not exist")
