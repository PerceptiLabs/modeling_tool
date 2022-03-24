import os
import time
import logging
from queue import Empty
import os
from contextlib import contextmanager

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.trainer import Trainer
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.sharing.exporter import Exporter
from perceptilabs.utils import KernelError
from perceptilabs.trainer.utils import EpochSlowdownTracker
import perceptilabs.tracking as tracking
import perceptilabs.utils as utils

logger = logging.getLogger(__name__)


class TrainingSessionInterface:
    def __init__(self, message_broker, event_tracker, model_access, epochs_access, results_access, tensorflow_support_access, max_slowdown_rate=0.1):
        self._message_broker = message_broker
        self._event_tracker = event_tracker
        self._model_access = model_access
        self._epochs_access = epochs_access
        self._results_access = results_access
        self._tensorflow_support_access = tensorflow_support_access


        self._max_slowdown_rate = max_slowdown_rate
        self._min_epochs_for_slowdown = 5
        self._has_reported_slowdown = False
        self._slowdown_tracker = EpochSlowdownTracker()

    def run(self, call_context, *args, **kwargs):
        assert call_context.user_unique_id
        for _ in self.run_stepwise(call_context, *args, **kwargs):
            pass

    def run_stepwise(self, call_context, data_loader, model_id, training_session_id, training_settings, load_checkpoint, results_interval=None, is_retry=False, logrocket_url='', graph_settings=None):
        self._tensorflow_support_access.set_tfhub_env_var(call_context)

        call_context = call_context.push(
            model_id = model_id,
            training_session_id = training_session_id,
            training_settings = training_settings,
            dataset_settings = data_loader.settings,
            graph_settings = graph_settings,
            logrocket_url = logrocket_url,
        )

        try:
            self._clean_old_status(call_context, training_session_id)

            trainer = self._setup_trainer(
                call_context,
                data_loader,
                model_id,
                training_session_id,
                training_settings,
                use_checkpoint=(load_checkpoint or is_retry),
                graph_settings=graph_settings,
            )
            with self._message_broker.subscription() as queue:
                yield from self._main_loop(call_context, queue, trainer, results_interval, training_session_id)

        except Exception as e:
            self._handle_error(call_context, e, training_session_id)

    def _handle_error(self, call_context, e, training_session_id):
        error = KernelError.from_exception(e, message="Error during training!")
        self._results_access.store(call_context, training_session_id, {'error': error.to_dict()})
        logger.exception("Exception in training session interface!")
        utils.send_ex_to_sentry(e, call_context)

    def _main_loop(self, call_context, queue, trainer, results_interval, training_session_id):
        training_step = trainer.run_stepwise()
        training_sentinel = object()

        last_update = -1
        is_running = True

        while is_running:
            self._maybe_handle_messages(call_context, queue, trainer)

            training_step_result = next(training_step, training_sentinel)
            is_running = training_step_result is not training_sentinel

            last_update = self._maybe_write_results(
                call_context, results_interval, last_update, trainer, training_session_id, is_running)

            yield

    def _setup_trainer(self, call_context, data_loader, model_id, training_session_id, training_settings, use_checkpoint, graph_settings):

        if graph_settings:
            graph_spec = GraphSpec.from_dict(graph_settings)
        else:
            graph_spec = self._model_access.get_graph_spec(call_context, model_id)

        epoch_id = self._epochs_access.get_latest(
            call_context,
            training_session_id=training_session_id,
            require_checkpoint=True,
            require_trainer_state=True
        )

        initial_state = None
        checkpoint_path = None
        if use_checkpoint:
            checkpoint_path = self._epochs_access.get_checkpoint_path(
                call_context,
                training_session_id=training_session_id,
                epoch_id=epoch_id
            )
            initial_state = self._epochs_access.load_state_dict(call_context, training_session_id, epoch_id)


        training_model = TrainingModel.from_graph_spec(
            graph_spec, checkpoint_path=checkpoint_path)

        self._exporter = Exporter(graph_spec, training_model, data_loader)

        def on_training_started():
            tracking.send_training_started(self._event_tracker, call_context, model_id, graph_spec)

        def on_training_stopped(*args):
            tracking.send_training_stopped(self._event_tracker, call_context, model_id, graph_spec, *args)

        def on_training_completed(trainer, *args):
            if not trainer.auto_checkpoint:  # At least save the final one.
                self._save_epoch(call_context, trainer)

            tracking.send_training_completed(self._event_tracker, call_context, model_id, graph_spec, *args)

        def on_epoch_completed(epoch, trainer, epoch_time):
            if trainer.auto_checkpoint:
                self._save_epoch(call_context, trainer)

            self._check_for_slowdown(epoch, epoch_time, call_context)

        trainer = Trainer(
            data_loader,
            training_model,
            training_settings,
            training_session_id,
            model_id=model_id,
            initial_state=initial_state,
            on_training_started=on_training_started,
            on_training_completed=on_training_completed,
            on_training_stopped=on_training_stopped,
            on_epoch_completed=on_epoch_completed
        )
        return trainer


    def _maybe_write_results(self, call_context, results_interval, last_update, trainer, training_session_id, is_running):
        time_since_update = time.time() - last_update

        if (results_interval is None) or (time_since_update >= results_interval) or not is_running:
            results = trainer.get_results()
            self._results_access.store(call_context, training_session_id, results)
            return time.time()
        else:
            return last_update

    def _maybe_handle_messages(self, call_context, queue, trainer):
        try:
            for message in iter(queue.get_nowait, None):
                event = message['event']
                payload = message.get('payload', {})
                self._handle_message(call_context, event, payload, trainer)
        except Empty:
            pass

    def _handle_message(self, call_context, event, payload, trainer):
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
            self._handle_export(
                call_context,
                payload['export_directory'],
                payload['mode'],
                model_id,
            )
        else:
            logger.error(f"Unknown event '{event}'")

    def _handle_export(self, call_context, export_directory, mode, model_id):
        if mode != 'Checkpoint':
            self._exporter.export(export_directory, mode)
            tracking.send_model_exported(self._event_tracker, call_context, model_id)
        else:
            self._exporter.export_checkpoint(
                os.path.join(export_directory, 'checkpoint.ckpt'))

    def _clean_old_status(self, call_context, training_session_id):
        self._results_access.remove(call_context, training_session_id)

    def _save_epoch(self, call_context, trainer):
        if (
                trainer.num_epochs_completed == 0 and
                trainer.num_training_batches_completed_this_epoch == 0
        ):
            return  # Nothing to save...

        checkpoint_path = self._epochs_access.get_checkpoint_path(
            call_context,
            training_session_id=trainer.training_session_id,
            epoch_id=trainer.num_epochs_completed
        )
        logger.info(f"Exporting checkpoint to {checkpoint_path}")
        self._exporter.export_checkpoint(checkpoint_path)

        state_dict = trainer.save_state()
        self._epochs_access.save_state_dict(
            call_context,
            trainer.training_session_id,
            trainer.num_epochs_completed,
            state_dict
        )

    def _check_for_slowdown(self, epoch, epoch_time, call_context):
        self._slowdown_tracker.add_time(epoch_time)

        if self._slowdown_tracker.num_epochs_measured < self._min_epochs_for_slowdown:
            return

        slowdown_per_epoch = self._slowdown_tracker.get_slowdown_rate()

        if not self._has_reported_slowdown and slowdown_per_epoch > self._max_slowdown_rate:
            logger.warning(
                f"Training has slowed down by {slowdown_per_epoch}s/epoch measured across {epoch+1} epochs. Maximum slowdown rate is set to {self._max_slowdown_rate}s/epoch. "
                f"Epoch durations: {self._slowdown_tracker.times}"
            )

            call_context = call_context.push(
                epoch_number = epoch,
                epoch_durations = self._slowdown_tracker.times,
                slowdown_rate = slowdown_per_epoch,
                slowdown_rate_max = self._max_slowdown_rate,
            )

            utils.send_message_to_sentry("Training slowdown detected")

            self._has_reported_slowdown = True


