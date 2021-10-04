import os
import sys
import logging
import pprint
from sentry_sdk import configure_scope


from perceptilabs.coreInterface import coreLogic
from perceptilabs.utils import stringify
from perceptilabs.logconf import APPLICATION_LOGGER, set_user_email
from perceptilabs.caching.utils import get_data_metadata_cache
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.testInterface import TestLogic
from perceptilabs.script import ScriptFactory
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.files import FileAccess
from perceptilabs.testInterface import TestLogic
import perceptilabs.utils as utils


logger = logging.getLogger(APPLICATION_LOGGER)


class Interface():
    def __init__(self, cores, testcore, issue_handler, message_factory=None, session_id='default', allow_headless=False):
        self._allow_headless = allow_headless
        self._cores=cores
        self._testcore = testcore
        self._issue_handler = issue_handler
        self._session_id = session_id
        
        self._settings_engine = None
        self._data_metadata_cache = get_data_metadata_cache().for_compound_keys()

        self._mode = 'ephemeral'
        self._has_remaining_work = True
        self._failed = False

        self._model_access = ModelAccess(ScriptFactory())

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
        if action == "Close":
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
        graph_dict = request_value['Layers']
        graph_spec = self._model_access.get_graph_spec(model_id=graph_dict)  # TODO: f/e should send an ID
        
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

            graph_dict = value_dict['layers']
            graph_spec = self._model_access.get_graph_spec(model_id=graph_dict)  # TODO: f/e should send an ID
            try:
                dataset_settings_dict = value['datasetSettings'][model_id]
                num_repeats = utils.get_num_data_repeats(dataset_settings_dict)   #TODO (adil): remove when frontend solution exists
                dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)

                key = ['pipelines', user_email, dataset_settings.compute_hash()]
                data_metadata = self._data_metadata_cache.get(key)

                csv_path = value['datasetSettings'][model_id]['filePath']
                file_access = FileAccess(os.path.dirname(csv_path)) 
                
                data_loader = DataLoader.from_csv(
                    file_access, csv_path, dataset_settings,
                    num_repeats=num_repeats, metadata=data_metadata
                )
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

    
