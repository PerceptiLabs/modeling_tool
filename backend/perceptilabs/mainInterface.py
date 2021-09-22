import sys
import os
import logging
import pprint
import time
import json
import threading
from sentry_sdk import configure_scope
from concurrent.futures import ThreadPoolExecutor

import perceptilabs.tracking as tracking

#core interface
from perceptilabs.extractVariables import extractCheckpointInfo
from perceptilabs.coreInterface import coreLogic

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.utils import stringify
from perceptilabs.core_new.errors import LightweightErrorHandler
from perceptilabs.core_new.extras import LayerExtrasReader
from perceptilabs.logconf import APPLICATION_LOGGER, set_user_email
from perceptilabs.lwcore import LightweightCore
from perceptilabs.caching.lightweight_cache import LightweightCache
import perceptilabs.utils as utils
import perceptilabs.dataevents as dataevents
from perceptilabs.messaging.zmq_wrapper import ZmqMessagingFactory, ZmqMessageConsumer
from perceptilabs.messaging import MessageConsumer, MessagingFactory

import perceptilabs.logconf
import perceptilabs.automation.autosettings.utils as autosettings_utils
import perceptilabs.automation.utils as automation_utils
from perceptilabs.caching.utils import get_data_metadata_cache
from perceptilabs.data.base import FeatureSpec, DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.script import ScriptFactory

#LW interface
from perceptilabs.lwInterface import (
    getDataMeta,
    getDataMetaV2,
    getPartitionSummary,
    GetNetworkInputDim,
    getNetworkOutputDim,
    getPreviewSample,
    getPreviewBatchSample,
    getPreviewVariableList
)

#Test interface
from perceptilabs.testInterface import (
    TestLogic
)

logger = logging.getLogger(APPLICATION_LOGGER)


USE_AUTO_SETTINGS = False  # TODO: enable for TF2 (story 1561)
USE_LW_CACHING = True
LW_CACHE_MAX_ITEMS = 25


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
    def __init__(self, cores, testcore, dataDict, lwDict, issue_handler, message_factory=None, session_id='default', allow_headless=False):
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
        self._data_metadata_cache = get_data_metadata_cache().for_compound_keys()

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

        elif action == "headless":
            return self._create_response_headless(value)

        elif action == "getTrainingStatistics":
            response = self._core.getTrainingStatistics(value)
            return response

        elif action == "getGlobalTrainingStatistics":
            response = self._core.get_global_training_statistics()
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

        elif action == "getEndResults":
            response = self._core.getEndResults()
            return response

        elif action == "getStatus":
            response = self._core.getStatus()
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

    def _create_testinterface(self, value):
        models_info = {}
        model_ids = value['models'].keys()
        tests = value["tests"]
        user_email = value['userEmail']
        for model_id in model_ids:
            value_dict = value['models'][model_id]
            graph_spec = self._network_loader.load(value_dict, as_spec=True)
            try:
                dataset_settings_dict = value['datasetSettings'][model_id]
                num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (adil): remove when frontend solution exists
                dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)

                key = ['pipelines', user_email, dataset_settings.compute_hash()]
                data_metadata = self._data_metadata_cache.get(key)

                data_loader = DataLoader.from_settings(dataset_settings, num_repeats=num_repeats, metadata=data_metadata)
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


        logger.info('List of tests %s have been requested for models %s', value['tests'], value.keys())
        self._testcore.setup_test_interface(models_info, tests, user_email)

    def _create_response_tests(self, value, on_finished):
        user_email = value['userEmail']
        self._create_testinterface(value)
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

