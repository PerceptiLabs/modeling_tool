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
        self._model = model
        self._stopped = False
        
    @classmethod
    def from_checkpoint(cls, checkpoint_directory, graph_spec, data_loader):
        """
        load model from checkpoint and graphspec
        """
        script_factory = ScriptFactory()
        exporter = Exporter.from_disk(checkpoint_directory, graph_spec, script_factory, data_loader)
        model = exporter.training_model
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
        self._counter = 0
        for input_,label in data_iterator:
            if self._stopped:
                break
            else:
                output,_ = self._model.predict(input_) #* running in inferene mode 
                outputs.append(output)
                labels.append(label)
                self._counter += 1
        return {'outputs':outputs, 'labels':labels}

    def stop(self):
        self._stopped = True

    @property
    def num_samples_inferred(self):
        return self._counter
