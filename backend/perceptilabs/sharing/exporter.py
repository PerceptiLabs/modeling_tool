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
import perceptilabs.sharing.fastapi_utils as fastapi_utils

logger = logging.getLogger(__name__)


class CompatibilityError(Exception):
    pass


class Exporter:
    def __init__(self, graph_spec, training_model, data_loader, on_model_exported=None):
        self._graph_spec = graph_spec
        self._data_loader = data_loader
        self._training_model = training_model
        self._on_model_exported = on_model_exported

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

    def export(self, export_directory, mode, include_preprocessing=True, include_postprocessing=True):
        """calls the export functions based on export mode"""
        created_paths = []
        
        if mode == 'Standard':
            created_paths = self._export_inference_model(
                export_directory,
                include_preprocessing=include_preprocessing,
                include_postprocessing=include_postprocessing
            )
        elif mode == 'Compressed':
            created_paths = self._export_compressed_model(export_directory)
        elif mode == 'Quantized':
            created_paths = self._export_quantized_model(export_directory)
        elif mode == 'FastAPI':
            created_paths = self._export_fastapi_service(
                export_directory,
                include_preprocessing=include_preprocessing,
                include_postprocessing=include_postprocessing
            )
        else:
            raise NotImplementedError(f"Unknown export mode '{mode}'")

        if self._on_model_exported:
            self._on_model_exported()
            
        return created_paths
            
    def _export_inference_model(self, directory, model=None, include_preprocessing=True, include_postprocessing=True):
        """ Export the inference model """
        if model is None:
            model = self.get_inference_model(
                include_preprocessing=include_preprocessing,
                include_postprocessing=include_postprocessing
            )

        directory = sanitize_path(directory)
        model.save(directory)
        
        return [
            os.path.join(directory, name) for name in
            ('saved_model.pb', 'variables', 'keras_metadata.pb', 'assets')
        ]

    def _export_fastapi_service(self, path, include_preprocessing=True, include_postprocessing=True):
        """ Export the inference model wrapped in a REST endpoint script """
        model = self.get_inference_model(include_preprocessing=include_preprocessing, include_postprocessing=include_postprocessing)
        inference_model_paths = self._export_inference_model(path, model=model)  # TODO: not used!


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

        example_json = os.path.join(path, 'example.json')
        with open(example_json, 'w') as f:
            json.dump(example_data, f, default=convert, indent=4)

        for partition in ['test', 'validation', 'training']:
            df = self._data_loader.get_data_frame(partition=partition).head(10)  # keep N first rows
            if len(df) > 0:
                break
        example_csv = os.path.join(path, fastapi_utils.EXAMPLE_CSV_FILE)            
        df.to_csv(example_csv, index=False)

        fastapi_paths = [
            example_csv,
            example_json,
            fastapi_utils.render_fastapi_requirements(path),
            fastapi_utils.render_fastapi_example_requirements(path),
            fastapi_utils.render_fastapi_example_script(path, self._data_loader.feature_specs),
            fastapi_utils.render_fastapi_script(
                path, model, self._graph_spec, self._data_loader.metadata)
        ]
        return inference_model_paths + fastapi_paths

    def _export_compressed_model(self, path):
        """ Export the compressed model """
        model = self.get_inference_model(include_preprocessing=False, include_postprocessing=False)
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

        return [frozen_path]

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

        model = self.get_inference_model(include_preprocessing=False, include_postprocessing=False)

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

        return [frozen_path]

    def get_inference_model(self, include_preprocessing=True, include_postprocessing=True):
        """ Convert the Training Model to a simpler version (e.g., skip intermediate outputs)  """
        inference_model = self._training_model.as_inference_model(
            self._data_loader, include_preprocessing=include_preprocessing, include_postprocessing=include_postprocessing)

        return inference_model

    @staticmethod
    def parse_export_mode(export_settings):
        type_ = export_settings['Type']
        if type_== 'TFModel':
            if export_settings['Compressed']:
                return 'Compressed'
            elif export_settings['Quantized']:
                return 'Quantized'
            else:
                return 'Standard'
        else:
            return type_

        
