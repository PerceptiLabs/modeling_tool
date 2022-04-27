from abc import ABC, abstractmethod
import numpy as np
import tensorflow as tf
import time
from perceptilabs.trainer.losses import dice, dice_coefficient
from perceptilabs.stats.iou import IouStatsTracker, IouStats


class DatasetError(ValueError):
    pass


class BaseStrategy(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError


class ConfusionMatrix(BaseStrategy):
    def __init__(self, model_outputs, compatible_output_layers, categories):
        self._model_outputs = model_outputs
        self._compatible_output_layers = compatible_output_layers
        self._categories = categories

    def run(self):
        confusion_matrices = {}
        for layer in self._compatible_output_layers:
            labels = [x[layer].numpy() for x in self._model_outputs["targets"]]
            outputs = [x[layer] for x in self._model_outputs["outputs"]]
            predictions = [np.argmax(output) for output in outputs]
            targets = [np.argmax(label) for label in labels]
            num_classes = np.asarray(labels).shape[2]  # TODO: get class names
            confusion_matrix = tf.math.confusion_matrix(
                targets, predictions, num_classes=num_classes
            )
            confusion_matrices[layer] = {
                "data": confusion_matrix,
                "categories": self._categories[layer],
            }
        return confusion_matrices


class MetricsTable(BaseStrategy):
    def __init__(self, model_outputs, compatible_output_layers):
        self._model_outputs = model_outputs
        self._compatible_output_layers = compatible_output_layers

    def run(self):
        metrics_tables = {}
        for layer in self._compatible_output_layers:
            if self._compatible_output_layers[layer] == "mask":
                metrics_tables = self._run_mask_metrics(
                    layer, self._model_outputs, metrics_tables
                )
            elif self._compatible_output_layers[layer] == "categorical":
                metrics_tables = self._run_categorical_metrics(
                    layer, self._model_outputs, metrics_tables
                )
        return metrics_tables

    def _run_categorical_metrics(self, layer, model_outputs, metrics_tables):
        metrics = {
            "categorical_accuracy": tf.keras.metrics.CategoricalAccuracy(),
            "top_5_categorical_accuracy": tf.keras.metrics.TopKCategoricalAccuracy(k=5),
            "precision": tf.keras.metrics.Precision(),
            "recall": tf.keras.metrics.Recall(),
        }

        metrics_tables[layer] = {}
        labels = np.asarray(
            [np.squeeze(x[layer].numpy()) for x in model_outputs["targets"]]
        )
        outputs = np.asarray([np.squeeze(x[layer]) for x in model_outputs["outputs"]])
        predictions = np.zeros_like(outputs)
        predictions[np.arange(len(outputs)), outputs.argmax(1)] = 1
        targets = np.zeros_like(labels)
        targets[np.arange(len(labels)), labels.argmax(1)] = 1
        for metric in ["categorical_accuracy", "top_5_categorical_accuracy"]:
            metrics[metric].update_state(labels, outputs)
            metrics_tables[layer][metric] = np.float(metrics[metric].result().numpy())
            metrics[metric].reset_states()
        for metric in ["precision", "recall"]:
            metrics[metric].update_state(targets, predictions)
            metrics_tables[layer][metric] = np.float(metrics[metric].result().numpy())
            metrics[metric].reset_states()
        return metrics_tables

    def _run_mask_metrics(self, layer, model_outputs, metrics_tables):
        metrics = {
            "IoU": IouStatsTracker(),
            "dice": dice,
            "cross_entropy": tf.keras.losses.CategoricalCrossentropy(),
        }
        metrics_tables[layer] = {}
        targets = np.asarray([x[layer].numpy() for x in model_outputs["targets"]])
        outputs = np.asarray([x[layer] for x in model_outputs["outputs"]])
        metrics["IoU"].update(
            predictions_batch=outputs,
            targets_batch=targets,
            epochs_completed=0,
            is_training=False,
            steps_completed=0,
            threshold=0.5,
        )
        iou_stats = metrics["IoU"].save()
        metrics_tables[layer]["IoU"] = round(
            float(iou_stats.get_iou_for_latest_step()), 2
        )
        if targets.shape[-1] <= 2:
            metrics_tables[layer]["loss"] = round(
                float(dice(outputs, targets).numpy()), 2
            )  # pytest was failing without the conversions
        else:
            metrics_tables[layer]["loss"] = round(
                float(metrics["cross_entropy"](outputs, targets).numpy()), 2
            )
        return metrics_tables


class OutputVisualization(BaseStrategy):
    def __init__(self, model_inputs, model_outputs, compatible_output_layers):
        self._model_inputs = model_inputs
        self._model_outputs = model_outputs
        self._compatible_output_layers = compatible_output_layers

    def run(self):
        """
        takes all the model outputs and calculates the loss on each sample. Best performing 5 samples and worst performing 5 samples are returned.
        Args:
            model_inputs ([list]): inputs list
            model_outputs ([dict]): contains lists of targets and predictions
            compatible_output_layers ([dict]): dict containing compatible layers and their datatypes
        returns:
            best 5 segmented images and their inputs and original segmentations and the worst 5.
        """
        output_images = {}
        for layer in self._compatible_output_layers:
            output_images[layer] = {}
            losses = []
            predictions = [x[layer] for x in self._model_outputs["outputs"]]
            targets = [x[layer].numpy() for x in self._model_outputs["targets"]]
            inputs = [
                list(x.values())[0] for x in self._model_inputs
            ]  # TODO: need to fix this for multi input/output
            for target, prediction in zip(targets, predictions):
                loss_fn = tf.keras.losses.CategoricalCrossentropy()
                loss = loss_fn(target, prediction).numpy()
                losses.append(loss)
            sorted_loss_indices = sorted(range(len(losses)), key=lambda i: losses[i])
            n = min(5, int(len(inputs) / 2))
            top_n_indices = sorted_loss_indices[-n:]
            bottom_n_indices = sorted_loss_indices[:n]
            selected_indices = bottom_n_indices + top_n_indices
            selected_inputs = [inputs[i] for i in selected_indices]
            selected_targets = [targets[i] for i in selected_indices]
            selected_predictions = [predictions[i] for i in selected_indices]
            selected_losses = [losses[i] for i in selected_indices]

            output_images[layer] = {
                "inputs": selected_inputs,
                "targets": selected_targets,
                "predictions": selected_predictions,
                "losses": selected_losses,
            }
        return output_images


class ShapValues:
    class ExplainerFactory:  # Factory necessary because "import shap" modifies tensorflow, causing unrelated tests to fail
        def make(self, model, background):
            import shap

            return shap.DeepExplainer(model, background)

    def __init__(
        self,
        data_iterator,
        training_model,
        n_background_samples_min=20,
        n_background_samples_max=100,
        n_visualized_samples=10,
        explainer_factory=None,
    ):
        self._data_iterator = data_iterator
        self._training_model = training_model
        self._n_background_samples_min = n_background_samples_min
        self._n_background_samples_max = n_background_samples_max
        self._n_visualized_samples = n_visualized_samples
        self._explainer_factory = explainer_factory or self.ExplainerFactory()

    def _get_input_feature(self):
        input_specs, _ = self._data_iterator.element_spec

        if len(input_specs) != 1:
            raise DatasetError("Shap Values test need exactly one input feature!")

        return list(input_specs.keys())[0]

    def _get_target_feature(self):
        _, target_specs = self._data_iterator.element_spec

        if len(target_specs) != 1:
            raise DatasetError("Shap Values test need exactly one target feature!")

        return list(target_specs.keys())[0]

    def run(self):
        input_feature = self._get_input_feature()
        target_feature = self._get_target_feature()

        background_samples, test_samples = self._create_data_partitions(input_feature)

        explainer = self._create_explainer(
            input_feature, target_feature, background_samples
        )

        shap_values = np.zeros(test_samples.shape)
        for i in range(len(test_samples)):
            shap_values[i] = self._explain_sample(explainer, test_samples[i])

        results = {
            "shap_values": shap_values,
            "test_samples": test_samples,
        }
        return results

    def _explain_sample(self, explainer, sample):
        input_as_array = np.asarray([sample])
        output_as_array = explainer.shap_values(input_as_array)
        return output_as_array[0]

    def _create_data_partitions(self, input_feature):
        input_iterator = self._data_iterator.map(lambda inputs, _: inputs)

        n_samples_min = self._n_background_samples_min + self._n_visualized_samples
        dataset_size = len(self._data_iterator)
        if dataset_size < n_samples_min:
            raise DatasetError(
                f"The dataset is too small. The shap test requires atleast {n_samples_min} samples, but the provided dataset only contains {dataset_size}"
            )

        n_background_samples = min(
            dataset_size - self._n_visualized_samples, self._n_background_samples_max
        )

        data_subset = next(
            iter(
                input_iterator.batch(n_background_samples + self._n_visualized_samples)
            )
        )
        input_dataset = data_subset[input_feature].numpy()

        background_samples = input_dataset[:n_background_samples]
        test_samples = input_dataset[n_background_samples:]

        return background_samples, test_samples

    def _create_explainer(self, input_feature, target_feature, background):
        input_shape = background[0].shape
        model = self._create_shap_compatible_model(
            input_feature, target_feature, input_shape
        )
        explainer = self._explainer_factory.make(model, background)
        return explainer

    def _create_shap_compatible_model(self, input_feature, target_feature, input_shape):
        inputs = tf.keras.layers.Input(shape=input_shape)
        outputs, outputs_by_layer = self._training_model({input_feature: inputs})
        res = tf.keras.layers.Layer()(outputs[target_feature])
        model = tf.keras.models.Model(inputs=inputs, outputs=res)
        return model
