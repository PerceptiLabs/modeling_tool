import os
import pickle
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


class Exporter:
    def __init__(self, graph_spec, training_model):
        self._graph_spec = graph_spec
        self._data_loader = DataLoader.from_graph_spec(self._graph_spec)
        self._training_model = training_model

    @staticmethod
    def get_path(graph_spec):
        if graph_spec is not None:
            path = graph_spec.layers[0].checkpoint_path  
        return path

    @staticmethod
    def from_disk(path, graph_spec, script_factory):
        if graph_spec is not None and len(os.listdir(graph_spec.layers[0].checkpoint_path)) > 0:
            path = graph_spec.layers[0].checkpoint_path  

        training_model = TrainingModel(script_factory, graph_spec)
        weights_path = os.path.join(path, 'model_checkpoint')
        training_model.load_weights(filepath=weights_path)
        return Exporter(graph_spec, training_model)

    @property
    def data_loader(self):
        return self._data_loader
    
    @property
    def training_model(self):
        return self._training_model
    
    def export_checkpoint(self, path):      
        self.save_model_checkpoint(path)
    
    def export_inference(self, path):
        model = self.get_inference_model()
        model.save(path)

    def save_model_checkpoint(self, path):
        """ Save the model weights """
        model = self._training_model
        file_path = os.path.join(path, 'model_checkpoint')
        model.save_weights(file_path)

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

        
