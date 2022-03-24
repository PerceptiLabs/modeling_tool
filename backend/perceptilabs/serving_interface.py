import time
import logging
from queue import Empty
from datetime import datetime
import os

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.gradio_serving.base import GradioStrategy
from perceptilabs.zipfile_serving import ZipfileStrategy
import perceptilabs.tracking as tracking
import perceptilabs.utils as utils

logger = logging.getLogger(__name__)


class ServingSessionInterface:
    def __init__(self, serving_settings, message_broker, event_tracker, model_access, model_archives_access, epochs_access, results_access, tensorflow_support_access, ttl):
        self._serving_settings = serving_settings
        self._message_broker = message_broker
        self._event_tracker = event_tracker
        self._model_access = model_access
        self._model_archives_access = model_archives_access
        self._epochs_access = epochs_access
        self._results_access = results_access
        self._tensorflow_support_access = tensorflow_support_access
        self._ttl = ttl
        
    def run(self, call_context, *args, **kwargs):
        for _ in self.run_stepwise(call_context, *args, **kwargs):
            pass

    def run_stepwise(self, call_context, data_loader, model_id, training_session_id, serving_session_id, model_name, results_interval=3.0, is_retry=False, logrocket_url='', graph_settings=None):
        call_context = call_context.push(
            dataset_settings = data_loader.settings,
            model_id = model_id,
            training_session_id = training_session_id,
            logrocket_url = logrocket_url,
        )

        try:
            self._tensorflow_support_access.set_tfhub_env_var(call_context)
            
            strategy = self._setup_strategy(
                call_context, training_session_id, serving_session_id, data_loader, model_name, model_id, graph_settings)

            strategy.start()
            logger.info("Serving strategy start called")
            
            with self._message_broker.subscription() as queue:
                yield from self._main_loop(queue, results_interval, serving_session_id, strategy)
        except Exception as e:
            logger.exception("Exception in serving session interface!")
            utils.send_ex_to_sentry(e, call_context)
            raise  # TODO. the other interfaces has a handle_error method.... they DON'T re-raise, but they do insert an error
        finally:
            self._results_access.remove(serving_session_id)

    def _setup_strategy(self, call_context, training_session_id, serving_session_id, data_loader, model_name, model_id, graph_settings):
        mode = self._serving_settings['mode']
        logger.info(f"Setting up serving strategy with mode {mode}")
        
        if graph_settings:
            graph_spec = GraphSpec.from_dict(graph_settings)
        else:
            graph_spec = self._model_access.get_graph_spec(call_context, model_id)
            
        def on_serving_started():
            tracking.send_model_served(self._event_tracker, call_context, model_id)
            logger.info("Serving strategy called")

        include_preprocessing = not self._serving_settings['ExcludePreProcessing']
        include_postprocessing = not self._serving_settings['ExcludePostProcessing']
        
        if mode == 'gradio':
            return GradioStrategy(
                call_context,
                self._model_access,
                self._epochs_access,
                model_id,
                graph_spec,
                data_loader,
                training_session_id,
                model_name,
                on_serving_started=on_serving_started,            
                include_preprocessing=include_preprocessing,
                include_postprocessing=include_postprocessing,
            )
        elif mode == 'zip':
            target_url = f"inference/serving/{serving_session_id}/file"
            
            export_dir = self._results_access.get_serving_directory(serving_session_id)
            return ZipfileStrategy(
                call_context,
                self._model_archives_access,
                self._epochs_access,
                model_id,
                graph_spec,
                data_loader,
                training_session_id,
                model_name,
                self._serving_settings['exportSettings'],
                export_dir,
                target_url,
                on_serving_started=on_serving_started,            
                include_preprocessing=include_preprocessing,
                include_postprocessing=include_postprocessing,
                frontend_settings=self._serving_settings.get('frontendSettings'),
                graph_settings=self._serving_settings.get('graphSettings'),
                dataset_settings=self._serving_settings.get('datasetSettings'),
                training_settings=self._serving_settings.get('trainingSettings'),
                ttl=self._ttl
            )        
        else:
            raise NotImplementedError(f"Serving mode {mode} not implemented")
        
    def _main_loop(self, queue, results_interval, serving_session_id, strategy):
        while strategy.is_running:
            time.sleep(results_interval)            
            self._maybe_handle_messages(queue, serving_session_id, strategy)
            self._write_results(serving_session_id, strategy)
            yield

    def _write_results(self, serving_session_id, strategy):
        results = {
            'url': strategy.get_url(),
            'path': strategy.get_path(),
            'last_update': datetime.now().timestamp()  # Current unix time
        }
        self._results_access.store(serving_session_id, results)

    def _maybe_handle_messages(self, queue, serving_session_id, strategy):
        def is_stop_event(event, payload):
            return (
                event == 'serving-stop' and
                payload['serving_session_id'] == serving_session_id
            )
        
        try:        
            for message in iter(queue.get_nowait, None):
                event = message['event']
                payload = message.get('payload', {})

                if is_stop_event(event, payload):
                    strategy.stop()
        
        except Empty:
            pass
            
