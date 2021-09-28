import numpy as np

from perceptilabs.createDataObject import createDataObject
from perceptilabs.stats.base import PreviewStats, TrainingStats


class RecurrentOutputStats(TrainingStats):
    def __init__(self, outputs):
        self.outputs = outputs

    def get_data_objects(self, view = None):
        data_objects = {}
        data_objects.update(self._get_output())
        return data_objects

    def _get_output(self):
        output = self.outputs[-1]
        dataObject = createDataObject([output])
        obj = {"Output": dataObject}
        return obj

    def __eq__(self, other):
        return (
            np.all(self.outputs == other.outputs)
        )

