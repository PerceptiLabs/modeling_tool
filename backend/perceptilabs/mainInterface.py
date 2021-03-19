import sys
import os
import logging
import pprint
import time
import threading
from sentry_sdk import configure_scope
from concurrent.futures import ThreadPoolExecutor

from perceptilabs.parser.onnx_converter import *
from perceptilabs.parser.parse_onnx import LayerCheckpoint, Parser

#core interface
from perceptilabs.extractVariables import extractCheckpointInfo
from perceptilabs.s3buckets import S3BucketAdapter
from perceptilabs.aggregation import AggregationRequest, AggregationEngine
from perceptilabs.coreInterface import coreLogic

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.exporter.base import Exporter
from perceptilabs.utils import stringify
from perceptilabs.core_new.errors import LightweightErrorHandler
from perceptilabs.core_new.extras import LayerExtrasReader
from perceptilabs.logconf import APPLICATION_LOGGER, set_user_email
from perceptilabs.lwcore import LightweightCoreAdapter, LightweightCore, LightweightCache
import perceptilabs.utils as utils
import perceptilabs.dataevents as dataevents
from perceptilabs.messaging.zmq_wrapper import ZmqMessagingFactory, ZmqMessageConsumer
from perceptilabs.api.data_container import DataContainer as Exp_DataContainer
from perceptilabs.messaging import MessageConsumer, MessagingFactory

import perceptilabs.logconf
import perceptilabs.autosettings.utils as autosettings_utils
from perceptilabs.modelrecommender import ModelRecommender
from perceptilabs.data.base import FeatureSpec, DataLoader
from perceptilabs.utils import is_tf1x
from perceptilabs.script import ScriptFactory

#LW interface
from perceptilabs.lwInterface import (
    getNotebookImports,
    getNotebookRunscript,
    getGraphOrder,
    getDataMeta,
    getDataMetaV2,
    getPartitionSummary,
    getCode,
    GetNetworkInputDim,
    getNetworkOutputDim,
    getPreviewSample,
    getPreviewBatchSample,
    getPreviewVariableList,
    Parse,
    GetNetworkData,
    ScanCheckpoint,
    CopyJsonModel,
    UploadKernelLogs
)

logger = logging.getLogger(APPLICATION_LOGGER)


USE_AUTO_SETTINGS = is_tf1x()  # TODO: enable for TF2 (story 1561)
USE_LW_CACHING = True
LW_CACHE_MAX_ITEMS = 25 
AGGREGATION_ENGINE_MAX_WORKERS = 2


class NetworkLoader:
    def __init__(self):
        self._visited_layers = set()

    def load(self, json_network, as_spec=False, layers_only=True):
        """ to load the json network in a single location for easy debugging """
        network = json_network.copy()
        
        if (layers_only or as_spec) and ('Layers' in network):
            network = network['Layers']

        self._track_visits(network)
    
        if as_spec:
            network = GraphSpec.from_dict(network)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("loading json network:" + pprint.pformat(network))

        return network

    def _track_visits(self, network):
        """ Sanity check to ensure we haven't gone from visited to not visited. """
        reverted_visits = set()
        for id_ in network:
            if 'visited' not in network[id_]:
                continue
            
            if network[id_]['visited']:
                self._visited_layers.add(id_)
            elif id_ in self._visited_layers:
                reverted_visits.add(id_)

        if reverted_visits:
            logger.warning(f"Layers {','.join(reverted_visits)} changed from visited to not visited")


class Interface():
    def __init__(self, cores, dataDict, checkpointDict, lwDict, issue_handler, message_factory=None, session_id='default', allow_headless=False, trainer='core_v2', experiment_api=False):
        self._allow_headless = allow_headless
        self._network_loader = NetworkLoader()
        self._cores=cores
        self._checkpointDict = checkpointDict
        self._dataDict=dataDict
        self._lwDict=lwDict
        self._issue_handler = issue_handler
        self._session_id = session_id
        self._lw_cache_v2 = LightweightCache(max_size=LW_CACHE_MAX_ITEMS) if USE_LW_CACHING else None
        self._settings_engine = None
        self._trainer = trainer

        if experiment_api:
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

    def _addCore(self, receiver):
        core=coreLogic(receiver, self._issue_handler, self._session_id, trainer=self._trainer)
        self._cores[receiver] = core

    def _setCore(self, receiver):
        if receiver not in self._cores:
            self._addCore(receiver)
        self._core = self._cores[receiver]
        if USE_AUTO_SETTINGS:
            self._settings_engine = autosettings_utils.setup_engine(
                self._create_lw_core_internal(
                    data_loader=None, # TODO: set data loader for TF2 (story 1561)
                    use_issue_handler=False
                )
            )

    def shutDown(self):
        for c in self._cores.values():
            c.Close()
            del c
        sys.exit(1)

    def close_core(self, receiver):
        if receiver in self._cores:
            msg = self._cores[receiver].Close()
            del self._cores[receiver]
            return msg
        else:
            return "No core called %s" %receiver

    def create_lw_core(self, receiver, jsonNetwork, adapter=True):
        graph_spec = GraphSpec.from_dict(jsonNetwork)

        if self._trainer == 'standard':
            data_loader = DataLoader.from_graph_spec(graph_spec)  # TODO(anton.k): REUSE THIS!
        else:
            data_loader = None
        
        if adapter:
            extras_reader = LayerExtrasReader()
            error_handler = LightweightErrorHandler()
            data_dict = {}
            

            lw_core = LightweightCoreAdapter(graph_spec, extras_reader, error_handler, self._core.issue_handler, self._lw_cache_v2, data_dict, data_loader=data_loader)
            return lw_core, extras_reader, data_dict
        else:
            lw_core = self._create_lw_core_internal(data_loader)
            return lw_core, None, None

    def _create_lw_core_internal(self, data_loader, use_issue_handler=True):
        lw_core = LightweightCore(
            issue_handler=(self._core.issue_handler if use_issue_handler else None),
            cache=self._lw_cache_v2,
            data_loader=data_loader
        )
        return lw_core
        

    def create_response(self, request):
        receiver = str(request.get('receiver'))
        action = request.get('action')
        value = request.get('value')
        if action != 'checkCore':
            logger.debug(f"Frontend receiver: {receiver} , Frontend request: {action}")
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("creating response for action: {}. \nFull request:\n{}".format(
                action,
                pprint.pformat(request, depth=3)
            ))

        with configure_scope() as scope:
            scope.set_extra("receiver",receiver)
            scope.set_extra("action",action)
            scope.set_extra("value",value)

        self._setCore(receiver)
        
        try:
            response = self._create_response(receiver, action, value)
        except Exception as e:
            with self._core.issue_handler.create_issue('Error in create_response', e) as issue:
                self._core.issue_handler.put_warning(issue.frontend_message)
                response = {'content': issue.frontend_message}                
                logger.error(issue.internal_message)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("created response for action: {}. \nFull request:\n{}\nResponse:\n{}".format(
                action,
                pprint.pformat(request, depth=3),
                stringify(response)
            ))

        return response, self._core.issue_handler

    def _create_response(self, receiver, action, value):
        #Parse the value and send it to the correct function
        if action == "getDataMeta":
            Id = value['Id']
            jsonNetwork = self._network_loader.load(value['Network'])
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            lw_core, extras_reader, data_container = self.create_lw_core(receiver, jsonNetwork)


            get_data_meta = getDataMetaV2(
                id_=Id, 
                lw_core=lw_core, 
                extras_reader=extras_reader
            )

            return get_data_meta.run()

        elif action == "getSettingsRecommendation":
            #json_network = self._network_loader.load(value["Network"])
            
            #if self._settings_engine is not None:
            #    new_json_network = autosettings_utils.get_recommendation(json_network, self._settings_engine)#
            #else:
            #    new_json_network = {}
            #    logger.warning("Settings engine is not set. Cannot make recommendations")

            return {}#new_json_network
                
        elif action == "getPartitionSummary":
            Id=value["Id"]
            jsonNetwork = self._network_loader.load(value["Network"])
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            lw_core, extras_reader, data_container = self.create_lw_core(receiver, jsonNetwork)

            return getPartitionSummary(id_=Id, 
                                    lw_core=lw_core, 
                                    data_container=data_container).run()

        elif action == "getCode":
            id_ = value['Id']            
            graph_spec = self._network_loader.load(value['Network'], as_spec=True)
            
            get_code = getCode(id_=id_, graph_spec=graph_spec)                            
            return get_code.run()

        elif action == "getNetworkInputDim":
            graph_spec = self._network_loader.load(value, as_spec=True)
            json_network = graph_spec.to_dict()
            
            lw_core, _, _ = self.create_lw_core(receiver, json_network, adapter=False)

            output = GetNetworkInputDim(lw_core, graph_spec).run()
            return output
        elif action == "getNetworkOutputDim":
            jsonNetwork = self._network_loader.load(value)
            lw_core, extras_reader, data_container = self.create_lw_core(receiver, jsonNetwork)

            return getNetworkOutputDim(lw_core=lw_core, 
                                    extras_reader=extras_reader).run()

        elif action == "getBatchPreviewSample":
            json_network = self._network_loader.load(value["Network"])
            lw_core, extras_reader, data_container = self.create_lw_core(receiver, json_network)
            outputDims = getNetworkOutputDim(lw_core, extras_reader).run()

            graph_spec = GraphSpec.from_dict(json_network)
            lw_core, _, _ = self.create_lw_core(receiver, json_network, adapter=False)

            previews, trained_layers_info = getPreviewBatchSample(lw_core, graph_spec, json_network).run()

            return {"previews":previews, "outputDims": outputDims, "trainedLayers": trained_layers_info}

        elif action == "getNetworkData":
            return self._get_network_data(receiver, value)
        
        elif action == "getPreviewSample":
            layer_id = value["Id"]
            json_network = self._network_loader.load(value["Network"])
            variable = value["Variable"]
            if variable == '(sample)' or variable is None:
                variable = 'output' # WORKAROUND 

            graph_spec = GraphSpec.from_dict(json_network)            
            lw_core, _, _ = self.create_lw_core(receiver, json_network, adapter=False)

            return getPreviewSample(layer_id, lw_core, graph_spec, variable).run()

        elif action == "getPreviewVariableList":
            layer_id = value["Id"]
            graph_spec = self._network_loader.load(value["Network"], as_spec=True)
            json_network = graph_spec.to_dict()
            lw_core, _, _ = self.create_lw_core(receiver, json_network, adapter=False)
            
            return getPreviewVariableList(layer_id, lw_core, graph_spec).run()

        elif action == "Parse":     
            return self._parse(value[0])

        elif action == "getGraphOrder":
            jsonNetwork = self._network_loader.load(value)
            return getGraphOrder(jsonNetwork=jsonNetwork).run()       

        elif action == "getNotebookImports":
            jsonNetwork = self._network_loader.load(value)
            return getNotebookImports(jsonNetwork=jsonNetwork).run()          

        elif action == "getNotebookRunscript":
            jsonNetwork = self._network_loader.load(value)
            return getNotebookRunscript(jsonNetwork=jsonNetwork).run()

        elif action == "Close":  
            self.shutDown()

        elif action == "closeCore":   
            return self.close_core(receiver)

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
            return self._create_response_headless(value)

        elif action == "getModelRecommendation":
            return self._create_response_model_recommendation(value)

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
            CopyJsonModel(value['copyJson_path']).run()
            graph_spec = self._network_loader.load(value, as_spec=True)
            
            self._core.set_running_mode('training')            
            model_id = int(value.get('modelId', None))
            response = self._core.startCore(graph_spec, model_id)
            return response

        elif action == "startTest":
            graph_spec = self._network_loader.load(value, as_spec=True)
            model_id = value.get('modelId', None)
            if model_id is not None:
                model_id = int(model_id)
            response = self._core.startTest(graph_spec, model_id)
            return response


        elif action =="getTestStatus":
            response = self._core.getTestStatus()
            return response

        elif action == "nextStep":
            response = self._core.nextStep()
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
            response = self._create_response_export(value, receiver)
            return response

        elif action == "isTrained":
            result = self._core.isTrained()
            response = {'result':result, 'receiver':receiver}
            return response

        elif action == "SaveTrained":  
            response = self._core.saveNetwork(value)
            return response

        elif action == "ScanCheckpoint":
            return ScanCheckpoint(path = value).run()

        elif action == "getEndResults":
            # time.sleep(3)
            response = self._core.getEndResults()
            return response

        elif action == "getStatus":
            response = self._core.getStatus()
            return response

        elif action == "setUser":
            response = self.on_set_user(value)
            return response
        
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
        elif action == 'UploadKernelLogs':
            uploader = UploadKernelLogs(value, self._session_id)
            response = uploader.run()
            return response
        else:
            raise LookupError(f"The requested action '{action}' does not exist")

    def on_set_user(self, value):
        user = value
        with configure_scope() as scope:
            scope.user = {"email" : user}

        perceptilabs.logconf.set_user_email(user)
        logger.info("User has been set to %s" % str(value))
        dataevents.on_user_email_set()
        
        return "User has been set to " + value
        
    def _get_network_data(self, receiver, value):
        json_network = value["Network"]
            
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("_get_network_data input network: \n" + stringify(json_network))
        
        graph_spec = self._network_loader.load(json_network, as_spec=True)
        lw_core, _, _ = self.create_lw_core(receiver, json_network, adapter=False)
        output = GetNetworkData(graph_spec, lw_core, self._settings_engine).run()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("_get_network_data output network: \n" + stringify(output))
            
        return output
        
    def _get_receiver_mode(self,receiver_id):
        """
        Requests to start testing contain 't' in receiver id.
        Some requests to export model contain 'e' in receiver id.
        Args:
            receiver_id (string): receiver id for the request
        """
        if receiver_id is not None:
            if 'e' not in receiver_id:
                mode = 'export_while_training'
            elif 'e' in receiver_id:
                mode = 'export_after_training'
            elif 't' in receiver_id:
                mode = 'testing'
        else:
            return None
                
        return mode

    def _create_response_headless(self, request_value):
        """ Toggles headless mode on/off. Returns None if successful """
        if not self._allow_headless:
            return None        
        return self._core.set_headless(active=request_value)

    def _create_response_model_recommendation(self, request_value):
        feature_specs = {}
        
        for feature_name, feature_info in request_value.items():
            feature_specs[feature_name] = FeatureSpec(
                datatype=feature_info['datatype'].lower(),
                iotype=feature_info['iotype'].lower(),
                file_path=feature_info['csv_path']
            )

        recommender = ModelRecommender()
        graph_spec = recommender.get_graph(feature_specs)
        json_network = graph_spec.to_dict()
        return json_network
    
    def _create_response_export(self, value, receiver):
        if utils.is_tf2x():
            return self._create_response_export_tf2x(value, receiver)
        else:
            return self._create_response_export_tf1x(value, receiver)

    def _create_response_export_tf2x(self, value, receiver):
        # first check if checkpoint exists if export is requested after training
        mode = self._get_receiver_mode(receiver)
        if mode == 'export_while_training':                    
            _model_id = value.get('modelId', None)
            if _model_id is not None:
                _model_id = int(_model_id)
            response = self._core.exportNetwork(value, graph_spec=None, model_id=_model_id)
            return response
        elif mode == 'export_after_training':
            graph_spec = self._network_loader.load(value, as_spec=True)
            response = self._export_using_exporter(value, path=value['Location'], graph_spec=graph_spec)
            return response
        else:
            return {'content':'The model is not trained.'}

    def _create_response_export_tf1x(self, value, receiver):
        mode = self._get_receiver_mode(receiver)
        if mode == 'export_while_training':
            if (ScanCheckpoint(path = value['path']).run() or value["Type"] == 'ipynb'):
                model_id = value.get('modelId', None)
                if model_id is not None:
                    model_id = int(model_id)
                response = self._core.exportNetwork(value, graph_spec=None, model_id=model_id)
                return response
        elif mode == 'export_after_training':
            graph_spec = self._network_loader.load(value, as_spec=True)
            response = self._core.exportNetwork(value, graph_spec, model_id=None)
            return response
        else:
            return {'content':'The model is not trained.'}

    def _parse(self, path):
        frozen_pb_model = load_tf1x_frozen(path)
        _, onnx_model = create_onnx_from_tf1x(frozen_pb_model)
        parser = Parser(onnx_model)
        layer_checkpoint_list = parser.parse()
        jsonNetwork = parser.save_json(layer_checkpoint_list[0])
        return jsonNetwork


    def _export_using_exporter(self, value, path, graph_spec):
        script_factory = ScriptFactory(
            mode='tf2x' if utils.is_tf2x() else 'tf1x',
            simple_message_bus=True,
        )
        try:
            exporter = Exporter.from_disk(path, graph_spec, script_factory)
        except:
            return {"content": f"Can't export a model that hasn't been trained yet."}
        export_path = os.path.join(path, value['name'])
        exporter.export_inference(export_path)
        return {"content": f"Exporting of model requested to the path {path}"}

