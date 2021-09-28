import numpy as np

from perceptilabs.createDataObject import createDataObject
from perceptilabs.stats.base import PreviewStats, TrainingStats
from perceptilabs.stats.utils import create_data_object_for_list_of_1D_arrays


class InceptionV3OutputStats(TrainingStats):
    def __init__(self, weights, bias, outputs, gradients):
        self.outputs = outputs
        self.weights = weights
        self.bias = bias
        self.gradients = gradients

    def get_data_objects(self, view):
        data_objects = {}
        if view=="Weights&Bias":
            data_objects.update(self._get_weights_and_bias())
        if view=="Output":
            data_objects.update(self._get_output())
        if view=="Gradients":
            data_objects.update(self._get_gradients())
        return data_objects

    def _get_weights_and_bias(self):
        weights = self.weights
        weights = np.squeeze(weights)
        w_shape = weights.shape
        if len(w_shape) == 4:
            weights = weights[-1,-1,:,:]
        elif len(w_shape) == 3:
            weights = weights[-1,:,:]
        weights = np.mean(weights, axis=1)
        dataObjectWeights = createDataObject([weights], type_list=['line'])

        bias = self.bias
        if bias is not None:
            dataObjectBias = createDataObject([bias], type_list=['line'])
            output = {"Bias": dataObjectBias, "Weights": dataObjectWeights}
        else:
            output = {"Weights": dataObjectWeights}
        return output

    def _get_output(self):
        output = self.outputs[-1]
        dataObject = createDataObject([output])
        obj = {"Output": dataObject}
        return obj

    def _get_gradients(self):
        minD = self.gradients["Min"]
        maxD = self.gradients["Max"]
        avD = self.gradients["Average"]

        dataObj = create_data_object_for_list_of_1D_arrays(
            values=[minD, maxD, avD],
            name_list=['Min', 'Max', 'Average'],
            object_name='Gradients'
        )
        return dataObj

    def __eq__(self, other):
        return (
            np.all(self.outputs == other.outputs) and
            np.all(self.weights == other.weights) and
            np.all(self.bias == other.bias)
        )
