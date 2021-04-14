import tensorflow as tf
import numpy as np
import os
from abc import ABC, abstractmethod
from perceptilabs.script import ScriptFactory
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.exporter.base import Exporter
import perceptilabs.utils as utils
    

class LoadInferenceModel():
    
    def __init__(self, model):
        self._script_factory = ScriptFactory(mode='tf2x')
        self._model = model
        
    @classmethod
    def from_checkpoint(cls, model_path, graph_spec):
        """
        load model from checkpoint and graphspec
        """
        script_factory = ScriptFactory(
            mode='tf2x' if utils.is_tf2x() else 'tf1x', simple_message_bus=True)
        exporter = Exporter.from_disk(model_path, graph_spec, script_factory)
        model = exporter.training_model
        return cls(model)
    
    @classmethod
    def from_saved_model(cls, model_path):
        """ load model from saved model"""
        model = tf.keras.models.load_model(model_path, None, None)
        return cls(model)
    
    def run_inference(self, data_iterator):
        """Runs inference through all the samples
        Args:
            dataLoader: Data
        Returns:
            outputs: Dict
        """
        labels = []
        outputs = []
        for input_,label in data_iterator:
            output,_ = self._model.predict(input_) #* running in inferene mode 
            outputs.append(output)
            labels.append(label)
        return {'outputs':outputs, 'labels':labels}