import sys
import os
import logging
import pprint
import time
import threading
from sentry_sdk import configure_scope
from concurrent.futures import ThreadPoolExecutor

#core interface
from perceptilabs.extractVariables import extractCheckpointInfo
from perceptilabs.s3buckets import S3BucketAdapter
from perceptilabs.aggregation import AggregationRequest, AggregationEngine
from perceptilabs.coreInterface import coreLogic

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.utils import stringify
from perceptilabs.core_new.errors import LightweightErrorHandler
from perceptilabs.core_new.extras import LayerExtrasReader
from perceptilabs.logconf import APPLICATION_LOGGER, set_user_email
from perceptilabs.core_new.lightweight2 import LightweightCoreAdapter, LightweightCore
from perceptilabs.core_new.cache2 import LightweightCache
import perceptilabs.utils as utils
from perceptilabs.messaging.zmq_wrapper import ZmqMessagingFactory, ZmqMessageConsumer
from perceptilabs.api.data_container import DataContainer as Exp_DataContainer
from perceptilabs.messaging import MessageConsumer, MessagingFactory

import perceptilabs.logconf
import perceptilabs.autosettings.utils as autosettings_utils


#LW interface
from perceptilabs.lwInterface import getRootFolder, getNotebookImports, getNotebookRunscript, getFolderContent, createFolder, saveJsonModel, getJsonModel, getGraphOrder, getDataMeta, getDataMetaV2, getPartitionSummary, getCode, getNetworkInputDim, getNetworkOutputDim, getPreviewSample, getPreviewBatchSample, getPreviewVariableList, Parse, resolveDir

logger = logging.getLogger(APPLICATION_LOGGER)


USE_AUTO_SETTINGS = True
USE_LW_CACHING = True
LW_CACHE_MAX_ITEMS = 25 
AGGREGATION_ENGINE_MAX_WORKERS = 2




def load_network(json_network, as_spec=False, layers_only=True):
    """ to load the json network in a single location for easy debugging """
    network = json_network.copy()
    
    if (layers_only or as_spec) and ('Layers' in network):
        network = network['Layers']
    
    if as_spec:
        network = GraphSpec.from_dict(network)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("loading json network:" + pprint.pformat(network))

    return network


class Interface():
    def __init__(self, cores, dataDict, checkpointDict, lwDict, core_mode=None, message_factory=None):
        self._cores=cores
        self._dataDict=dataDict
        self._checkpointDict=checkpointDict
        self._lwDict=lwDict
        self._core_mode = 'v2'
        self._lw_cache_v2 = LightweightCache(max_size=LW_CACHE_MAX_ITEMS) if USE_LW_CACHING else None
        self._settings_engine = None

        self._data_container = Exp_DataContainer()
        self._aggregation_engine = self._setup_aggregation_engine(self._data_container)
        self._start_experiment_thread(message_factory)
    
    def _setup_consumer(self, message_factory: MessagingFactory = None) -> MessageConsumer:
        '''Creates consumer for incoming experiment data
        
        Returns:
            consumer: Consumer object to consume experiment data
        '''
        if message_factory:
            topic_data = 'generic-experiment'
            consumer = message_factory.make_consumer([topic_data])

            return consumer
        else:
            topic_data = f'generic-experiment'.encode()
            zmq_consumer = ZmqMessagingFactory().make_consumer([topic_data])

            return zmq_consumer

    def _setup_aggregation_engine(self, data_container: Exp_DataContainer) -> AggregationEngine:
        '''Creates Aggregations Engine
        
        Args:
            data_container: DataContainer object that stores experiment data
        
        Returns:
            agg_engine: AggregationEngine class to query data
        '''
        agg_engine = AggregationEngine(
            ThreadPoolExecutor(max_workers=AGGREGATION_ENGINE_MAX_WORKERS),
            data_container,
            aggregates={}
        )
        return agg_engine
    
    def _start_experiment_thread(self, message_factory: MessagingFactory):
        '''Creates a thread to continuously get data from experiment API
        
        Args:
            consumer: A MessageConsumer object to be created
        '''
        def _get_experiment_data():
            '''Creates consumer object and gets experiment data from consumer object'''
            self._dc_consumer = self._setup_consumer(message_factory=message_factory)
            self._dc_consumer.start()

            while True:
                raw_messages = self._dc_consumer.get_messages()

                for raw_message in raw_messages:
                    self._data_container.process_message(raw_message)
                
                time.sleep(2)

        t = threading.Thread(target=_get_experiment_data)
        t.daemon = True
        t.start()

    def _addCore(self, reciever):
        core=coreLogic(reciever, self._core_mode)
        self._cores[reciever] = core

    def _setCore(self, reciever):
        if reciever not in self._cores:
            self._addCore(reciever)
        self._core = self._cores[reciever]

        if USE_AUTO_SETTINGS:
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

    def create_lw_core(self, reciever, jsonNetwork, adapter=True):
        if adapter:
            extras_reader = LayerExtrasReader()
            error_handler = LightweightErrorHandler()
            data_dict = {}
            
            graph_spec = GraphSpec.from_dict(utils.patch_net_connections(jsonNetwork))
            lw_core = LightweightCoreAdapter(graph_spec, extras_reader, error_handler, self._core.issue_handler, self._lw_cache_v2, data_dict)
            return lw_core, extras_reader, data_dict
        else:
            lw_core = LightweightCore(
                issue_handler=self._core.issue_handler,
                cache=self._lw_cache_v2
            )

            return lw_core, None, None

    def create_response(self, request):
        reciever = request.get('reciever')
        action = request.get('action')
        value = request.get('value')

        if action != 'checkCore':
            logger.info(f"Frontend request: {action}")
        
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
            jsonNetwork = load_network(value['Network'])
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
            json_network = load_network(value["Network"])

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

        elif action == "resolveDir":
            path_to_folder = value["path"]
            return resolveDir(path=path_to_folder).run()
            
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
            jsonNetwork = load_network(value["Network"])
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)

            return getPartitionSummary(id_=Id, 
                                    lw_core=lw_core, 
                                    data_container=data_container).run()

        elif action == "getCode":
            id_ = value['Id']            
            graph_spec = load_network(value['Network'], as_spec=True)
            
            get_code = getCode(id_=id_, graph_spec=graph_spec)                            
            return get_code.run()

        elif action == "getNetworkInputDim":
            jsonNetwork = load_network(value)

            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)

            return getNetworkInputDim(network=jsonNetwork, 
                                    lw_core=lw_core, 
                                    extras_reader=extras_reader).run()

        elif action == "getNetworkOutputDim":
            jsonNetwork = load_network(value)
            lw_core, extras_reader, data_container = self.create_lw_core(reciever, jsonNetwork)

            return getNetworkOutputDim(lw_core=lw_core, 
                                    extras_reader=extras_reader).run()

        elif action == "getBatchPreviewSample":
            json_network = load_network(value["Network"])
            lw_core, extras_reader, data_container = self.create_lw_core(reciever, json_network)
            outputDims = getNetworkOutputDim(lw_core, extras_reader).run()

            graph_spec = GraphSpec.from_dict(utils.patch_net_connections(json_network))
            lw_core, _, _ = self.create_lw_core(reciever, None, adapter=False)

            previews = getPreviewBatchSample(lw_core, graph_spec, json_network).run()

            return {"previews":previews, "outputDims": outputDims}

        elif action == "getNetworkData":
            json_network = load_network(value["Network"])

            if self._settings_engine is not None:
                new_json_network = autosettings_utils.get_recommendation(json_network, self._settings_engine)
            else:
                new_json_network = {}
                logger.warning("Settings engine is not set. Cannot make recommendations. Using old json_network.")

            for id_,settings in new_json_network.items():
                json_network[id_].update(settings)
                json_network[id_]['getPreview']=True


            lw_core, extras_reader, data_container = self.create_lw_core(reciever, json_network)
            outputDims = getNetworkOutputDim(lw_core, extras_reader).run()

            graph_spec = GraphSpec.from_dict(utils.patch_net_connections(json_network))
            lw_core, _, _ = self.create_lw_core(reciever, None, adapter=False)
            previews = getPreviewBatchSample(lw_core, graph_spec, json_network).run()
            return {"previews":previews, "outputDims": outputDims, "newNetwork":new_json_network}

        elif action == "getPreviewSample":
            layer_id = value["Id"]
            json_network = load_network(value["Network"])
            variable = value["Variable"]
            if variable == '(sample)' or variable is None:
                variable = 'output' # WORKAROUND 

            graph_spec = GraphSpec.from_dict(utils.patch_net_connections(json_network))            
            lw_core, _, _ = self.create_lw_core(reciever, None, adapter=False)

            return getPreviewSample(layer_id, lw_core, graph_spec, variable).run()

        elif action == "getPreviewVariableList":
            layer_id = value["Id"]
            graph_spec = load_network(value["Network"], as_spec=True)
            lw_core, _, _ = self.create_lw_core(reciever, None, adapter=False)
            
            return getPreviewVariableList(layer_id, lw_core, graph_spec).run()

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
            jsonNetwork = load_network(value)
            return getGraphOrder(jsonNetwork=jsonNetwork).run()       

        elif action == "getNotebookImports":
            jsonNetwork = load_network(value)
            return getNotebookImports(jsonNetwork=jsonNetwork).run()          

        elif action == "getNotebookRunscript":
            jsonNetwork = load_network(value)
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
            graph_spec = load_network(value, as_spec=True)
            response = self._core.startCore(graph_spec, self._checkpointDict.copy())
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
