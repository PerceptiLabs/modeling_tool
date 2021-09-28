import tensorflow as tf
import numpy as np
import os
from abc import ABC, abstractmethod
from perceptilabs.script import ScriptFactory
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.epochs import EpochsAccess
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

        epochs_access = EpochsAccess()                
        epoch_id = epochs_access.get_latest(
            training_session_id=checkpoint_directory,  # TODO: Frontend needs to send ID
            require_checkpoint=True,
            require_trainer_state=False
        )

        checkpoint_path = epochs_access.get_checkpoint_path(
            training_session_id=checkpoint_directory,
            epoch_id=epoch_id
        )
        
        training_model = ModelAccess(script_factory).get_training_model(
            graph_spec.to_dict(),  # TODO: F/E needs to send ID
            checkpoint_path=checkpoint_path
        )

        return cls(training_model)

    def run_inference(self, data_iterator, return_inputs=False):
        """Runs inference through all the samples
        Args:
            dataLoader: Data
        Returns:
            outputs: model inputs(optional, returns empty list if set to false) and Dict of labels and model outputs
        """
        inputs = []
        targets = []
        outputs = []
        self._counter = 0
        for input_,target in data_iterator:
            if self._stopped:
                break
            else:
                output,_ = self._model.predict(input_) #* running in inferene mode
                if return_inputs:
                    inputs.append(input_)
                outputs.append(output)
                targets.append(target)
                self._counter += 1
        return inputs, {'outputs':outputs, 'targets':targets}

    def stop(self):
        self._stopped = True

    @property
    def num_samples_inferred(self):
        return self._counter
