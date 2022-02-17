import tensorflow as tf
import numpy as np
import os
from abc import ABC, abstractmethod
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.epochs import EpochsAccess
import perceptilabs.utils as utils


class LoadInferenceModel():
    def __init__(self, model):
        self._model = model
        self._stopped = False
        self._inputs = None
        self._outputs = None

    @classmethod
    def from_checkpoint(cls, call_context, model_access, epochs_access, training_session_id, graph_spec, data_loader):
        """
        load model from checkpoint and graphspec
        """
        epoch_id = epochs_access.get_latest(
            call_context,
            training_session_id=training_session_id,
            require_checkpoint=True,
            require_trainer_state=False
        )

        checkpoint_path = epochs_access.get_checkpoint_path(
            call_context,
            training_session_id=training_session_id,
            epoch_id=epoch_id
        )

        training_model = TrainingModel.from_graph_spec(
            graph_spec, checkpoint_path=checkpoint_path)

        return cls(training_model)

    def run_inference(self, data_iterator, return_inputs=False):
        for _ in self.run_inference_stepwise(data_iterator, return_inputs=return_inputs):
            pass

        return self.model_inputs, self.model_outputs

    def run_inference_stepwise(self, data_iterator, return_inputs=False):
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
            yield

        self._inputs = inputs
        self._outputs = {'outputs':outputs, 'targets':targets}

    @property
    def model_inputs(self):
        return self._inputs

    @property
    def model_outputs(self):
        return self._outputs

    def stop(self):
        self._stopped = True

    @property
    def num_samples_inferred(self):
        return self._counter
