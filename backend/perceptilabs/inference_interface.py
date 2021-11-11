import os
import sys
import logging

from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


class InferenceInterface:
    def __init__(self, task_executor, message_broker, testing_results_access, serving_results_access):
        self._task_executor = task_executor
        self._message_broker = message_broker
        self._testing_results_access = testing_results_access
        self._serving_results_access = serving_results_access                

    def start_serving(self, serving_type, dataset_settings_dict, graph_spec_dict, model_id, training_session_id, model_name, user_email):
        serving_session_id = self._serving_results_access.new_id()
        self._task_executor.enqueue('serving_task', serving_type, dataset_settings_dict, graph_spec_dict, model_id, training_session_id, model_name, user_email, serving_session_id)
        return serving_session_id

    def get_serving_status(self, serving_session_id):
        status_dict = self._serving_results_access.get_latest(serving_session_id)
        return status_dict

    def stop_serving(self, serving_session_id):
        self._message_broker.publish(
            {'event': 'serving-stop', 'payload': {'serving_session_id': serving_session_id}})

    def start_testing(self, models_info, tests, user_email):
        testing_session_id = self._testing_results_access.new_id()
        self._task_executor.enqueue('testing_task', testing_session_id, models_info, tests, user_email)
        return testing_session_id
    
    def get_testing_status(self, testing_session_id):
        results_dict = self._testing_results_access.get_latest(testing_session_id)

        if results_dict:
            results = results_dict.get('status', {})
            results['error'] = results_dict.get('error')
            return results
        else:
            return {}

    def get_testing_results(self, testing_session_id):
        results_dict = self._testing_results_access.get_latest(testing_session_id)

        if results_dict:
            return results_dict['results']
        else:
            return {}

