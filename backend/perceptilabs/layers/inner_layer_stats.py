from abc import ABC, abstractmethod
import pickle
import numpy as np

from perceptilabs.stats import GradientStatsTracker

from perceptilabs.layers.processgrayscale.stats import GrayscaleOutputStats
from perceptilabs.layers.processonehot.stats import OneHotOutputStats
from perceptilabs.layers.mathsoftmax.stats import SoftmaxOutputStats
from perceptilabs.layers.mathargmax.stats import ArgmaxOutputStats
from perceptilabs.layers.processreshape.stats import ReshapeOutputStats
from perceptilabs.layers.processrescale.stats import RescaleOutputStats
from perceptilabs.layers.mathmerge.stats import MergeOutputStats
from perceptilabs.layers.layercustom.stats import LayerCustomOutputStats
from perceptilabs.layers.pretrainedvgg16.stats import VGG16OutputStats
from perceptilabs.layers.pretrainedmobilenetv2.stats import MobileNetV2OutputStats
from perceptilabs.layers.pretrainedinceptionv3.stats import InceptionV3OutputStats
from perceptilabs.layers.pretrainedresnet50.stats import ResNet50OutputStats
from perceptilabs.layers.deeplearningfc.stats import FCOutputStats
from perceptilabs.layers.deeplearningconv.stats import ConvOutputStats
from perceptilabs.layers.deeplearningrecurrent.stats import RecurrentOutputStats
from perceptilabs.layers.unet.stats import UnetOutputStats

class InnerLayersStatsTracker(ABC):

    def __init__(self, layers):
        self.layers = layers
        self.layer_outputs = {}
        self.layer_trainables = {}
        self.gradients_tracker = GradientStatsTracker()

    def update(self, **kwargs):
        self.gradients_tracker.update(**kwargs)

        outputs = kwargs['outputs']
        for layer_id in self.layers.keys():
            self.layer_outputs[layer_id] = {
                name: tensor.numpy()
                for name, tensor in outputs[layer_id].items()
            }

        trainables_by_layer = kwargs['trainables_by_layer']
        for layer_id in trainables_by_layer.keys():
            self.layer_trainables[layer_id] = {
                name: tensor.numpy()
                for name, tensor in trainables_by_layer[layer_id].items()
            }

    def save(self):
        """ Save the tracked values into the corresponding layer stats object """
        gradient_stats = self.gradients_tracker.save()
        stats = {}
        for id_ in self.layers.keys():
            type_ = self.layers[id_]
            outputs = self.get_layer_output(id_)
            weights = self.get_layer_weights(id_)
            bias = self.get_layer_bias(id_)
            gradients = self.get_layer_gradients(id_, gradient_stats)
            stats_object = self.get_inner_layer_stats_object(type_, weights, bias, outputs, gradients)
            stats[id_] = stats_object
        return stats

    def get_layer_output(self, layer_id, output_variable='output'):
        """ Gets the output batch of a layer

        Arguments:
            layer_id: the layer id
            output_variable: which variable to fetch from the output dict
        Returns:
            A numpy array (or None if the layer/variable doesnt exist)
        """
        try:
            output_batch = self.layer_outputs[layer_id][output_variable]
            return output_batch
        except KeyError as e:
            return None

    def get_layer_weights(self, layer_id):
        """ Get the weights associated with a layer """
        try:
            value = self.layer_trainables[layer_id]['weights']
            return value
        except KeyError as e:
            return None

    def get_layer_bias(self, layer_id):
        """ Get the bias associated with a layer """
        try:
            value = self.layer_trainables[layer_id]['bias']
            return value
        except KeyError as e:
            return None

    def get_layer_gradients(self, layer_id, gradient_stats):
        """ Get the gradients of a layer

        Arguments:
            layer_id: the layer id
            gradient_stats: one of minimum, maximum and average
        """
        minimum = gradient_stats.get_minimum_by_layer_id(layer_id)
        average = gradient_stats.get_average_by_layer_id(layer_id)
        maximum = gradient_stats.get_maximum_by_layer_id(layer_id)
        return {'Min': minimum,
                'Max': maximum,
                'Average': average }


    def get_inner_layer_stats_object(self, layer_type, weights, bias, outputs, gradients):
        if layer_type == 'UNet':
            return UnetOutputStats(weights, bias, outputs, gradients)
        elif layer_type == 'ProcessGrayscale':
            return GrayscaleOutputStats(outputs)
        elif layer_type == 'ProcessOneHot':
            return OneHotOutputStats(outputs)
        elif layer_type == 'MathSoftmax':
            return SoftmaxOutputStats(outputs)
        elif layer_type == 'MathArgmax':
            return ArgmaxOutputStats(outputs)
        elif layer_type == 'ProcessReshape':
            return ReshapeOutputStats(outputs)
        elif layer_type == 'ProcessRescale':
            return RescaleOutputStats(outputs)
        elif layer_type == 'MathMerge':
            return MergeOutputStats(outputs)
        elif layer_type == 'LayerCustom':
            return LayerCustomOutputStats(outputs)
        elif layer_type == 'PreTrainedVGG16':
            return VGG16OutputStats(weights, bias, outputs, gradients)
        elif layer_type == 'PreTrainedMobileNetV2':
            return MobileNetV2OutputStats(weights, bias, outputs, gradients)
        elif layer_type == 'PreTrainedInceptionV3':
            return InceptionV3OutputStats(weights, bias, outputs, gradients)
        elif layer_type == 'PreTrainedResNet50':
            return ResNet50OutputStats(weights, bias, outputs, gradients)
        elif layer_type == 'DeepLearningFC':
            return FCOutputStats(weights, bias, outputs, gradients)
        elif layer_type == 'DeepLearningConv':
            return ConvOutputStats(weights, bias, outputs, gradients)
        elif layer_type == 'DeepLearningRecurrent':
            return RecurrentOutputStats(outputs)

    def __eq__(self, other):
        return(
            self.gradients_tracker == other.gradients_tracker and
            self.layer_outputs == other.layer_outputs and
            self.layer_trainables == other.layer_trainables
        )


    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)