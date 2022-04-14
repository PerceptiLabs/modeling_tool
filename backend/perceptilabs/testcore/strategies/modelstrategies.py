import tensorflow as tf
import numpy as np
import os
from abc import ABC, abstractmethod
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.epochs import EpochsAccess
import perceptilabs.utils as utils


class LoadInferenceModel:
    def __init__(self, model, return_inputs, return_outputs):
        self._model = model
        self._stopped = False
        self._inputs = None
        self._outputs = None
        self._return_inputs = return_inputs
        self._return_outputs = return_outputs

    @property
    def model(self):
        return self._model

    def run_inference(self, data_iterator):
        for _ in self.run_inference_stepwise(data_iterator):
            pass

        return self.model_inputs, self.model_outputs

    def run_inference_stepwise(self, data_iterator):
        """Runs inference through all the samples
        Args:
            dataLoader: Data
        Returns:
            outputs: model inputs(optional, returns empty list if set to false) and Dict of labels and model outputs
        """
        if self._return_inputs or self._return_outputs:
            inputs = []
            targets = []
            outputs = []
            self._counter = 0

            for input_, target in data_iterator.batch(1):
                if self._stopped:
                    break
                else:
                    output, _ = self._model.predict(
                        input_
                    )  # * running in inferene mode

                    if self._return_inputs:
                        inputs.append(input_)

                    if self._return_outputs:
                        outputs.append(output)
                        targets.append(target)

                    self._counter += 1
                yield

            self._inputs = inputs
            self._outputs = {"outputs": outputs, "targets": targets}
        else:
            self._inputs = {}
            self._outputs = {}

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
