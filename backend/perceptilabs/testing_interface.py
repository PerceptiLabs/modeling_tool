import time
import logging
from queue import Empty

import perceptilabs.utils as utils
from perceptilabs.testcore import TestCore, ProcessResults
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.utils import KernelError


logger = logging.getLogger(APPLICATION_LOGGER)


class TestingSessionInterface():
    """Main Class that does all the computations for the tests and returns the results
    """
    def __init__(self, message_broker, model_access, epochs_access, results_access):
        self._message_broker = message_broker
        self._model_access = model_access
        self._epochs_access = epochs_access
        self._results_access = results_access

    def run(self, *args, **kwargs):
        for _ in self.run_stepwise(*args, **kwargs):
            pass

    def run_stepwise(self, testing_session_id, models, tests, user_email, results_interval=None):
        try:
            test_core = self._setup_test_core(testing_session_id, models, tests, user_email)

            with self._message_broker.subscription() as queue:
                yield from self._main_loop(queue, test_core, results_interval, testing_session_id)
                
        except Exception as e:
            error = KernelError.from_exception(e, "Error during testing!")            
            self._results_access.store(testing_session_id, {'error': error.to_dict()})

            # TODO: Sentry capture here???? probably on original exception...            
            logger.exception("Exception in training session interface!")

    def _main_loop(self, queue, core, results_interval, testing_session_id):            
        testing_step = core.run_stepwise()
        testing_sentinel = object()
            
        last_update = -1
        is_running = True

        while is_running:
            self._maybe_handle_messages(queue, core)

            testing_step_result = next(testing_step, testing_sentinel)
            is_running = testing_step_result is not testing_sentinel
            
            last_update = self._maybe_write_results(
                results_interval, last_update, core, testing_session_id, is_running)

            yield

    def _setup_test_core(self, testing_session_id, models, tests, user_email):
        core = TestCore(
            testing_session_id,
            list(models.keys()),
            models,
            tests,
            user_email=user_email,
        )
        return core
            
                
    def _maybe_write_results(self, results_interval, last_update, core, testing_session_id, is_running):
        time_since_update = time.time() - last_update
        
        if (results_interval is None) or (time_since_update >= results_interval) or not is_running:

            self._write_results(core, testing_session_id)
            return time.time()
        else:
            return last_update

    def _write_results(self, core, testing_session_id):         
        status = core.get_testcore_status()
        unprocessed_results = core.get_results()

        results = {}
        for test in core.tests:
            results[test] = {}
            for model_id in unprocessed_results:
                processed_output = ProcessResults(
                    unprocessed_results[model_id][test], test).run()
                results[test][model_id] = processed_output
                
        all_results = {'results': results, 'status': status}
        self._results_access.store(testing_session_id, all_results)

    def _maybe_handle_messages(self, queue, core):
        try:
            for message in iter(queue.get_nowait, None):
                event = message['event']
                payload = message.get('payload', {})
                
                if event == 'testing-stop' and payload['testing_session_id'] == core.session_id:
                    core.stop()                
        except Empty:
            pass