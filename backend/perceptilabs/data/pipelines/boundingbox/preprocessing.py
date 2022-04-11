import numpy as np
import tensorflow as tf

from perceptilabs.data.pipelines.base import BasePipeline


class BoundingBoxPreprocessing(BasePipeline):
    def build(self, tensor_shape):
        categories_tensor = tf.constant(list(self.metadata["mapping"].keys()))
        indices_tensor = tf.constant(list(self.metadata["mapping"].values()))
        init = tf.lookup.KeyValueTensorInitializer(categories_tensor, indices_tensor)
        self._lookup_table = tf.lookup.StaticHashTable(init, default_value=-1)

    def call(self, x):
        categories = []
        bounding_boxes = []

        x = tf.reshape(x, [5, -1])
        num_boxes = x.shape[1] if x.shape[1] is not None else 1
        for i in range(num_boxes):
            j = (
                None if num_boxes == 1 and i == 1 else i
            )  # to get around initialization with symbolic tensor
            category = self._lookup_table.lookup(x[0, j])
            categories.append(category)
            bounding_box_array = tf.strings.to_number(x[1:, j])
            bounding_box_coordinates = self._convert_to_xywh(bounding_box_array)
            bounding_boxes.append(bounding_box_coordinates)

        dict_ = {
            "num_boxes": num_boxes,
            "categories": categories,
            "bounding_boxes": bounding_boxes,
            "num_categories": self._lookup_table.size(),
        }
        return dict_

    @tf.function
    def _convert_to_xywh(self, bounding_box_array):
        """xmin, ymin, xmax, ymax = bounding_box_array"""
        # Compute width and height of box
        box_width = bounding_box_array[2] - bounding_box_array[0]
        box_height = bounding_box_array[3] - bounding_box_array[1]
        # Compute x, y center
        x_center = bounding_box_array[0] + (box_width / 2)
        y_center = bounding_box_array[1] + (box_height / 2)
        return [x_center, y_center, box_width, box_height]

    @property
    def n_categories(self):
        return len(self.metadata["mapping"])

    @classmethod
    def from_data(cls, preprocessing, dataset):
        metadata = cls.compute_metadata(preprocessing, dataset, on_status_updated=None)

        return cls(preprocessing=preprocessing, metadata=metadata)

    @classmethod
    def compute_metadata(cls, preprocessing, dataset, on_status_updated=None):
        unique_values = set()
        size = sum(1 for _ in dataset)
        for index, tensor in enumerate(dataset):
            bounding_box_array = tensor.numpy()
            num_boxes = int(bounding_box_array.size / 5)
            for i in range(num_boxes):

                value = bounding_box_array[5 * i]
                if isinstance(value, bytes):
                    value = value.decode()
                else:
                    value = value.item()  # Convert to native python type
                unique_values.add(value)
                if on_status_updated:
                    on_status_updated(index=index, size=size)

        mapping = {value: idx for idx, value in enumerate(sorted(unique_values))}

        metadata = {"mapping": mapping}
        return metadata
