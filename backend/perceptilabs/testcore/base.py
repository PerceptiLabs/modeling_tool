import json
import logging
from typing import Any, Dict, Generator, List, overload

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
    def __init__(self, receivers, issue_handler):
        self._issue_handler = issue_handler
        self._receivers = receivers
        self._models = {}

    def load_model(self, receiver_id, model_path, graph_spec):
        """
        loads model from exported model.pb file or using checkpoints.
        """
        try:
            self._models[receiver_id] = LoadInferenceModel.from_checkpoint(model_path, graph_spec)
            logger.info("model %s loaded successfully.", receiver_id)
        except Exception as e:
            with self._issue_handler.create_issue('Error while loading model', e) as issue:
                logger.info(issue.internal_message)
                raise Exception(issue.frontend_message)

    def load_data(self, graph_spec, dataset_path, method):
        if method == 'graph_spec':
            self._load_data_from_graphspec(graph_spec, dataset_path)

    def _load_data_from_graphspec(self, graph_spec, dataset_path):
        """
        Loads data using DataLoader from graph spec.
        """
        partitions = {
            'training': 0.7, 
            'validation': 0.2, 
            'test': 0.1,
        }
        self._data_loader = DataLoader.from_graph_spec(graph_spec, partitions)
        self._dataspecs = self._get_input_and_output_feature(self._data_loader)

    def run_tests(self, tests, user_email=None):
        """
        Runs the list of tests for all models in the testcore.

        Args:
            user_email: the email of the user. Optional.
        Returns:
            A dictionary containing results of all the tests of all models
        """
        results = {}
        for model_id in self._models:
            compatible_layers = {}
            for test in tests:
                compatible_layers[test] = self.get_compatible_output_layers(test, model_id)
            # all the results are being collected at once to not repeat the same computations for every test. 
            data_iterator = self._get_data_generator()

            logger.info("Generating outputs for model %s.",  model_id)
            model_outputs = self._models[model_id].run_inference(data_iterator) #TODO(mukund): support inner layer outputs 
            logger.info("Outputs generated for model %s.", model_id)
            results[model_id] = {}
            for test in tests:
                logger.info("Starting test %s for model %s.",
                            test, model_id)
                results[model_id][test] = self._run_test(test, model_outputs, compatible_layers[test], model_id, user_email)
        return results

    def _run_test(self, test, model_outputs, compatible_output_layers, model_id, user_email): 
        if len(compatible_output_layers):
            if test == 'confusion_matrix':
                results = ConfusionMatrix().run(model_outputs, compatible_output_layers)
            elif test == 'metrics_table':
                results = MetricsTable().run(model_outputs, compatible_output_layers)
            logger.info("test %s completed for model %s.", test, model_id)

            if user_email:
                tracking.send_testing_completed(user_email, model_id, test)            
            
            return results
        else: 
            raise Exception("%s is not supported yet by the model %s.", test, model_id)
        
        
    def get_compatible_output_layers(self, test, receiver_id):
        """
        checks the compatibility of the given test with the model. The rules to check the compatibility
        are listed in tests.json file.
        Returns:
            list: list of compatible output layers 
        """
        compatible_list = []
        file = pkg_resources.resource_filename('perceptilabs', 'testcore/tests.json')
        with open(file) as f:
            compatibility_table = json.load(f)
        try:
            required_layer_info = compatibility_table[test]
        except:
            raise Exception(f'The test {test} is not yet supported.')

        #TODO(mukund): add support for checking encoders and decoders properly.
        for layer_type in required_layer_info:
            accepted_datatypes = required_layer_info[layer_type]
            used_datatypes = [
                self._dataspecs[layer].datatype for layer in self._dataspecs
                if self._dataspecs[layer].iotype == layer_type.lower()
            ]
            common_list = list(set(accepted_datatypes) & set(used_datatypes))
            if not accepted_datatypes:
                continue
            elif not common_list:
                return []
            if layer_type == 'Output':
                compatible_list = [
                    layer for layer in self._dataspecs 
                    if self._layer_has_compatible_output_datatype(layer, common_list)
                ]
        return compatible_list

    def _layer_has_compatible_output_datatype(self, layer, common_list):
        if self._dataspecs[layer].iotype == 'output':
            if self._dataspecs[layer].datatype in common_list:
                return True
        
    def _get_data_generator(self):
        dataset_test_generator = self._data_loader.get_dataset(partition='test').batch(1) 
        #TODO(mukund): test with different batch sizes possibly dynamic based on given tests for better performance. 
        return dataset_test_generator

    def _get_input_and_output_feature(self, data_loader):
        specs = data_loader._feature_specs
        return specs

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
            data_object = createDataObject(data_list=[result], type_list = ['heatmap'])
            self._results[layer_name] = data_object
        return self._results

    def _process_metrics_table_output(self):
        return self._results
