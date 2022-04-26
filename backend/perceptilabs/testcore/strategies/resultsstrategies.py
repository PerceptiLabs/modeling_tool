import logging
import numpy as np
import pkg_resources
from abc import ABC, abstractmethod
import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt

from perceptilabs.createDataObject import createDataObject, subsample


logger = logging.getLogger(__name__)


class ResultsStrategy(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError


class ProcessShapValues(ResultsStrategy):
    def __init__(self, results):
        self._results = results

    def run(self):
        from pathlib import Path

        shap_values = self._results["shap_values"]
        test_samples = self._results["test_samples"]

        images = []
        for index, shap_value, test_sample in self._generate_samples(
            shap_values, test_samples
        ):
            image = self._create_plot(
                shap_value,
                test_sample,
                default_path=Path.home() / f"shap_plot_{index}.png",
            )
            images.append(image)

        data_object = createDataObject(
            data_list=images,  # TODO: frontend should handle this
            normalize=True,
            ratio=1.0,
        )
        return {"image": data_object}

    def _generate_samples(self, shap_values, test_samples):
        import os

        n_samples_max = int(os.getenv("PL_SHAP_MAX_IMAGES", 1))
        n_samples_available = len(test_samples)

        n_samples_used = min(n_samples_max, n_samples_available)
        logger.info(
            f"Samples used: {n_samples_used}. Limit: {n_samples_max}, available: {n_samples_available}"
        )

        for index in range(n_samples_used):
            yield (index, shap_values[index], test_samples[index])

    def _create_plot(self, shap_value, test_sample, default_path):
        import shap

        shap.image_plot(shap_value, test_sample)
        fig = plt.gcf()
        fig.set_facecolor("#2B2C31")
        fig.set_alpha(0.0)

        ax = plt.gca()
        im = ax.images

        cb = im[-1].colorbar

        cb.ax.xaxis.label.set_color("white")
        cb.ax.tick_params(axis="x", colors="white")

        fig.canvas.draw()

        data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        return image


class ProcessConfusionMatrix(ResultsStrategy):
    def __init__(self, results):
        self._results = results

    def run(self):
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


class ProcessMetricsTable(ResultsStrategy):
    def __init__(self, results):
        self._results = results

    def run(self):
        return self._results


class ProcessOutputsVisualization(ResultsStrategy):
    def __init__(self, results):
        self._results = results

    def run(self):
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
