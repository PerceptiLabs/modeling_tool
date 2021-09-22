import os
import json
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
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.exporter.fastapi_utils as fastapi_utils
import perceptilabs.tracking as tracking

logger = logging.getLogger(APPLICATION_LOGGER)


class CompatibilityError(Exception):
    pass


class Exporter:
    def __init__(self, graph_spec, training_model, data_loader, model_id=None, user_email=None):
        self._graph_spec = graph_spec
        self._data_loader = data_loader
        self._training_model = training_model
        self._model_id = model_id
        self._user_email = user_email

    @property
    def data_loader(self):
        return self._data_loader

    @property
    def training_model(self):
        return self._training_model

    def export_checkpoint(self, checkpoint_path):
        """ Save the model weights using the full checkpoint path"""
        checkpoint_path = sanitize_path(checkpoint_path)
        self._training_model.save_weights(checkpoint_path)        

    def export(self, export_directory, mode):
        """calls the export functions based on export mode"""
        if mode == 'Standard':
            self._export_inference_model(export_directory)
        elif mode == 'Compressed':
            self._export_compressed_model(export_directory)
        elif mode == 'Quantized':
            self._export_quantized_model(export_directory)
        elif mode == 'FastAPI':
            self._export_fastapi_service(export_directory)
        else:
            raise NotImplementedError(f"Unknown export mode '{mode}'")

        tracking.send_model_exported(self._user_email, self._model_id)

    def _export_inference_model(self, path, model=None):
        """ Export the inference model """
        if model is None:
            model = self.get_inference_model()

        model.save(sanitize_path(path))

    def _export_fastapi_service(self, path):
        """ Export the inference model wrapped in a REST endpoint script """
        model = self.get_inference_model()
        self._export_inference_model(path, model=model)


        dataset = self._data_loader.get_dataset(
            partition='training', apply_pipelines='loader').batch(1)
        inputs_batch, _ = next(iter(dataset))

        example_data = {
            feature_name: tensor.numpy().tolist()
            for feature_name, tensor in inputs_batch.items()
        }

        def convert(obj):
            if isinstance(obj, bytes):
                return obj.decode('utf-8')
            else:
                return obj

        with open(os.path.join(path, 'example.json'), 'w') as f:
            json.dump(example_data, f, default=convert, indent=4)

        for partition in ['test', 'validation', 'training']:
            df = self._data_loader.get_data_frame(partition=partition).head(10)  # keep N first rows
            if len(df) > 0:
                break
        df.to_csv(os.path.join(path, fastapi_utils.EXAMPLE_CSV_FILE), index=False)

        fastapi_utils.render_fastapi_requirements(path)
        fastapi_utils.render_fastapi_example_requirements(path)
        fastapi_utils.render_fastapi_example_script(path, self._data_loader.feature_specs)
        fastapi_utils.render_fastapi_script(
            path, model, self._graph_spec, self._data_loader.metadata)

    def _export_compressed_model(self, path):
        """ Export the compressed model """
        model = self.get_inference_model(include_preprocessing=False)
        frozen_path = os.path.join(path, 'model.tflite')

        if not os.path.exists(path):
            os.mkdir(path)

        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.post_training_quantize = True

        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS, # enable TensorFlow Lite ops.
            tf.lite.OpsSet.SELECT_TF_OPS # enable TensorFlow ops.
        ]

        tflite_model = converter.convert()
        with open(frozen_path, "wb") as f:
            f.write(tflite_model)

    def _export_quantized_model(self, path):
        """ Export the quantized model """
        # checking the number of input layers in the dataset
        feature_specs = self._data_loader.feature_specs
        num_input_layers = 0
        for layer in feature_specs:
            if feature_specs[layer].iotype == 'input':
                num_input_layers += 1
        if num_input_layers > 1:
            raise CompatibilityError("Number of input layers cannot be greater than 1")

        model = self.get_inference_model(include_preprocessing=False)

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
            raise CompatibilityError from e

        frozen_path = os.path.join(path, 'quantized_model.tflite')
        if not os.path.exists(path):
            os.mkdir(path)
        with open(frozen_path, "wb") as f:
            f.write(tflite_model)

    def get_inference_model(self, include_preprocessing=True):
        """ Convert the Training Model to a simpler version (e.g., skip intermediate outputs)  """
        inference_model = self._training_model.as_inference_model(
            self._data_loader, include_preprocessing=include_preprocessing)

        return inference_model

