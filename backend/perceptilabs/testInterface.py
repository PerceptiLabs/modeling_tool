import os
import logging
import numpy as np
import tensorflow as tf
import platform
import shutil
import threading

from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER
from perceptilabs.createDataObject import createDataObject, subsample_data
import perceptilabs.logconf
import perceptilabs.utils as utils
from perceptilabs.testcore import TestCore, ProcessResults
from perceptilabs.CoreThread import CoreThread


logger = logging.getLogger(APPLICATION_LOGGER)
user_logger = logging.getLogger(USER_LOGGER)


class TestLogic():
    """Main Class that does all the computations for the tests and returns the results
    """

    def __init__(self, issue_handler, model_ids):
        self._issue_handler = issue_handler
        self._model_ids = model_ids
        self._stopped = False

    def setup_test_interface(self, models_info, tests):
        self._models_info = models_info
        self._tests = tests
        self._results = {}

    def run(self, on_finished, user_email=None):
        """
        Runs all the tests for all the models iteratively.

        Args:
            user_email: the email of the user. Optional.
        Returns:
            results: returns dict containing required test results in the appropriate format
        """
        self._core = TestCore(
            model_ids=self._model_ids,
            models_info=self._models_info,
            tests=self._tests,
            issue_handler=self._issue_handler,
            user_email=user_email,
        )
        self._start_testing_thread(on_finished)
        return "Testing started."

    def _start_testing_thread(self, on_finished):
        def run():
            try:
                self._core.run()
            except:
                failed = True
                raise
            else:
                failed = False
            finally:
                on_finished(failed)
        
        try:
            threading.Thread(target=run, daemon=True).start()
        except Exception as e:
            message = "Could not boot up the new thread to run the computations on because of: " + \
                str(e)
            with self._issue_handler.create_issue(message, e) as issue:
                self._issue_handler.put_error(issue.frontend_message)
                logger.error(issue.internal_message)
        else:
            logger.info(
                f"Started core for computing {self._tests} for {self._model_ids}")

    def get_results(self):
        if not self._stopped:
            unprocessed_results = self._core.get_results()
            self._update_results(unprocessed_results)
            return self._results
        else:
            return 'tests were stopped.'

    def _update_results(self, unprocessed_results):
        for test in self._tests:
            self._results[test] = {}
            for model_id in unprocessed_results:
                processed_output = self._process_results(
                    unprocessed_results[model_id][test], test)
                self._results[test][model_id] = processed_output

    def _process_results(self, results, test):
        """Process the results into required format for frontend
        Args:
            results: dict
            test: string
        """
        processed_output = ProcessResults(results, test).run()
        return processed_output

    def process_request(self, request, on_finished=None, value=None):
        logger.debug("{} request is being processed in the testcore.".format(request))
        print(request, self)
        if request == 'StartTest':
            if value:
                user_email = value['user_email']
            return self.run(on_finished, user_email=user_email)
        elif request == 'Stop':
            return self.stop()
        elif request == 'GetResults':
            return self.get_results()
        elif request == 'GetStatus':
            return self.get_status()
        elif request == 'Close':
            return self.close()
        else:
            logger.info('Unknown request {} sent.'.format(request))

    def get_status(self):
        return self._core.get_testcore_status()

    def stop(self):
        self._stopped = True
        try:
            self._core.stop()
        except Exception as e:
            with self._issue_handler.create_issue('Error while stopping model', e) as issue:
                logger.exception(issue.internal_message)

    def close(self):
        try:
            self._core.stop()
            del self._core
        except Exception as e:
            with self._issue_handler.create_issue('Error while closing model', e) as issue:
                logger.exception(issue.internal_message)
