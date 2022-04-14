import json
import logging
import numpy as np

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt

import pkg_resources

from perceptilabs.createDataObject import createDataObject, subsample
from perceptilabs.testcore.strategies.modelstrategies import LoadInferenceModel
from perceptilabs.testcore.strategies.teststrategies import (
    ConfusionMatrix,
    MetricsTable,
    OutputVisualization,
    ShapValues,
)
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

        def should_return_inputs():
            return "outputs_visualization" in self._tests

        def should_return_outputs():
            if "confusion_matrix" in self._tests:
                return True

            if "classification_metrics" in self._tests:
                return True

            if "segmentation_metrics" in self._tests:
                return True

            if "outputs_visualization" in self._tests:
                return True

            return False

        try:
            self._inference_models[model_id] = LoadInferenceModel(
                training_model,
                return_inputs=should_return_inputs(),
                return_outputs=should_return_outputs(),
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
                if test == "confusion_matrix":
                    categories = self._get_categories(
                        model_id, compatible_output_layers
                    )
                    results = ConfusionMatrix().run(
                        model_outputs, compatible_output_layers, categories
                    )
                elif test == "segmentation_metrics":
                    results = MetricsTable().run(
                        model_outputs, compatible_output_layers
                    )
                elif test == "classification_metrics":
                    results = MetricsTable().run(
                        model_outputs, compatible_output_layers
                    )
                elif test == "outputs_visualization":
                    results = OutputVisualization().run(
                        model_inputs, model_outputs, compatible_output_layers
                    )
                elif test == "shap_values":
                    model = self._model_contexts[model_id]["training_model"]
                    data_iterator = self.get_data_iterator(model_id)

                    results = ShapValues(
                        data_iterator, model, explainer_factory=self._explainer_factory
                    ).run()
                else:
                    raise ValueError(f"Undefined test '{test}'")

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
                processed_output = ProcessResults(
                    unprocessed_results[model_id][test], test
                ).run()
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


class ProcessResults:
    """process results here."""

    def __init__(self, results, test):
        self._results = results
        self._test = test

    def run(self):
        if self._test == "confusion_matrix":
            return self._process_confusionmatrix_output()
        elif self._test in ["segmentation_metrics", "classification_metrics"]:
            return self._process_metrics_table_output()
        elif self._test == "outputs_visualization":
            return self._process_outputs_visualization_output()
        elif self._test == "shap_values":
            return self._process_shapvalue_output()
        else:
            raise KernelError(f"{self._test} is not supported yet.")

    def _process_shapvalue_output(self):
        import os
        import shap
        from pathlib import Path

        shap_values = self._results["shap_values"]
        test_samples = self._results["test_samples"]
        shap.image_plot(shap_values, test_samples)

        fig = plt.gcf()
        fig.canvas.draw()

        data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        default_path = Path.home() / "shap_plot.png"
        path = os.getenv("PL_SHAP_PATH", str(default_path))
        try:
            fig.savefig(path)
        except:
            logger.exception(f"Failed writing shap plot to {path}")
        else:
            logger.exception(f"Wrote shap plot to {path}")

        data_object = createDataObject(data_list=[image], normalize=False)
        self._results = {"image": data_object}
        return self._results

    def _process_confusionmatrix_output(self):
        for layer_name in self._results:
            result = self._results[layer_name]["data"].numpy()
            categories = self._results[layer_name]["categories"]

            # normalize the matrix and purge nans
            result = np.nan_to_num(result)
            result = np.around(result, 3)

            show_data = True if len(categories) < 14 else False
            data_object = createDataObject(
                data_list=[result],
                type_list=["heatmap"],
                name_list=categories,
                show_data=show_data,
            )
            self._results[layer_name] = data_object
        return self._results

    def _process_metrics_table_output(self):
        return self._results

    def _process_outputs_visualization_output(self):
        """
        input, target, prediction, heatmap will be concatenated into a single image for each sample.
        Returns:
            conv layer like output from workspace
        """
        for layer_name in self._results:
            result = self._results[layer_name]
            inputs = result["inputs"]
            targets = result["targets"]
            predictions = result["predictions"]
            losses = result["losses"]
            # getting segmentations and generating concatenated images
            images = []

            # subsampling
            MAX_SIZE = 200
            image_largest_axis = np.max(inputs[0].shape)
            subsample_ratio = max(image_largest_axis / MAX_SIZE, 1)
            # inspired from https://github.com/yingkaisha/keras-unet-collection/blob/main/examples/human-seg_atten-unet-backbone_coco.ipynb
            for i in range(len(inputs)):
                predicted_segmentation = np.argmax(predictions[i], axis=3)
                target_segmentation = np.argmax(targets[i], axis=3)

                fig, axs = plt.subplots(2, 2, tight_layout=True, figsize=(3, 3))
                fig.suptitle("Loss: " + str(losses[i]), fontsize=8, color="white")

                axs[0, 0].pcolormesh(
                    subsample(np.squeeze(np.mean(inputs[i], axis=-1)), subsample_ratio)[
                        1
                    ],
                    cmap=plt.get_cmap("gray"),
                )
                axs[0, 0].axis("off")
                axs[0, 0].set_title(
                    "Input", {"fontname": "Roboto"}, fontsize=7, color="white"
                )
                axs[0, 0].invert_yaxis()

                axs[1, 1].pcolormesh(
                    subsample(
                        np.squeeze(predicted_segmentation, axis=0), subsample_ratio
                    )[1],
                    cmap=plt.get_cmap("jet"),
                )
                axs[1, 1].axis("off")
                axs[1, 1].set_title(
                    "Prediction", {"fontname": "Roboto"}, fontsize=7, color="white"
                )
                axs[1, 1].invert_yaxis()

                axs[0, 1].pcolormesh(
                    subsample(np.squeeze(target_segmentation), subsample_ratio)[1],
                    cmap=plt.get_cmap("jet"),
                )
                axs[0, 1].axis("off")
                axs[0, 1].set_title(
                    "Target", {"fontname": "Roboto"}, fontsize=7, color="white"
                )
                axs[0, 1].invert_yaxis()

                axs[1, 0].pcolormesh(
                    subsample(np.squeeze(np.mean(inputs[i], axis=-1)), subsample_ratio)[
                        1
                    ],
                    cmap=plt.get_cmap("gray"),
                )
                axs[1, 0].pcolormesh(
                    subsample(np.mean(predicted_segmentation, axis=0), subsample_ratio)[
                        1
                    ],
                    cmap=plt.get_cmap("jet"),
                    alpha=0.2,
                )
                axs[1, 0].axis("off")
                axs[1, 0].set_title(
                    "Prediction on Input",
                    {"fontname": "Roboto"},
                    fontsize=7,
                    color="white",
                )
                axs[1, 0].invert_yaxis()

                rect = fig.patch
                rect.set_facecolor("#23252A")
                fig.canvas.draw()

                data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
                image = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
                images.append(image)

            # create data object
            data_object = createDataObject(data_list=images, normalize=True)
            self._results[layer_name] = data_object
        return self._results
