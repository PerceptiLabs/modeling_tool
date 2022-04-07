import tensorflow as tf
import numpy as np

from perceptilabs.createDataObject import create_data_object
from perceptilabs.stats.base import TrainingStatsTracker, TrainingStats


class InputStats(TrainingStats):
    def __init__(self, inputs):
        self._inputs = inputs

    @property
    def inputs(self):
        return self._inputs

    def __eq__(self, other):
        return np.all(self.inputs == other.inputs)

    def get_data_objects(self, view=None):
        batch = self._inputs
        sample = batch[-1]
        data_object = create_data_object([sample])
        return {"Data": data_object}


class InputStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._inputs = tf.constant([0.0])

    def update(self, **kwargs):
        self._inputs = kwargs["inputs_batch"]

    def save(self):
        """Save the tracked values into a TrainingStats object"""
        return InputStats(inputs=self._inputs.numpy())

    @property
    def inputs(self):
        return self._inputs

    def __eq__(self, other):
        return np.all(self.inputs == other.inputs)
