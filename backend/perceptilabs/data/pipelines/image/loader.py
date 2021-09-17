import collections
import numpy as np
import tensorflow as tf
import skimage.io
import os

from perceptilabs.data.pipelines.base import PipelineBuilder, BasePipeline


class Loader(BasePipeline):  # TODO: move out and add to included files
    def call(self, path):
        image = self._load_image(path, self.metadata["has_tiff"])

        if self.resize:
            image = self.resize(image)

        return image

    def build(self, input_shape):
        if self.preprocessing and self.preprocessing.resize:
            target_shape = self.metadata['target_shape']
            self.resize = lambda x: tf.image.resize(x, target_shape)
        else:
            self.resize = None

    @staticmethod
    def _load_image(path_tensor, has_tiff):
        if has_tiff:
            def load_tiff(path_tensor):
                path = path_tensor.numpy().decode()
                image = np.atleast_3d(skimage.io.imread(path).astype(np.uint16))
                image_tensor = tf.constant(image)
                return image_tensor

            image_decoded = tf.py_function(load_tiff, [path_tensor], tf.uint16)
            image_decoded.set_shape([None, None, None])  # Make sure the shape is present
        else:
            image_encoded = tf.io.read_file(path_tensor)
            image_decoded = tf.image.decode_image(image_encoded, expand_animations=False, channels=None)  # animated im

        image_decoded = image_decoded[:, :, :3]  # DISCARD ALPHA CHANNEL
        return image_decoded

    @classmethod
    def from_data(cls, dataset, preprocessing=None):
        """ Convenience method for testing"""
        metadata = cls.compute_metadata(dataset, preprocessing)
        return cls(preprocessing=preprocessing, metadata=metadata)

    @classmethod
    def compute_metadata(cls, dataset, preprocessing):
        has_tiff = cls._has_tiff(dataset)
        target_shape = cls._get_target_shape(dataset, preprocessing, has_tiff)
        n_channels = cls._get_n_channels(dataset, has_tiff)

        metadata = {
            "target_shape": target_shape, "has_tiff": has_tiff, "n_channels": n_channels
        }
        return metadata

    @classmethod
    def _get_n_channels(cls, dataset, has_tiff):
        path = next(iter(dataset))
        height, width, channels = cls._load_image(path, has_tiff).shape
        return channels

    @staticmethod
    def _has_tiff(dataset):
        def gen():
            for path_tensor in dataset:
                path = path_tensor.numpy().decode().lower()
                _, ext = os.path.splitext(path)
                yield ext in ['.tif', '.tiff']

        return any(gen())

    @classmethod
    def _get_target_shape(cls, dataset, preprocessing, has_tiff):
        def get_first_image_shape():
            path = next(iter(dataset))
            height, width, channels = cls._load_image(path, has_tiff).shape
            return (height, width)

        if preprocessing is None:
            return get_first_image_shape()

        if not preprocessing.resize:
            return get_first_image_shape()

        if preprocessing.resize_mode == 'custom':
            height = preprocessing.resize_height
            width = preprocessing.resize_width
            return (height, width)
        elif preprocessing.resize_mode == 'automatic':
            all_shapes = (
                cls._load_image(path, has_tiff).shape
                for path in dataset
            )

            if preprocessing.resize_automatic_mode == 'min':
                min_height = 10**2
                min_width = 10**2

                for (height, width, channels) in all_shapes:
                    min_height = min(min_height, height)
                    min_width = min(min_width, width)

                return (min_height, min_width)
            elif preprocessing.resize_automatic_mode == 'max':
                max_height = 0
                max_width = 0

                for (height, width, channels) in all_shapes:
                    max_height = max(max_height, height)
                    max_width = max(max_width, width)

                return (max_height, max_width)
            elif preprocessing.resize_automatic_mode == 'mean':
                running_height = 0
                running_width = 0
                count = 0

                for (height, width, channels) in all_shapes:
                    running_height += height
                    running_width += width
                    count += 1

                return (int(running_height/count), int(running_width/count))
            elif preprocessing.resize_automatic_mode == 'mode':
                counts = collections.defaultdict(int)

                for (height, width, channels) in all_shapes:
                    counts[(height, width)] += 1

                mode_shape = None
                for shape, count in counts.items():

                    if mode_shape is None:
                        mode_shape = shape
                    elif count > counts[mode_shape]:
                        mode_shape = shape

                return mode_shape
            else:
                raise ValueError
