import json
import logging
import numpy as np

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt

import pkg_resources

from perceptilabs.createDataObject import createDataObject, subsample
from perceptilabs.testcore.strategies.factory import TestStrategyFactory
from perceptilabs.utils import KernelError
import perceptilabs.utils as utils


logger = logging.getLogger(__name__)


class TestCore:
    def __init__(
        self,
        testing_session_id,
        model_contexts,
        tests,
        on_testing_completed=None,
        explainer_factory=None,
    ):
        self._on_testing_completed = on_testing_completed
        self._testing_session_id = testing_session_id
        self._status = None
        self.set_status("Initializing")
        self._tests = tests
        self._explainer_factory = explainer_factory

        self._model_contexts = model_contexts
        self._inference_models = {}
        self._results = {}
        self._stopped = False
        self._model_number = 0
        self._test_number = 0

        self._test_strategy_factory = TestStrategyFactory()

    def get_data_iterator(self, model_id):
        return self._model_contexts[model_id]["dataset"]

    def _get_dataset_size(self, model_id):
        return self._model_contexts[model_id]["dataset_size"]

    def _get_output_datatypes(self, model_id):
        return list(self._model_contexts[model_id]["target_datatypes"].values())

    def _get_input_datatypes(self, model_id):
        return list(self._model_contexts[model_id]["input_datatypes"].values())

    @property
    def session_id(self):
        return self._testing_session_id

    @property
    def tests(self):
        return self._tests.copy()

    def load_models_and_data(self, call_context):
        """
        loads the pretrained models and the data loaders for the testing to begin.
        """
        for model_id in self._model_contexts:
            model_info = self._model_contexts[model_id]
            self._current_model_name = model_info["model_name"]

            self.load_model(
                call_context,
                model_id,
                training_session_id=model_info["training_session_id"],
                training_model=self._model_contexts[model_id]["training_model"],
            )

    def load_model(self, call_context, model_id, training_session_id, training_model):
        """
        loads model from exported model.pb file or using checkpoints.
        """

        try:
            self._inference_models[
                model_id
            ] = self._test_strategy_factory.make_model_strategy(
                self._tests, training_model
            )
            logger.info("model %s loaded successfully.", model_id)
        except Exception as e:
            raise KernelError.from_exception(
                e,
                message=f"Unable to load the {self._current_model_name} using checkpoint from training session {training_session_id}",
            )

    def load_data(self, data_loader, model_id):
        """
        Loads data using DataLoader.
        """
        self._data_loaders[model_id] = data_loader
        self._dataspecs[model_id] = self._get_input_and_output_feature(data_loader)
        self._dataset_sizes[model_id] = data_loader.get_dataset_size("test")

    def run(self, call_context):
        """
        Runs the list of tests for all models in the testcore and saves the results.
        """
        for _ in self.run_stepwise(call_context):
            pass

    def run_stepwise(self, call_context):
        self.set_status("Loading")
        yield

        self.load_models_and_data(call_context)
        self._model_number = 0

        for model_id in self._inference_models:
            self._current_model_id = model_id
            self._current_model_name = self._model_contexts[model_id]["model_name"]
            self._current_dataset_size = self._get_dataset_size(model_id)
            self._model_number += 1

            logger.info(
                f"Preparing model {model_id} with dataset size {self._current_dataset_size}"
            )

            compatible_layers = self.get_compatible_layers_for_tests()
            # all the results are being collected at once to not repeat the same computations for every test.
            yield from self._compute_model_outputs()

            model_inputs = self._inference_models[model_id].model_inputs
            model_outputs = self._inference_models[model_id].model_outputs

            self._results[model_id] = {}
            self._test_number = 0
            yield from self._run_tests(
                model_id, compatible_layers, model_outputs, model_inputs
            )
        if not self._stopped:
            self.set_status("Completed")

    def _run_tests(self, model_id, compatible_layers, model_outputs, model_inputs=None):
        "runs all the tests for a given model information."
        for test in self._tests:
            if not self._stopped:
                logger.info("Starting test %s for model %s.", test, model_id)
                self.set_status("Testing")
                self._test_number += 1

                self._results[model_id][test] = self._run_test(
                    test, compatible_layers[test], model_outputs, model_inputs
                )
                yield

    def _run_test(
        self, test, compatible_output_layers, model_outputs, model_inputs=None
    ):
        "runs the given test for a given model information."
        model_id = self._current_model_id
        if not self._stopped:
            if len(compatible_output_layers):
                training_model = self._model_contexts[model_id]["training_model"]
                data_iterator = self.get_data_iterator(model_id)
                model_categories = self._model_contexts[model_id]["categories"]

                strategy = self._test_strategy_factory.make_test_strategy(
                    test,
                    model_id,
                    training_model,
                    model_inputs,
                    model_outputs,
                    data_iterator,
                    model_categories,
                    compatible_output_layers,
                    self._explainer_factory,
                )
                results = strategy.run()

                logger.info("test %s completed for model %s.", test, model_id)

                if self._on_testing_completed and not self._stopped:
                    self._on_testing_completed(model_id, test)

                return results

            else:
                raise KernelError(
                    f"{test} test is not supported yet by {self._current_model_name} model."
                )

    def _compute_model_outputs(self):
        model_id = self._current_model_id
        data_iterator = self.get_data_iterator(model_id)

        logger.info("Generating outputs for model %s.", model_id)
        self.set_status("Inference")

        try:
            inference_model = self._inference_models[model_id]
            yield from inference_model.run_inference_stepwise(data_iterator)

            # TODO(mukund): support inner layer outputs
            if not self._stopped:
                logger.info("Outputs generated for model %s.", model_id)

        except Exception as e:
            raise KernelError.from_exception(
                e,
                message=f"Error while running inference on {self._current_model_name} model.",
            )

    def get_compatible_layers_for_tests(self):
        compatible_layers = {}
        for test in self._tests:
            if not self._stopped:
                compatible_layers[test] = self.get_compatible_output_layers(test)
        return compatible_layers

    def get_compatible_output_layers(self, test, model_id=None):
        """
        checks the compatibility of the given test with the model. The rules to check the compatibility
        are listed in tests.json file.
        Returns:
            dict: dict of compatible output layers and thier datatypes.
        """
        if model_id is None:
            model_id = self._current_model_id
        compatible_dict = {}

        file = pkg_resources.resource_filename("perceptilabs", "testcore/tests.json")
        with open(file) as f:
            compatibility_table = json.load(f)
        try:
            required_layer_info = compatibility_table[test]
        except:
            raise KernelError(f"The test {test} is not yet supported.")

        # TODO(mukund): add support for checking encoders and decoders properly.

        if self._model_has_accepted_inputs(model_id, required_layer_info["Input"]):
            return self._get_compatible_output_layers(
                model_id, required_layer_info["Target"]
            )
        else:
            return {}

    def _model_has_accepted_inputs(self, model_id, accepted_datatypes):
        for datatype in self._get_input_datatypes(model_id):
            if datatype in accepted_datatypes:
                return True
        return False

    def _get_compatible_output_layers(self, model_id, accepted_datatypes):
        used_datatypes = self._get_output_datatypes(model_id)
        common_list = list(set(accepted_datatypes) & set(used_datatypes))

        compatible_dict = {}
        for layer_id, datatype in self._model_contexts[model_id][
            "target_datatypes"
        ].items():
            if datatype in common_list:
                compatible_dict[layer_id] = datatype

        return compatible_dict

    def set_status(self, status):
        if self._status != "Stopped":
            self._status = status

    def stop(self):
        "sets some class variables to True so that testing will be stopped."
        self._stopped = True
        self.set_status("Stopped")
        for model_id in self._inference_models:
            self._inference_models[model_id].stop()
        return "Testing stopped."

    @property
    def num_models(self):
        "Total number of models in the current test request."
        return len(self._inference_models)

    @property
    def num_tests(self):
        "Total number of tests in the current test request."
        return len(self._tests)

    @property
    def num_samples_inferred(self):
        "number of samples inferred in the current model being tested."
        return self._inference_models[self._current_model_id].num_samples_inferred

    def get_testcore_status(self):
        """
        get_status computes the progress of the testcore.
        Returns:
            [dict]: returns the status in 3 key value pairs.
            'status': state of the testcore
            'update_line_1': progress of the model
            'update_line_2': progress of the test/inference
        """
        if self._status == "Loading":
            test_status = {
                "status": self._status,
                "update_line_1": "Loading models.",
                "update_line_2": "",
            }
        elif self._status == "Inference":
            test_status = {
                "status": self._status,
                "update_line_1": "Testing {} out of {} models.".format(
                    self._model_number, self.num_models
                ),
                "update_line_2": "Running inference on sample {}/{}".format(
                    self.num_samples_inferred, self._current_dataset_size
                ),
            }
        elif self._status == "Testing":
            test_status = {
                "status": self._status,
                "update_line_1": "Testing {} out of {} models.".format(
                    self._model_number, self.num_models
                ),
                "update_line_2": "Generating test {}/{}".format(
                    self._test_number, self.num_tests
                ),
            }
        elif self._status == "Completed":
            test_status = {
                "status": self._status,
                "update_line_1": "Testing completed.",
                "update_line_2": "",
            }
        elif self._status == "Stopped":
            test_status = {
                "status": self._status,
                "update_line_1": "",
                "update_line_2": "",
            }
        else:
            test_status = {
                "status": self._status,
                "update_line_1": "Starting tests.",
                "update_line_2": "",
            }
        return test_status

    def get_results(self):
        "retrieves results for the current test request"
        if self._status == "Completed":
            processed_results = self._process_results(self._results)
            return processed_results
        else:
            return {}

    def _process_results(self, unprocessed_results):
        results = {}

        for test in self._tests:
            results[test] = {}
            for model_id in unprocessed_results:

                strategy = self._test_strategy_factory.make_results_strategy(
                    test, unprocessed_results[model_id][test]
                )
                processed_output = strategy.run()
                results[test][model_id] = processed_output

        return results

    def _get_categories(self, model_id, compatible_layers):
        all_categories = self._model_contexts[model_id]["categories"]

        categories = {
            layer_id: all_categories.get(layer_id)
            for layer_id in compatible_layers.keys()
        }
        return categories

    @property
    def models(self):
        return self._inference_models.copy()
