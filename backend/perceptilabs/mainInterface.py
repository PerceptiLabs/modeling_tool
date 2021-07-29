import sys
import os
import logging
import pprint
import time
import json
import threading
from sentry_sdk import configure_scope
from concurrent.futures import ThreadPoolExecutor

from perceptilabs.parser.onnx_converter import load_tf1x_frozen, create_onnx_from_tf1x
from perceptilabs.parser.parse_onnx import LayerCheckpoint, Parser
import perceptilabs.tracking as tracking

#core interface
from perceptilabs.extractVariables import extractCheckpointInfo
from perceptilabs.s3buckets import S3BucketAdapter
from perceptilabs.aggregation import AggregationRequest, AggregationEngine
from perceptilabs.coreInterface import coreLogic

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.utils import stringify
from perceptilabs import __version__
from perceptilabs.core_new.errors import LightweightErrorHandler
from perceptilabs.core_new.extras import LayerExtrasReader
from perceptilabs.logconf import APPLICATION_LOGGER, set_user_email
from perceptilabs.lwcore import LightweightCore, LightweightCache
import perceptilabs.utils as utils
import perceptilabs.dataevents as dataevents
from perceptilabs.messaging.zmq_wrapper import ZmqMessagingFactory, ZmqMessageConsumer
from perceptilabs.api.data_container import DataContainer as Exp_DataContainer
from perceptilabs.messaging import MessageConsumer, MessagingFactory

import perceptilabs.logconf
import perceptilabs.automation.autosettings.utils as autosettings_utils
import perceptilabs.automation.utils as automation_utils
from perceptilabs.data.base import FeatureSpec, DataLoader
from perceptilabs.script import ScriptFactory

#LW interface
from perceptilabs.lwInterface import (
    getNotebookImports,
    getNotebookRunscript,
    getGraphOrder,
    getDataMeta,
    getDataMetaV2,
    getPartitionSummary,
    GetNetworkInputDim,
    getNetworkOutputDim,
    getPreviewSample,
    getPreviewBatchSample,
    getPreviewVariableList,
    Parse,
    UploadKernelLogs
)

#Test interface
from perceptilabs.testInterface import (
    TestLogic
)

logger = logging.getLogger(APPLICATION_LOGGER)


USE_AUTO_SETTINGS = False  # TODO: enable for TF2 (story 1561)
USE_LW_CACHING = True
LW_CACHE_MAX_ITEMS = 25 
AGGREGATION_ENGINE_MAX_WORKERS = 2


class NetworkLoader:
    def __init__(self):
        self._visited_layers = set()

    def load(self, json_network, as_spec=False, layers_only=True):
        """ to load the json network in a single location for easy debugging """
        network = json_network.copy()
        if (layers_only or as_spec):
            if 'Layers' in network:
                network = network['Layers']
            elif 'layers' in network:
                network = network['layers']
        
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
    def __init__(self, cores, testcore, dataDict, lwDict, issue_handler, message_factory=None, session_id='default', allow_headless=False, experiment_api=False):
        self._allow_headless = allow_headless
        self._network_loader = NetworkLoader() 
        self._cores=cores
        self._testcore = testcore
        self._dataDict=dataDict
        self._lwDict=lwDict
        self._issue_handler = issue_handler
        self._session_id = session_id
        self._lw_cache_v2 = LightweightCache(max_size=LW_CACHE_MAX_ITEMS) if USE_LW_CACHING else None
        self._settings_engine = None

        if experiment_api:
            self._data_container = Exp_DataContainer()
            self._aggregation_engine = self._setup_aggregation_engine(self._data_container)
            self._start_experiment_thread(message_factory)

        self._mode = 'ephemeral'
        self._has_remaining_work = True
        self._failed = False

    @property
    def has_failed(self):
        return self._failed

    @property
    def has_remaining_work(self):
        if self._mode == 'ephemeral':
            return self._has_remaining_work            
        else:
            return True

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
        core = coreLogic(receiver, self._issue_handler, self._session_id)
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

    def _set_testcore(self, model_ids):
        """
        sets/creates the testcore with given receiver ids.
        Args:
            receivers (str): receiver id for request
        """
        self._testcore = TestLogic(self._issue_handler, model_ids)

    def shutDown(self):
        for c in self._cores.values():
            c.Close()
            del c    
        if self._testcore:
            del self._testcore
        sys.exit(1)
        

    def close_core(self, receiver): 
        if receiver in self._cores:
            msg = self._cores[receiver].Close()
            del self._cores[receiver]
            return msg
        elif receiver == 'test_requests':
            #self._testcore.close()
            #del self._testcore
            return
        else:
            return "No core called %s exists" %receiver

    def create_lw_core(self, receiver, jsonNetwork, adapter=True, dataset_settings=None):
        graph_spec = GraphSpec.from_dict(jsonNetwork)
        if not dataset_settings:
            raise RuntimeError("Dataset settings must be set!")
            
        data_loader = DataLoader.from_dict(dataset_settings)  # TODO(anton.k): REUSE THIS!
        lw_core = self._create_lw_core_internal(data_loader)
        return lw_core, None, None

    def _create_lw_core_internal(self, data_loader, use_issue_handler=True):
        lw_core = LightweightCore(
            issue_handler=(self._issue_handler if use_issue_handler else None),
            cache=self._lw_cache_v2,
            data_loader=data_loader
        )
        return lw_core

    def create_response_with_errors(self, request, is_retry=False, on_finished=None):
        content, issue_handler = self.create_response(
            request, is_retry=is_retry, on_finished=on_finished)
        response = {'content': content}

        error_list = issue_handler.pop_errors()
        if error_list:
            response['errorMessage'] = error_list

        warning_list = issue_handler.pop_warnings()
        if warning_list:
            response['warningMessage'] = warning_list

        log_list = issue_handler.pop_logs()
        if log_list:
            response['consoleLogs'] = log_list

        info_list = issue_handler.pop_info()
        if info_list:
            response['generalLogs'] = info_list
        
        return response

    def create_response(self, request, is_retry=False, on_finished=None):
        receiver = str(request.get('receiver'))
        action = request.get('action')
        value = request.get('value')
        logger.info(f"Frontend receiver: {receiver} , Frontend request: {action}")
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("creating response for action: {}. \nFull request:\n{}".format(
                action,
                pprint.pformat(request, depth=3)
            ))

        with configure_scope() as scope:
            scope.set_extra("receiver",receiver)
            scope.set_extra("action",action)
            scope.set_extra("value",value)

        if receiver == 'test_requests':
            if action == 'startTests':
                model_ids = value['models'].keys()
                self._set_testcore(model_ids)
        else:
            self._setCore(receiver)
        
        try:
            response = self._create_response(receiver, action, value, is_retry, on_finished)
        except Exception as e:
            message = f"Error in create_response (action='{action}')"
            with self._issue_handler.create_issue(message, e) as issue:
                self._issue_handler.put_warning(issue.frontend_message)
                response = {'content': issue.frontend_message}
                logger.error(issue.internal_message)

                
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("created response for action: {}. \nFull request:\n{}\nResponse:\n{}".format(
                action,
                pprint.pformat(request, depth=3),
                stringify(response)
            ))

        return response, self._issue_handler

    def _create_response(self, receiver, action, value, is_retry, on_finished):
        #Parse the value and send it to the correct function
        if action == "getDataMeta":
            return self._create_response_get_data_meta(value, receiver)

        elif action == "getSettingsRecommendation":
            #json_network = self._network_loader.load(value["Network"])
            
            #if self._settings_engine is not None:
            #    new_json_network = autosettings_utils.get_recommendation(json_network, self._settings_engine)#
            #else:
            #    new_json_network = {}
            #    logger.warning("Settings engine is not set. Cannot make recommendations")

            return {}#new_json_network
                
        elif action == "getPartitionSummary":
            return self._create_response_get_partition_summary(value, receiver)

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
            return self._create_response_get_preview_var_list(value, receiver)

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

        elif action == "version":
            return __version__

        elif action == "headless":
            return self._create_response_headless(value)

        elif action == "getTrainingStatistics":
            response = self._core.getTrainingStatistics(value)
            return response

        elif action == "getGlobalTrainingStatistics":
            response = self._core.get_global_training_statistics()
            return response
        

        elif action == "getS3Keys":
            adapter = S3BucketAdapter(value['bucket'],
                                value['aws_access_key_id'], value['aws_secret_access_key'])
            response = adapter.get_keys(value['delimiter'], value['prefix'])
            return response

        elif action == "Start":
            return self._create_response_start_training(value, is_retry, on_finished)

        elif action == "nextStep":
            response = self._core.nextStep()
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

        elif action == "startTests":
            response = self._create_response_tests(value, on_finished)
            return response

        elif action == "getTestResults":
            response = self._testcore.process_request('GetResults')
            return response

        elif action == 'getTestStatus':
            response = self._testcore.process_request('GetStatus')
            return response

        elif action == "StopTests":
            response = self._testcore.process_request('Stop')
            return response
        
        elif action == "CloseTests":
            response = self._testcore.process_request('Close')
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
        
    def _create_response_headless(self, request_value):
        """ Toggles headless mode on/off. Returns None if successful """
        if not self._allow_headless:
            return None        
        return self._core.set_headless(active=request_value)

    def _create_response_export(self, export_settings, receiver):
        response = self._core.export_network(export_settings)
        logger.info("Created export response while training")            
        return response
    
    def _create_response_start_training(self, request_value, is_retry, on_finished):
        graph_spec = self._network_loader.load(request_value, as_spec=True)
        
        self._core.set_running_mode('training')            
        model_id = int(request_value.get('modelId', None))
        user_email = request_value.get('userEmail', None)      
        training_settings = request_value.get('trainSettings', None)        
        dataset_settings = request_value.get('datasetSettings', None)
        checkpoint_directory = request_value.get('checkpointDirectory', None)
        load_checkpoint = request_value.get('loadCheckpoint', False)
        
        response = self._core.start_core(
            graph_spec,
            model_id,
            user_email,
            training_settings,
            dataset_settings,
            checkpoint_directory,
            load_checkpoint,
            on_finished=on_finished,
            is_retry=is_retry
        )
        return response

    def _parse(self, path):
        frozen_pb_model = load_tf1x_frozen(path)
        _, onnx_model = create_onnx_from_tf1x(frozen_pb_model)
        parser = Parser(onnx_model)
        layer_checkpoint_list = parser.parse()
        jsonNetwork = parser.save_json(layer_checkpoint_list[0])
        return jsonNetwork

    def _create_response_tests(self, value, on_finished):
        models_info = {}
        model_ids = value['models'].keys()
        for model_id in model_ids:
            value_dict = value['models'][model_id]
            graph_spec = self._network_loader.load(value_dict, as_spec=True)
            
            try:
                dataset_settings = value['datasetSettings'][model_id]
                data_loader = DataLoader.from_dict(dataset_settings)
            except Exception as e:
                message = str(e)
                with self._issue_handler.create_issue(message, exception=None, as_bug=False) as issue:
                    self._issue_handler.put_error("Error while loading dataset.")
                    logger.info(issue.internal_message)
                    return 
            models_info[model_id] = {
                'graph_spec': graph_spec, 
                'checkpoint_directory': value_dict['checkpoint_directory'], 
                'data_path': value_dict['data_path'],
                'data_loader': data_loader,
                'model_name': value_dict['model_name'],
            } 
        tests = value["tests"]
        user_email = value['userEmail']
        logger.info('List of tests %s have been requested for models %s', value['tests'], value.keys())
        self._testcore.setup_test_interface(models_info, tests)
        response = self._testcore.process_request(
            'StartTest', on_finished=on_finished, value={'user_email':user_email})
        return response
    
    def _create_response_get_partition_summary(self, request_value, receiver):
            Id=request_value["Id"]
            jsonNetwork = self._network_loader.load(request_value["Network"])
            if "layerSettings" in request_value:
                layerSettings = request_value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings
            dataset_settings = request_value.get('datasetSettings', None)

            lw_core, extras_reader, data_container = self.create_lw_core(receiver, jsonNetwork, dataset_settings=dataset_settings)

            return getPartitionSummary(id_=Id, 
                                    lw_core=lw_core, 
                                    data_container=data_container).run()

    def _create_response_get_data_meta(self, request_value, receiver):
            Id = request_value['Id']
            jsonNetwork = self._network_loader.load(request_value['Network'])
            dataset_settings = None

            if "layerSettings" in request_value:
                layerSettings = request_value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            if "datasetSettings" in request_value:
                dataset_settings = request_value["datasetSettings"]

            lw_core, extras_reader, data_container = self.create_lw_core(receiver, jsonNetwork, dataset_settings=dataset_settings)


            get_data_meta = getDataMetaV2(
                id_=Id, 
                lw_core=lw_core, 
                extras_reader=extras_reader
            )

            return get_data_meta.run()

    def _create_response_get_preview_var_list(self, request_value, receiver):
        layer_id = request_value["Id"]
        graph_spec = self._network_loader.load(request_value["Network"], as_spec=True)
        json_network = graph_spec.to_dict()
        dataset_settings = request_value["datasetSettings"]
        lw_core, _, _ = self.create_lw_core(receiver, json_network, adapter=False, dataset_settings=dataset_settings)
        
        return getPreviewVariableList(layer_id, lw_core, graph_spec).run()
        
