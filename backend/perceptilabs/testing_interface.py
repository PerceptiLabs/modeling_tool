import time
import logging
from queue import Empty
import os

import perceptilabs.utils as utils
from perceptilabs.testcore import TestCore
from perceptilabs.utils import KernelError
import perceptilabs.tracking as tracking
from perceptilabs.data.resolvers import DataFrameResolver

logger = logging.getLogger(__name__)


class TestingSessionInterface:
    """Main Class that does all the computations for the tests and returns the results"""

    def __init__(
        self,
        message_broker,
        event_tracker,
        dataset_access,
        model_access,
        epochs_access,
        results_access,
        tensorflow_support_access,
        preprocessing_results_access,
        explainer_factory=None,
    ):
        self._dataset_access = dataset_access
        self._preprocessing_results_access = preprocessing_results_access
        self._event_tracker = event_tracker
        self._message_broker = message_broker
        self._model_access = model_access
        self._epochs_access = epochs_access
        self._results_access = results_access
        self._tensorflow_support_access = tensorflow_support_access
        self._explainer_factory = explainer_factory

    def run(self, call_context, *args, **kwargs):
        for _ in self.run_stepwise(call_context, *args, **kwargs):
            pass

    def run_stepwise(
        self,
        call_context,
        testing_session_id,
        models,
        tests,
        results_interval=None,
        logrocket_url="",
    ):
        self._tensorflow_support_access.set_tf_dependencies(call_context)

        call_context = call_context.push(
            testing_session_id=testing_session_id,
            logrocket_url=logrocket_url,
        )

        try:
            test_core = self._setup_test_core(
                call_context, testing_session_id, models, tests
            )

            with self._message_broker.subscription() as queue:
                yield from self._main_loop(
                    call_context, queue, test_core, results_interval, testing_session_id
                )

        except Exception as e:
            error = KernelError.from_exception(e, "Error during testing!")
            self._results_access.store(testing_session_id, {"error": error.to_dict()})
            logger.exception("Exception in testing session interface!")
            utils.send_ex_to_sentry(e, call_context)

    def _main_loop(
        self, call_context, queue, core, results_interval, testing_session_id
    ):
        testing_step = core.run_stepwise(call_context)
        testing_sentinel = object()

        last_update = -1
        is_running = True

        while is_running:
            self._maybe_handle_messages(queue, core)

            testing_step_result = next(testing_step, testing_sentinel)
            is_running = testing_step_result is not testing_sentinel

            last_update = self._maybe_write_results(
                results_interval, last_update, core, testing_session_id, is_running
            )

            yield

    def _prepare_model_context(self, call_context, model_id, model_info):
        dataset_settings = self._dataset_access.parse_settings(
            model_info["datasetSettings"]
        )

        data_metadata = self._preprocessing_results_access.get_metadata(
            dataset_settings.compute_hash()
        )

        df = self._dataset_access.get_dataframe(
            call_context,
            dataset_settings.dataset_id,
            fix_paths_for=dataset_settings.file_based_features,
        )

        df = DataFrameResolver.resolve_dataframe(df, model_info["datasetSettings"])

        data_loader = self._dataset_access.get_data_loader(
            df,
            dataset_settings,
            data_metadata,
            num_repeats=dataset_settings.num_recommended_repeats,
        )

        if "graphSettings" not in model_info:
            logger.warning(
                f"No default graph settings provided in request for model {model_id}"
            )

        graph_spec = self._model_access.get_graph_spec(
            call_context, model_id, default_settings=model_info.get("graphSettings")
        )

        epoch_id = self._epochs_access.get_latest(
            call_context,
            training_session_id=model_info["training_session_id"],
            require_checkpoint=True,
            require_trainer_state=False,
        )

        checkpoint_path = self._epochs_access.get_checkpoint_path(
            call_context,
            training_session_id=model_info["training_session_id"],
            epoch_id=epoch_id,
        )

        training_model = self._model_access.get_training_model(
            call_context,
            model_id,
            default_graph_settings=graph_spec.to_dict(),
            checkpoint_path=checkpoint_path,
        )

        model_context = {
            "training_model": training_model,
            "model_name": model_info["model_name"],
            "training_session_id": model_info["training_session_id"],
            "dataset": data_loader.get_dataset(partition="test"),
            "dataset_size": data_loader.get_dataset_size(partition="test"),
            "categories": data_loader.get_categories(),
            "input_datatypes": data_loader.get_datatypes("input"),
            "target_datatypes": data_loader.get_datatypes("target"),
        }
        return model_context

    def _setup_test_core(self, call_context, testing_session_id, models_info, tests):
        def on_testing_completed(model_id, test):
            tracking.send_testing_completed(
                self._event_tracker, call_context, model_id, test
            )

        model_contexts = {
            model_id: self._prepare_model_context(call_context, model_id, model_info)
            for model_id, model_info in models_info.items()
        }

        core = TestCore(
            testing_session_id,
            model_contexts,
            tests,
            on_testing_completed=on_testing_completed,
            explainer_factory=self._explainer_factory,
        )
        return core

    def _maybe_write_results(
        self, results_interval, last_update, core, testing_session_id, is_running
    ):
        time_since_update = time.time() - last_update
        if (
            (results_interval is None)
            or (time_since_update >= results_interval)
            or not is_running
        ):

            self._write_results(core, testing_session_id)
            return time.time()
        else:
            return last_update

    def _write_results(self, core, testing_session_id):
        status = core.get_testcore_status()
        results = core.get_results()

        all_results = {"results": results, "status": status}
        self._results_access.store(testing_session_id, all_results)

    def _maybe_handle_messages(self, queue, core):
        try:
            for message in iter(queue.get_nowait, None):
                event = message["event"]
                payload = message.get("payload", {})

                if (
                    event == "testing-stop"
                    and payload["testing_session_id"] == core.session_id
                ):
                    core.stop()
        except Empty:
            pass
