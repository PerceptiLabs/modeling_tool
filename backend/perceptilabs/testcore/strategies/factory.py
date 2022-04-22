from perceptilabs.utils import KernelError
from perceptilabs.testcore.strategies.modelstrategies import LoadInferenceModel
from perceptilabs.testcore.strategies.teststrategies import (
    ConfusionMatrix,
    MetricsTable,
    OutputVisualization,
    ShapValues,
)

from perceptilabs.testcore.strategies.resultsstrategies import (
    ProcessConfusionMatrix,
    ProcessMetricsTable,
    ProcessOutputsVisualization,
    ProcessShapValues,
)


class TestStrategyFactory:
    def make_model_strategy(self, tests, training_model):
        # TODO: if we can remove the dependency on all tests we can make this an abstract factory

        def should_return_inputs():
            return "outputs_visualization" in tests

        def should_return_outputs():
            if "confusion_matrix" in tests:
                return True

            if "classification_metrics" in tests:
                return True

            if "segmentation_metrics" in tests:
                return True

            if "outputs_visualization" in tests:
                return True

            return False

        inference_model = LoadInferenceModel(
            training_model,
            return_inputs=should_return_inputs(),
            return_outputs=should_return_outputs(),
        )
        return inference_model

    def make_test_strategy(
        self,
        test,
        model_id,
        training_model,
        model_inputs,
        model_outputs,
        data_iterator,
        model_categories,
        compatible_output_layers,
        explainer_factory,
    ):
        if test == "confusion_matrix":
            categories = {
                layer_id: model_categories.get(layer_id)
                for layer_id in compatible_output_layers.keys()
            }

            return ConfusionMatrix(model_outputs, compatible_output_layers, categories)
        elif test == "segmentation_metrics":
            return MetricsTable(model_outputs, compatible_output_layers)
        elif test == "classification_metrics":
            return MetricsTable(model_outputs, compatible_output_layers)
        elif test == "outputs_visualization":
            return OutputVisualization(
                model_inputs, model_outputs, compatible_output_layers
            )
        elif test == "shap_values":
            return ShapValues(
                data_iterator, training_model, explainer_factory=explainer_factory
            )
        else:
            raise ValueError(f"Undefined test '{test}'")

        return results

    def make_results_strategy(self, test, results):
        if test == "confusion_matrix":
            return ProcessConfusionMatrix(results)
        elif test in ["segmentation_metrics", "classification_metrics"]:
            return ProcessMetricsTable(results)
        elif test == "outputs_visualization":
            return ProcessOutputsVisualization(results)
        elif test == "shap_values":
            return ProcessShapValues(results)
        else:
            raise KernelError(f"{test} is not supported yet.")
