import time
import logging
from queue import Empty
from datetime import datetime

import sentry_sdk

from perceptilabs.gradio_serving.base import GradioLauncher
import perceptilabs.tracking as tracking

logger = logging.getLogger(__name__)


class ServingSessionInterface():
    def __init__(self, message_broker, event_tracker, model_access, epochs_access, results_access):
        self._message_broker = message_broker
        self._event_tracker = event_tracker
        self._model_access = model_access
        self._epochs_access = epochs_access
        self._results_access = results_access

    def run(self, *args, **kwargs):
        for _ in self.run_stepwise(*args, **kwargs):
            pass

    def run_stepwise(self, data_loader, graph_spec_dict, model_id, training_session_id, serving_session_id, model_name, user_email, results_interval=3.0, is_retry=False, logrocket_url=''):

        try:
            launcher = self._setup_launcher(
                graph_spec_dict, training_session_id, data_loader, model_name, model_id, user_email)
            
            with self._message_broker.subscription() as queue:
                yield from self._main_loop(queue, results_interval, serving_session_id, launcher)
        except Exception as e:
            logger.exception("Exception in serving session interface!")
            
            with sentry_sdk.push_scope() as scope:
                scope.set_user({'email': user_email})                
                scope.set_extra('graph_spec', graph_spec_dict)
                scope.set_extra('dataset_settings', data_loader.settings)
                scope.set_extra('model_id', model_id)
                scope.set_extra('training_session_id', training_session_id)
                scope.set_extra('logrocket_url', logrocket_url)            
            
                sentry_sdk.capture_exception(e)
                sentry_sdk.flush()                        
            

    def _setup_launcher(self, graph_spec_dict, training_session_id, data_loader, model_name, model_id, user_email):
        graph_spec = self._model_access.get_graph_spec(graph_spec_dict)
        
        epoch_id = self._epochs_access.get_latest(
            training_session_id=training_session_id,
            require_checkpoint=True,
            require_trainer_state=True
        )

        def on_serving_started():
            tracking.send_model_served(self._event_tracker, user_email, model_id)            

        launcher = GradioLauncher(self._model_access, self._epochs_access)
        launcher.start(
            graph_spec,
            data_loader,
            training_session_id,
            model_name,
            on_serving_started=on_serving_started
        )
        return launcher
        
    def _main_loop(self, queue, results_interval, serving_session_id, launcher):
        is_running = True

        while is_running:
            time.sleep(results_interval)            
            try:
                for message in iter(queue.get_nowait, None):
                    event = message['event']
                    payload = message.get('payload', {})
                    
                    if event == 'serving-stop' and payload['serving_session_id'] == serving_session_id:
                        is_running = False
            except Empty:
                results = {
                    'url': launcher.get_url(),
                    'last_update': datetime.now().timestamp()  # Current unix time
                }
                self._results_access.store(serving_session_id, results)
            finally:
                yield


