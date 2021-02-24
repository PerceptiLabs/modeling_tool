from abc import abstractmethod, ABC
import logging

import pandas as pd
import numpy as np


from perceptilabs.lwcore.utils import exception_to_error
from perceptilabs.lwcore.results import LayerResults
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.utils import graph_spec_to_core_graph
from perceptilabs.lwcore.utils import exception_to_error, format_exception
from perceptilabs.issues import UserlandError
from perceptilabs.utils import stringify

logger = logging.getLogger(APPLICATION_LOGGER)


class BaseStrategy(ABC):
    @abstractmethod
    def run(self, layer_spec, graph_spec, input_results, line_offset=None):
        raise NotImplementedError

    @staticmethod
    def get_default(code_error=None, instantiation_error=None, strategy_error=None):
        """ Alias for get_default_results """
        return BaseStrategy.get_default_results(code_error=code_error, instantiation_error=instantiation_error, strategy_error=strategy_error)
        
    @staticmethod
    def get_default_results(code_error=None, instantiation_error=None, strategy_error=None):
        """ Get default results with the option to include a set of UserlandError instances
        Args:
            code_error: an that originated when rendering the code
            instantiation_error: an that originated when instantiating the layer
            strategy_error: an that originated when running the layer
        """
        results = LayerResults(
            sample={},
            out_shape={},
            variables={},
            columns=[],
            code_error=code_error,
            instantiation_error=instantiation_error,
            strategy_error=strategy_error,
            trained = False
        )                
        return results

    
class DefaultStrategy(BaseStrategy):
    def run(self, layer_spec, graph_spec, input_results, line_offset=None):    
        return self.get_default()


class JinjaLayerStrategy(BaseStrategy):
    def __init__(self, script_factory):
        self._script_factory = script_factory

    def run(self, layer_spec, graph_spec, input_results, line_offset=None):
        layer_class, line_offset, code_error, instantiation_error = self._get_layer_class(layer_spec, graph_spec, input_results)
        if layer_class is None:
            return self.get_default(code_error=code_error, instantiation_error=instantiation_error)
        else:
            return self._run_internal(layer_spec, graph_spec, layer_class, input_results, line_offset=line_offset)

    @abstractmethod
    def _run_internal(self, layer_spec, graph_spec, layer_class, input_results, line_offset):
        raise NotImplementedError
    
    def _get_layer_code(self, layer_id, layer_spec, graph_spec):
        layer_helper = LayerHelper(self._script_factory, layer_spec, graph_spec)
        try:
            code = layer_helper.get_code(check_syntax=True)
        except SyntaxError as e:
            logger.exception(f"Layer {layer_spec.id_} raised an error when getting layer code")
            layer_code_offset = layer_helper.get_line_count(prepend_imports=True, layer_code=False) # Get length of imports
            message = format_exception(e, adjust_by_offset=layer_code_offset)
            error = UserlandError(layer_id, layer_spec.type_, e.lineno, message)
            return None, error
        except Exception as e:
            logger.warning(f"{type(e).__name__}: {str(e)} | couldn't get code for {layer_spec.id_}. Treating it as not fully specified")
            if logger.isEnabledFor(logging.DEBUG):
                logger.warning("layer spec: \n" + stringify(layer_spec.to_dict()))
            return None, None
        else:
            return code, None
        
    def _get_layer_class(self, layer_spec, graph_spec, input_results):
        code, code_error = self._get_layer_code(layer_spec.id_, layer_spec, graph_spec)
        
        if code is None:
            return None, 0, code_error, None

        if not layer_spec.is_fully_configured:  # E.g., required input connections aren't set..
            return None, 0, None, None

        layer_helper = LayerHelper(self._script_factory, layer_spec, graph_spec)
        layer_code_offset = layer_helper.get_line_count(prepend_imports=True, layer_code=False) # Get length of imports
        try:
            layer_class = layer_helper.get_class()
        except Exception as e:
            layer_class = None
            instantiation_error = exception_to_error(layer_spec.id_, layer_spec.type_, e, line_offset=layer_code_offset)
            logger.debug(f"Layer {layer_spec.id_} raised an error when executing module " + repr(e))
        else:
            instantiation_error = None

        if layer_class is None:
            return None, layer_code_offset, None, instantiation_error

        return layer_class, layer_code_offset, None, None


class DataSupervisedStrategy(JinjaLayerStrategy):
    def _run_internal(self, layer_spec, graph_spec, layer_class, input_results, line_offset=None):
        try:
            layer_instance = layer_class()
            columns = layer_instance.columns        
            output = layer_instance.sample
            variables = layer_instance.variables.copy()
        except Exception as e:
            output = {'output': None}
            shape = {'output': None}
            variables = {}
            columns = []
            strategy_error = exception_to_error(layer_spec.id_, layer_spec.type_, e, line_offset=line_offset)
            logger.debug(f"Layer {layer_spec.id_} raised an error when calling sample property")                        
        else:
            shape = {name: np.atleast_1d(value).shape for name, value in output.items()}
            strategy_error = None

        results = LayerResults(
            sample=output,
            out_shape=shape,
            variables=variables,
            columns=columns,
            code_error=None,
            instantiation_error=None,
            strategy_error=strategy_error,
            trained = False
        )
        return results

    
class DataReinforceStrategy(JinjaLayerStrategy):
    def _run_internal(self, layer_spec, graph_spec, layer_class, input_results, line_offset=None):
        layer_instance = layer_class()
        try:
            y = layer_instance.sample
        except Exception as e:
            y = None
            shape = None
            strategy_error = exception_to_error(layer_spec.id_, layer_spec.type_, e, line_offset=line_offset)
            logger.debug(f"Layer {layer_spec.id_} raised an error when calling sample property")                        
        else:
            shape = np.atleast_1d(y).shape
            strategy_error=None

        variables = layer_instance.variables.copy()
        
        results = LayerResults(
            sample=y,
            out_shape=shape,
            variables=variables,
            columns = [],
            code_error=None,
            instantiation_error=None,
            strategy_error=strategy_error,
            trained = False
        )
        return results

    
class TrainingStrategy(JinjaLayerStrategy):    
    PREAMBLE  = 'import logging\n'
    PREAMBLE += 'log = logging.getLogger(__name__)\n\n'
    PREAMBLE_LINES = len(PREAMBLE.split('\n')) - 1
    
    @abstractmethod
    def _create_graph_and_run(self, layer_spec, graph_spec, line_offset):
        raise NotImplementedError
    
    def _run_internal(self, layer_spec, graph_spec, layer_class, input_results, line_offset=None):
        sample, shape, variables, strategy_error = self._create_graph_and_run(
            layer_spec, graph_spec, line_offset=line_offset
        )        
        results = LayerResults(
            sample=sample,
            out_shape=shape,
            variables=variables,
            columns=[],
            code_error=None,
            instantiation_error=strategy_error,
            strategy_error=strategy_error,
            trained = False
        )
        return results

    def _create_graph(self, graph_spec):
        """ Creates the graph since it's needed as input for the training layer"""
        try:
            graph = graph_spec_to_core_graph(self._script_factory, graph_spec, preamble=self.PREAMBLE)
        except Exception as e:
            graph = None
            logger.info("create graph step failed: " + repr(e))        
        return graph

    def _run_training_layer(self, graph, layer_spec, line_offset):
        """ Run the training layer """
        try:
            training_layer = graph.active_training_node.layer
            training_layer.init_layer(graph)
            sample = training_layer.sample
            variables = training_layer.variables.copy()
        except Exception as e:
            strategy_error = exception_to_error(layer_spec.id_, layer_spec.type_, e, line_offset=(line_offset + self.PREAMBLE_LINES))
            sample = {'output': None}
            shape = {'output': None}
            variables = {}
            logger.debug(f"Layer {layer_spec.id_} raised an error when initializing")
        else:
            strategy_error = None
            shape = {name: np.atleast_1d(value).shape for name, value in sample.items()}    

        return sample, shape, variables, strategy_error


class IoLayerStrategy(BaseStrategy):
    def __init__(self, data_loader):
        self._dataset = data_loader.get_dataset()
    
    def run(self, layer_spec, layer_class, input_results, line_offset=None):
        columns = []
        variables = {}
        
        try:
            value = self._get_first_batch_from_dataset(layer_spec).numpy()
            output = {'output': value}
        except Exception as e:
            output = {'output': None}
            shape = {'output': None}
            strategy_error = exception_to_error(layer_spec.id_, layer_spec.type_, e, line_offset=line_offset)
            logger.debug(f"Layer {layer_spec.id_} raised an error when calling sample property")                        
        else:
            shape = {name: np.atleast_1d(value).shape for name, value in output.items()}
            strategy_error = None

        results = LayerResults(
            sample=output,
            out_shape=shape,
            variables=variables,
            columns=columns,
            code_error=None,
            instantiation_error=None,
            strategy_error=strategy_error,
            trained = False
        )
        return results

    def _get_first_batch_from_dataset(self, layer_spec):
        inputs_batch, targets_batch = next(iter(self._dataset))

        if layer_spec.is_input_layer:
            return inputs_batch[layer_spec.feature_name]
        elif layer_spec.is_output_layer:
            return targets_batch[layer_spec.feature_name]
        else:
            raise RuntimeError


        

