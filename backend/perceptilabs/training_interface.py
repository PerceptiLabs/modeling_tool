import time
import logging
from queue import Empty

import sentry_sdk

from perceptilabs.trainer import Trainer
from perceptilabs.exporter.base import Exporter
from perceptilabs.utils import KernelError

logger = logging.getLogger(__name__)


class TrainingSessionInterface:
    def __init__(self, message_broker, model_access, epochs_access, results_access):
        self._message_broker = message_broker
        self._model_access = model_access
        self._epochs_access = epochs_access
        self._results_access = results_access

    def run(self, *args, **kwargs):
        for _ in self.run_stepwise(*args, **kwargs):
            pass

    def run_stepwise(self, data_loader, model_id, graph_spec_dict, training_session_id, training_settings, load_checkpoint, user_email, results_interval=None, is_retry=False, logrocket_url=''):
        try:
            self._clean_old_status(training_session_id)
        
            trainer = self._setup_trainer(
                data_loader, model_id, graph_spec_dict, training_session_id, training_settings,
                use_checkpoint=(load_checkpoint or is_retry), user_email=user_email
            )
            with self._message_broker.subscription() as queue:
                yield from self._main_loop(queue, trainer, results_interval, training_session_id)

        except Exception as e:
            self._handle_error(e, model_id, graph_spec_dict, training_session_id, training_settings, user_email, logrocket_url)

    def _handle_error(self, e, model_id, graph_spec_dict, training_session_id, training_settings, user_email, logrocket_url):
        error = KernelError.from_exception(e, message="Error during training!")
        self._results_access.store(training_session_id, {'error': error.to_dict()})
        logger.exception("Exception in training session interface!")

        with sentry_sdk.push_scope() as scope:
            scope.set_extra('model_id', model_id)
            scope.set_extra('graph_spec', graph_spec_dict)
            scope.set_extra('training_session_id', training_session_id)
            scope.set_extra('training_settings', training_settings)
            scope.set_extra('user_email', user_email)
            scope.set_extra('logrocket_url', logrocket_url)            
            
            sentry_sdk.capture_exception(e)
            sentry_sdk.flush()            

    def _main_loop(self, queue, trainer, results_interval, training_session_id):
        training_step = trainer.run_stepwise()
        training_sentinel = object()        

        last_update = -1
        is_running = True

        while is_running:
            self._maybe_handle_messages(queue, trainer)

            training_step_result = next(training_step, training_sentinel)
            is_running = training_step_result is not training_sentinel
                
            last_update = self._maybe_write_results(
                results_interval, last_update, trainer, training_session_id, is_running)

            yield            

    def _setup_trainer(self, data_loader, model_id, graph_spec_dict, training_session_id, training_settings, use_checkpoint, user_email):
        graph_spec = self._model_access.get_graph_spec(graph_spec_dict)
        
        epoch_id = self._epochs_access.get_latest(
            training_session_id=training_session_id,
            require_checkpoint=True,
            require_trainer_state=True
        )

        initial_state = None
        checkpoint_path = None        
        if use_checkpoint:
            checkpoint_path = self._epochs_access.get_checkpoint_path(
                training_session_id=training_session_id,
                epoch_id=epoch_id
            )
            initial_state = self._epochs_access.load_state_dict(training_session_id, epoch_id)            
        training_model = self._model_access.get_training_model(
            graph_spec.to_dict(), checkpoint_path=checkpoint_path)

        exporter = Exporter(
            graph_spec, training_model, data_loader,
            model_id=model_id, user_email=user_email
        )        
        
        trainer = Trainer(
            data_loader,
            training_model,
            training_settings,
            training_session_id,
            exporter=exporter,
            model_id=model_id,
            user_email=user_email,
            initial_state=initial_state
        )
        return trainer

    
                
    def _maybe_write_results(self, results_interval, last_update, trainer, training_session_id, is_running):
        time_since_update = time.time() - last_update

        if (results_interval is None) or (time_since_update >= results_interval) or not is_running:
            results = trainer.get_results()
            self._results_access.store(training_session_id, results)            
            return time.time()
        else:
            return last_update

    def _maybe_handle_messages(self, queue, trainer):
        try:
            for message in iter(queue.get_nowait, None):
                event = message['event']
                payload = message.get('payload', {})
                self._handle_message(event, payload, trainer)
        except Empty:
            pass
        
    def _handle_message(self, event, payload, trainer):
        model_id = payload.get('model_id')
        session_id = payload.get('training_session_id')
        
        if model_id != trainer.model_id or session_id != trainer.session_id:
            return            
        
        if event == 'training-stop':
            trainer.stop()
        elif event == 'training-pause':
            trainer.pause()            
        elif event == 'training-unpause':
            trainer.unpause()
        elif event == 'training-export': 
            trainer.export(payload['export_directory'], mode=payload['mode'])
        else:
            print(f"Unknown event '{event}'")  # TODO: use logger..

    def _clean_old_status(self, training_session_id):
        self._results_access.remove(training_session_id)
