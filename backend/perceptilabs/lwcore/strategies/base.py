from abc import abstractmethod, ABC
import logging

import numpy as np


from perceptilabs.lwcore.utils import exception_to_error
from perceptilabs.lwcore.results import LayerResults
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.layers.utils import graph_spec_to_core_graph


logger = logging.getLogger(APPLICATION_LOGGER)


class BaseStrategy(ABC):
    @abstractmethod
    def run(self, layer_spec, layer_class, input_results, line_offset=None):
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
    def run(self, layer_spec, layer_class, input_results, line_offset=None):    
        return self.get_default()
    

class DataSupervisedStrategy(BaseStrategy):
    def run(self, layer_spec, layer_class, input_results, line_offset=None):
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

    
class DataReinforceStrategy(BaseStrategy):
    def run(self, layer_spec, layer_class, input_results, line_offset=None):
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

    
class TrainingStrategy(BaseStrategy):    
    PREAMBLE  = 'import logging\n'
    PREAMBLE += 'log = logging.getLogger(__name__)\n\n'
    PREAMBLE_LINES = len(PREAMBLE.split('\n')) - 1
    
    def __init__(self, graph_spec, script_factory):
        self._graph_spec = graph_spec
        self._script_factory = script_factory

    @abstractmethod
    def _create_graph_and_run(self, layer_spec, line_offset):
        raise NotImplementedError
    
    def run(self, layer_spec, layer_class, input_results, line_offset=None):
        sample, shape, variables, strategy_error = self._create_graph_and_run(
            layer_spec, line_offset=line_offset
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

    def _create_graph(self):
        """ Creates the graph since it's needed as input for the training layer"""
        try:
            graph = graph_spec_to_core_graph(self._script_factory, self._graph_spec, preamble=self.PREAMBLE)
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
