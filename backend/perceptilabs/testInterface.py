import os
import logging
import numpy as np
import tensorflow as tf
import platform
import shutil

from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER
from perceptilabs.createDataObject import createDataObject, subsample_data
import perceptilabs.logconf
import perceptilabs.utils as utils
from perceptilabs.testcore import TestCore, ProcessResults

logger = logging.getLogger(APPLICATION_LOGGER)
user_logger = logging.getLogger(USER_LOGGER)

class CreateTestCore():
    def __init__(self, receivers, issue_handler):
        self._issue_handler = issue_handler
        self._receivers = receivers
    
    def run(self):
        core = TestCore(self._receivers, self._issue_handler)
        return core

class GetTestResults():
    """Main Class that does all the computations for the tests and returns the results
    """
    def __init__(self, models_info, testcore, tests):
        self._models_info = models_info
        self._tests = tests
        self._testcore = testcore
        #TODO(mukund): load data for all the models at once once project hub is up
        
    def run(self, user_email=None):
        """
        Runs all the tests for all the models iteratively.

        Args:
            user_email: the email of the user. Optional.
        Returns:
            results: returns dict containing required test results in the appropriate format
        """
        results = {}
        for receiver_id in self._models_info:
            model_info = self._models_info[receiver_id]
            self._testcore.load_data(
                model_info['graph_spec'], model_info['data_path'], method='graph_spec'
            )
            self._testcore.load_model(
                receiver_id, model_path=model_info['model_path'], graph_spec=model_info['graph_spec']
            )

        unprocessed_results = self._testcore.run_tests(tests=self._tests, user_email=user_email) #TODO(mukund): use corethread to run the tests.
        for test in self._tests:
            results[test] = {}
            for receiver_id in unprocessed_results:
                processed_output = self._process_results(unprocessed_results[receiver_id][test], test)
                results[test][receiver_id] = processed_output
        return results

    def _process_results(self, results, test):
        """Process the results into required format for frontend
        Args:
            results: dict
            test: string
        """
        processed_output = ProcessResults(results, test).run()
        return processed_output
    
    
    
    
    
    
