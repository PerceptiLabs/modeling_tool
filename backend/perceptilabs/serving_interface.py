import time
import logging
from queue import Empty
from datetime import datetime

from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.gradio_serving.base import GradioLauncher
import perceptilabs.tracking as tracking

logger = logging.getLogger(APPLICATION_LOGGER)


class ServingSessionInterface():
    def __init__(self, message_broker, model_access, epochs_access, results_access):
        self._message_broker = message_broker        
        self._model_access = model_access
        self._epochs_access = epochs_access
        self._results_access = results_access

    def run(self, *args, **kwargs):
        for _ in self.run_stepwise(*args, **kwargs):
            pass

    def run_stepwise(self, data_loader, graph_spec_dict, model_id, training_session_id, serving_session_id, model_name, user_email, results_interval=3.0, is_retry=False):
        graph_spec = self._model_access.get_graph_spec(graph_spec_dict)
        
        epoch_id = self._epochs_access.get_latest(
            training_session_id=training_session_id,
            require_checkpoint=True,
            require_trainer_state=True
        )

        def on_serving_started():
            tracking.send_model_served(user_email, model_id)            

        launcher = GradioLauncher(self._model_access, self._epochs_access)
        launcher.start(
            graph_spec,
            data_loader,
            training_session_id,
            model_name,
            on_serving_started=on_serving_started
        )

        is_running = True
        with self._message_broker.subscription() as queue:        
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


