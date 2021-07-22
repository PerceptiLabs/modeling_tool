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
        file_path = os.path.join(path, self.format_checkpoint_prefix(epoch=epoch))
        model.save_weights(sanitize_path(file_path))

    def export_inference(self, path):
        """ Export the inference model """
        model = self.get_inference_model()
        model.save(sanitize_path(path))
        tracking.send_model_exported(self._user_email, self._model_id)                

    def get_inference_model(self):
        """ Convert the Training Model to a simpler version (e.g., skip intermediate outputs)  """        
        # TODO: add option to include pre- and post-processing pipelines (story 1609)
        inputs = {}
        for layer_spec in self._graph_spec:
            if not layer_spec.is_input_layer:
                continue
            shape = self._data_loader.get_feature_shape(layer_spec.feature_name)

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

