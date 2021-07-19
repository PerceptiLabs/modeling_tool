import json
import logging
from typing import Any, Dict, Generator, List, overload
import time

import pkg_resources

from perceptilabs.createDataObject import createDataObject
from perceptilabs.data.base import DataLoader, FeatureSpec
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER
from perceptilabs.testcore.strategies.modelstrategies import LoadInferenceModel
from perceptilabs.testcore.strategies.teststrategies import ConfusionMatrix, MetricsTable
import perceptilabs.tracking as tracking

logger = logging.getLogger(APPLICATION_LOGGER)
user_logger = logging.getLogger(USER_LOGGER)


class TestCore():
    def __init__(self, model_ids, models_info, tests, issue_handler, user_email=None):
        self._issue_handler = issue_handler
        self._model_ids = model_ids
        self._models_info = models_info
        self._tests = tests
        self._user_email = user_email

        self._models = {}
        self._results = {}
        self._stopped = False
        self._status = None
        self._data_loaders = {}
        self._dataspecs = {}
        self._dataset_sizes = {}
        self._model_number = 0
        self._test_number = 0
        self.set_status('Initializing')

    def load_models_and_data(self):
        """
        loads the pretrained models and the data loaders for the testing to begin.
        """
        for model_id in self._models_info:
            model_info = self._models_info[model_id]
            self.load_data(model_info['data_loader'], model_id)
            self.load_model(
                model_id, checkpoint_directory=model_info['checkpoint_directory'], graph_spec=model_info['graph_spec']
            )

    def load_model(self, model_id, checkpoint_directory, graph_spec):
        """
        loads model from exported model.pb file or using checkpoints.
        """
        try:
            self._models[model_id] = LoadInferenceModel.from_checkpoint(
                checkpoint_directory, graph_spec, self._data_loaders[model_id])
            logger.info("model %s loaded successfully.", model_id)
        except Exception as e:
            self._found_error(
                f"Unable to load the {self._current_model_name} using checkpoint from {checkpoint_directory}")
            with self._issue_handler.create_issue('Error while loading model', e) as issue:
                raise Exception(issue.frontend_message)

    def load_data(self, data_loader, model_id):
        """
        Loads data using DataLoader.
        """
        self._data_loaders[model_id] = data_loader
        self._dataspecs[model_id] = self._get_input_and_output_feature(
            data_loader)
        self._dataset_sizes[model_id] = data_loader.get_dataset_size('test')

    def run(self):
        """
        Runs the list of tests for all models in the testcore and saves the results.
        """
        self.set_status('Loading')
        self.load_models_and_data()
        self._model_number = 0
        for model_id in self._models:
            self._current_model_id = model_id
            self._current_model_name = self._models_info[model_id]['model_name']
            self._current_dataset_size = self._dataset_sizes[model_id]
            self._model_number += 1
            compatible_layers = self.get_compatible_layers_for_tests()
            # all the results are being collected at once to not repeat the same computations for every test.
            model_outputs = self._get_model_outputs()
            self._results[model_id] = {}
            self._test_number = 0
            self._run_tests(model_id, model_outputs, compatible_layers)
        if not self._stopped:
            self.set_status('Completed')

    def _run_tests(self, model_id, model_outputs, compatible_layers):
        "runs all the tests for a given model information."
        for test in self._tests:
            if not self._stopped:
                logger.info("Starting test %s for model %s.", test, model_id)
                self.set_status('Testing')
                self._test_number += 1
                self._results[model_id][test] = self._run_test(
                    test, model_outputs, compatible_layers[test])
        
    def _run_test(self, test, model_outputs, compatible_output_layers):
        "runs the given test for a given model information."
        model_id = self._current_model_id
        if not self._stopped:
            if len(compatible_output_layers):
                if test == 'confusion_matrix':
                    results = ConfusionMatrix().run(model_outputs, compatible_output_layers)
                elif test == 'metrics_table':
                    results = MetricsTable().run(model_outputs, compatible_output_layers)
                logger.info("test %s completed for model %s.", test, model_id)
                if self._user_email and not self._stopped:
                    tracking.send_testing_completed(
                        self._user_email, model_id, test)
                return results
            else:
                self._found_error(
                    f"{test} test is not supported yet by {self._current_model_name} model.")
                raise Exception(
                    f"{test} test is not supported yet by {self._current_model_name} model.")

    def _get_model_outputs(self):
        model_id = self._current_model_id
        data_iterator = self._get_data_generator(model_id)
        logger.info("Generating outputs for model %s.",  model_id)
        self.set_status('Inference')
        try:
            model_outputs = self._models[model_id].run_inference(data_iterator)
            # TODO(mukund): support inner layer outputs
            if not self._stopped:
                logger.info("Outputs generated for model %s.", model_id)
                return model_outputs
        except Exception as e:
            self._found_error(
                f"Error while running inference on {self._current_model_name} model.")
            with self._issue_handler.create_issue('Error while loading model', e) as issue:
                raise Exception(issue.frontend_message)

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
            list: list of compatible output layers
        """
        if model_id is None:
            model_id = self._current_model_id
        compatible_list = []
        data_specs = self._dataspecs[model_id]
        file = pkg_resources.resource_filename(
            'perceptilabs', 'testcore/tests.json')
        with open(file) as f:
            compatibility_table = json.load(f)
        try:
            required_layer_info = compatibility_table[test]
        except:
            self._found_error(f"The test {test} is not yet supported.")
            raise Exception(f'The test {test} is not yet supported.')

        # TODO(mukund): add support for checking encoders and decoders properly.
        for layer_type in required_layer_info:
            accepted_datatypes = required_layer_info[layer_type]
            used_datatypes = [
                data_specs[layer].datatype for layer in data_specs
                if data_specs[layer].iotype == layer_type.lower()
            ]
            common_list = list(set(accepted_datatypes)
                                & set(used_datatypes))
            if not accepted_datatypes:
                continue
            elif not common_list:
                return []
            if layer_type == 'Target':
                compatible_list = [
                    layer for layer in data_specs
                    if self._layer_has_compatible_output_datatype(layer, common_list, model_id)
                ]
        return compatible_list

    def _layer_has_compatible_output_datatype(self, layer, common_list, model_id):
        if self._dataspecs[model_id][layer].iotype == 'target':
            if self._dataspecs[model_id][layer].datatype in common_list:
                return True

    def _get_data_generator(self, model_id):
        dataset_test_generator = self._data_loaders[model_id].get_dataset(
            partition='test').batch(1)
        # TODO(mukund): test with different batch sizes possibly dynamic based on given tests for better performance.
        return dataset_test_generator

    def _get_input_and_output_feature(self, data_loader):
        specs = data_loader.feature_specs
        return specs

    def set_status(self, status):
        if self._status != 'Stopped':
            self._status = status

    def stop(self):
        'sets some class variables to True so that testing will be stopped.'
        self._stopped = True
        self.set_status('Stopped')
        for model_id in self._models:
            self._models[model_id].stop()
        return 'Testing stopped.'
    
    def _found_error(self, message=''):
        self.set_status('Error')
        self._error_message = message

    @property
    def num_models(self):
        'Total number of models in the current test request.'
        return len(self._models)

    @property
    def num_tests(self):
        'Total number of tests in the current test request.'
        return len(self._tests)

    @property
    def num_samples_inferred(self):
        'number of samples inferred in the current model being tested.'
        return self._models[self._current_model_id].num_samples_inferred

    def get_testcore_status(self):
        """
        get_status computes the progress of the testcore.
        Returns:
            [dict]: returns the status in 3 key value pairs.
            'status': state of the testcore
            'update_line_1': progress of the model
            'update_line_2': progress of the test/inference
        """
        if self._status == 'Loading':
            test_status = {
                'status': self._status,
                'update_line_1': "Loading models.",
                'update_line_2': ""
            }
        elif self._status == 'Inference':
            test_status = {
                'status': self._status,
                'update_line_1': "Testing {} out of {} models.".format(self._model_number, self.num_models),
                'update_line_2': "Running inference on sample {}/{}".format(self.num_samples_inferred, self._current_dataset_size)
            }
        elif self._status == 'Testing':
            test_status = {
                'status': self._status,
                'update_line_1': "Testing {} out of {} models.".format(self._model_number, self.num_models),
                'update_line_2': "Generating test {}/{}".format(self._test_number, self.num_tests)
            }
        elif self._status == 'Completed':
            test_status = {
                'status': self._status,
                'update_line_1': "Testing completed.",
                'update_line_2': ""
            }
        elif self._status == 'Stopped':
            test_status = {
                'status': self._status,
                'update_line_1': "",
                'update_line_2': ""
            }
        elif self._status == 'Error':
            test_status = {
            'status': self._status,
            'update_line_1': self._error_message,
            'update_line_2': ""
        }
        else:
            test_status = {
                'status': self._status,
                'update_line_1': "Starting tests.",
                'update_line_2': ""
            }
        return test_status

    def get_results(self):
        'retrieves results for the current test request'
        if self._status == 'Completed':
            return self._results
        else:
            return {}

class ProcessResults():
    """process results here.
    """

    def __init__(self, results, test):
        self._results = results
        self._test = test

    def run(self):
        if self._test == 'confusion_matrix':
            return self._process_confusionmatrix_output()
        elif self._test == 'metrics_table':
            return self._process_metrics_table_output()
        else:
            raise Exception(f"{self._test} is not supported yet.")

    def _process_confusionmatrix_output(self):
        for layer_name in self._results:
            result = self._results[layer_name].numpy()
            data_object = createDataObject(
                data_list=[result], type_list=['heatmap'])
            self._results[layer_name] = data_object
        return self._results

    def _process_metrics_table_output(self):
        return self._results
