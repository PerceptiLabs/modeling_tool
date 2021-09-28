import numpy as np

from perceptilabs.createDataObject import createDataObject
from perceptilabs.stats.base import PreviewStats, TrainingStats


class GrayscaleOutputStats(TrainingStats):
    def __init__(self, outputs):
        self.outputs = outputs

    def get_data_objects(self, view=None):
        data_objects = {}
        data_objects.update(self._get_output())
        return data_objects

    def _get_output(self):
        output = self.outputs[-1]

        if len(output.shape) == 3:
            if output.shape[-1] == 1:
                obj = createDataObject([output])
            else:
                obj = createDataObject([output[:,:,0]])
        elif len(output.shape)>3:
            obj = createDataObject([output[0]])
        else:
            obj = createDataObject([output])
        return {"Output":obj}


    def __eq__(self, other):
        return (
            np.all(self.outputs == other.outputs)
        )
