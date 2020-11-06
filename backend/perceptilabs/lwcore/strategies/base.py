from abc import abstractmethod, ABC
import logging

import numpy as np


from perceptilabs.lwcore.utils import exception_to_error
from perceptilabs.lwcore.results import LayerResults
from perceptilabs.logconf import APPLICATION_LOGGER


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

    
