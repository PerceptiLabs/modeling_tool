import os
import pickle
import logging
import tempfile
from unittest.mock import MagicMock

import tensorflow as tf
import numpy as np
import pandas as pd

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.data.base import DataLoader, FeatureSpec
from perceptilabs.script import ScriptFactory
from perceptilabs.data.base import DataLoader, FeatureSpec
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.utils import sanitize_path
import perceptilabs.tracking as tracking
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class Exporter:
    def __init__(self, graph_spec, training_model, data_loader, model_id=None, user_email=None, checkpoint_file=None):
        self._graph_spec = graph_spec
        self._data_loader = data_loader
        self._training_model = training_model
        self._model_id = model_id
        self._user_email = user_email
        self._checkpoint_file = checkpoint_file

    @classmethod
    def from_disk(cls, checkpoint_directory, graph_spec, script_factory, data_loader, model_id=None, user_email=None):
        checkpoint_directory = sanitize_path(checkpoint_directory)
        weights_path = tf.train.latest_checkpoint(checkpoint_directory)
        training_model = TrainingModel(script_factory, graph_spec)
        training_model.load_weights(filepath=weights_path)
        logger.info(f"Loaded weights from {weights_path}")
        return cls(graph_spec, training_model, data_loader, model_id=model_id, user_email=user_email, checkpoint_file=weights_path)

    @property
    def checkpoint_file(self):
        return self._checkpoint_file

    @property
    def data_loader(self):
        return self._data_loader

    @property
    def training_model(self):
        return self._training_model

    def export_checkpoint(self, path, epoch=None):
        """ Save the model weights """
        model = self._training_model
        file_path = os.path.join(
            path, self.format_checkpoint_prefix(epoch=epoch))
        model.save_weights(sanitize_path(file_path))

    def export(self, export_path, mode):
        """calls the export functions based on export mode"""
        if mode == 'Standard':
            return self._export_training_model(export_path)
        elif mode == 'Compressed':
            return self._export_compressed_model(export_path)
        elif mode == 'Quantized':
            return self._export_quantized_model(export_path)

    def _export_training_model(self, path):
        """ Export the inference model """
        model = self.get_inference_model()
        model.save(sanitize_path(path))
        tracking.send_model_exported(self._user_email, self._model_id)

    def _export_compressed_model(self, path):
        """ Export the compressed model """
        model = self.get_inference_model()
        frozen_path = os.path.join(path, 'model.tflite')
        if not os.path.exists(path):
            os.mkdir(path)
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.post_training_quantize = True
        tflite_model = converter.convert()
        with open(frozen_path, "wb") as f:
            f.write(tflite_model)
        tracking.send_model_exported(self._user_email, self._model_id)


    def _export_quantized_model(self, path):
        """ Export the quantized model """
        # checking the number of input layers in the dataset
        feature_specs = self._data_loader.feature_specs
        num_input_layers = 0
        for layer in feature_specs:
            if feature_specs[layer].iotype == 'input':
                num_input_layers += 1
        if num_input_layers > 1:
            return "Not compatible"
        model = self.get_inference_model()

        def representative_data_gen():
            data_size = min(100, int(self._data_loader.get_dataset_size()/5))
            for input_value,_ in self._data_loader.get_dataset(partition='training').batch(1).take(data_size):
                yield [list(input_value.values())[0]]

        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = representative_data_gen
        # Ensure that if any ops can't be quantized, the converter throws an error
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        # Set the input and output tensors to uint8 (APIs added in r2.3)
        converter.inference_input_type = tf.uint8
        converter.inference_output_type = tf.uint8
        try:
            tflite_model = converter.convert()
        except Exception as e:
            logger.exception(e)
            return "Not compatible"
        frozen_path = os.path.join(path, 'quantized_model.tflite')
        if not os.path.exists(path):
            os.mkdir(path)
        with open(frozen_path, "wb") as f:
            f.write(tflite_model)
        tracking.send_model_exported(self._user_email, self._model_id)

    def get_inference_model(self):
        """ Convert the Training Model to a simpler version (e.g., skip intermediate outputs)  """
        # TODO: add option to include pre- and post-processing pipelines (story 1609)
        inputs = {}
        for layer_spec in self._graph_spec:
            if not layer_spec.is_input_layer:
                continue
            shape = self._data_loader.get_feature_shape(
                layer_spec.feature_name)

            if shape.rank == 0:
                shape = tf.TensorShape([1])

            inputs[layer_spec.feature_name] = tf.keras.Input(
                shape=shape,
                name=layer_spec.feature_name # Giving the input a name allows us to pass dicts in. https://github.com/tensorflow/tensorflow/issues/34114#issuecomment-588574494
            )

        outputs, _ = self._training_model(inputs)
        inference_model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return inference_model

    @staticmethod
    def format_checkpoint_prefix(epoch=None):
        if epoch is not None:
            return f"checkpoint-{epoch:04d}.ckpt"
        else:
            return "checkpoint.ckpt"
