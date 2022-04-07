from abc import abstractmethod, ABC
import logging

import pandas as pd
import numpy as np


from perceptilabs.lwcore.utils import exception_to_error
from perceptilabs.lwcore.results import LayerResults
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.lwcore.utils import exception_to_error, format_exception
from perceptilabs.issues import UserlandError
from perceptilabs.utils import stringify

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    @abstractmethod
    def run(
        self,
        layer_spec,
        graph_spec,
        input_results,
        random_number_generator,
        line_offset=None,
    ):
        raise NotImplementedError

    @staticmethod
    def get_default(code_error=None, instantiation_error=None, strategy_error=None):
        """Alias for get_default_results"""
        return BaseStrategy.get_default_results(
            code_error=code_error,
            instantiation_error=instantiation_error,
            strategy_error=strategy_error,
        )

    @staticmethod
    def get_default_results(
        code_error=None, instantiation_error=None, strategy_error=None
    ):
        """Get default results with the option to include a set of UserlandError instances
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
            trained=False,
        )
        return results


class DefaultStrategy(BaseStrategy):
    def run(
        self,
        layer_spec,
        graph_spec,
        input_results,
        random_number_generator,
        line_offset=None,
    ):
        return self.get_default()


class JinjaLayerStrategy(BaseStrategy):
    def __init__(self, script_factory):
        self._script_factory = script_factory

    def run(
        self,
        layer_spec,
        graph_spec,
        input_results,
        random_number_generator,
        line_offset=None,
    ):
        (
            layer_class,
            line_offset,
            code_error,
            instantiation_error,
        ) = self._get_layer_class(layer_spec, graph_spec, input_results)
        if layer_class is None:
            return self.get_default(
                code_error=code_error, instantiation_error=instantiation_error
            )
        else:
            return self._run_internal(
                layer_spec,
                graph_spec,
                layer_class,
                input_results,
                random_number_generator,
                line_offset=line_offset,
            )

    @abstractmethod
    def _run_internal(
        self,
        layer_spec,
        graph_spec,
        layer_class,
        input_results,
        random_number_generator,
        line_offset,
    ):
        raise NotImplementedError

    def _get_layer_code(self, layer_id, layer_spec, graph_spec):
        layer_helper = LayerHelper(self._script_factory, layer_spec, graph_spec)
        try:
            code = layer_helper.get_code(check_syntax=True)
        except SyntaxError as e:
            logger.exception(
                f"Layer {layer_spec.id_} raised an error when getting layer code"
            )
            layer_code_offset = layer_helper.get_line_count(
                prepend_imports=True, layer_code=False
            )  # Get length of imports
            message = format_exception(e, adjust_by_offset=layer_code_offset)
            error = UserlandError(layer_id, layer_spec.type_, e.lineno, message)
            return None, error
        except Exception as e:
            logger.warning(
                f"{type(e).__name__}: {str(e)} | couldn't get code for {layer_spec.id_}. Treating it as not fully specified"
            )
            if logger.isEnabledFor(logging.DEBUG):
                logger.warning("layer spec: \n" + stringify(layer_spec.to_dict()))
            return None, None
        else:
            return code, None

    def _get_layer_class(self, layer_spec, graph_spec, input_results):
        code, code_error = self._get_layer_code(layer_spec.id_, layer_spec, graph_spec)

        if code is None:
            return None, 0, code_error, None

        if (
            not layer_spec.is_fully_configured
        ):  # E.g., required input connections aren't set..
            logger.warning(f"Layer {layer_spec.name} is not fully configured")
            return None, 0, None, None

        layer_helper = LayerHelper(self._script_factory, layer_spec, graph_spec)
        layer_code_offset = layer_helper.get_line_count(
            prepend_imports=True, layer_code=False
        )  # Get length of imports
        try:
            layer_class = layer_helper.get_class()
        except Exception as e:
            layer_class = None
            instantiation_error = exception_to_error(
                layer_spec.id_, layer_spec.type_, e, line_offset=layer_code_offset
            )
            logger.debug(
                f"Layer {layer_spec.id_} raised an error when executing module "
                + repr(e)
            )
        else:
            instantiation_error = None

        if layer_class is None:
            return None, layer_code_offset, None, instantiation_error

        return layer_class, layer_code_offset, None, None


class IoLayerStrategy(BaseStrategy):
    def __init__(self, data_batch):
        self._data_batch = data_batch

    def run(self, layer_spec, layer_class, input_results, line_offset=None):
        columns = []
        variables = {}

        try:
            value = self._data_batch.numpy()
            output = {"output": value}
        except Exception as e:
            output = {"output": None}
            shape = {"output": None}
            strategy_error = exception_to_error(
                layer_spec.id_, layer_spec.type_, e, line_offset=line_offset
            )
            logger.debug(
                f"Layer {layer_spec.id_} raised an error when calling sample property"
            )
        else:
            shape = {name: np.atleast_1d(value).shape for name, value in output.items()}
            strategy_error = None

            shape_error = self._validate_shapes(layer_spec, input_results, shape)
            if shape_error:
                strategy_error = UserlandError(
                    layer_spec.id_, layer_spec.type_, None, shape_error
                )

        results = LayerResults(
            sample=output,
            out_shape=shape,
            variables=variables,
            columns=columns,
            code_error=None,
            instantiation_error=None,
            strategy_error=strategy_error,
            trained=False,
        )
        return results

    def _validate_shapes(self, layer_spec, input_results, shape):
        for conn in layer_spec.backward_connections:
            if not conn.src_id in input_results:
                continue

            prediction_shape = input_results[conn.src_id].out_shape.get("output")
            target_shape = shape.get("output")

            if prediction_shape != target_shape:
                message = f"Error in layer {layer_spec.name}. Expected shape {target_shape} but got {prediction_shape}"
                return message

        return None
