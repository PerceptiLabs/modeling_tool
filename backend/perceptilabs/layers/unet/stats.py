import numpy as np

from perceptilabs.stats.base import TrainingStats, PreviewStats
from perceptilabs.createDataObject import createDataObject
from perceptilabs.stats.utils import create_data_object_for_list_of_1D_arrays

class UnetOutputStats(TrainingStats):
    def __init__(self, weights, bias, outputs, gradients):
        self.outputs = outputs
        self.weights = weights
        self.bias = bias
        self.gradients = gradients

    def get_data_objects(self, view):
        data_objects = {}
        if view=="Weights&Output":
            data_objects.update(self._get_weights_and_outputs())
        if view=="Bias":
            data_objects.update(self._get_bias())
        if view=="Gradients":
            data_objects.update(self._get_gradients())
        return data_objects

    def _get_weights_and_outputs(self):
        weights=self.weights
        Wshapes=weights.shape

        if len(Wshapes)==3:
            weights=np.expand_dims(np.average(weights[:,:,-1],1),axis=0)
        elif len(Wshapes)==4:
            weights=np.average(weights[:,:,:,-1],2)
        elif len(Wshapes)==5:
            weights=np.average(weights[:,:,:,:,-1],3)

        output = self.outputs[-1]
        dataObjWeights = createDataObject([weights], type_list=['heatmap'])
        dataObjOutput = createDataObject([output], type_list=['mask'])

        obj = {"Weights":dataObjWeights, "Output": dataObjOutput}
        return obj

    def _get_bias(self):
        b = self.bias
        dataObj = create_data_object_for_list_of_1D_arrays(
            values=[b],
            object_name='Bias'
        )
        return dataObj

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


class UnetPreviewStats(PreviewStats):

    def get_preview_content(self, sample):
        sample_array = np.asarray(sample)
        sample_layer_shape = sample_array.shape
        layer_sample_data_points = int(np.prod(sample_layer_shape))
        sample_data = [sample_array]
        type_list = ['mask']
        return sample_data, sample_layer_shape, layer_sample_data_points, type_list

