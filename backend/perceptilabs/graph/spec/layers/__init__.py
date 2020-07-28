from perceptilabs.graph.spec.layers.base import sanitize_name, LayerSpec, LayerSpecBuilder, ParamSpec, DummyBuilder, DummySpec

from perceptilabs.graph.spec.layers.datadata import DataDataBuilder
from perceptilabs.graph.spec.layers.processreshape import ProcessReshapeBuilder
from perceptilabs.graph.spec.layers.processonehot import ProcessOneHotBuilder
from perceptilabs.graph.spec.layers.deeplearningfc import DeepLearningFcBuilder
from perceptilabs.graph.spec.layers.trainclassification import TrainClassificationBuilder
from perceptilabs.graph.spec.layers.deeplearningconv import DeepLearningConvBuilder


class InvalidLayerBuilder(Exception):
    pass


def get_layer_builder(type_: str):
    assert isinstance(type_, str)
    
    if type_ == 'DataData':
        return DataDataBuilder()
    elif type_ == 'ProcessReshape':
        return ProcessReshapeBuilder()
    elif type_ == 'DeepLearningFC':
        return DeepLearningFcBuilder()
    elif type_ == 'ProcessOneHot':
        return ProcessOneHotBuilder()
    elif type_ == 'TrainNormal':
        return TrainClassificationBuilder()
    elif type_ == 'DeepLearningConv':
        return DeepLearningConvBuilder()
    else:
        return DummyBuilder()        
        
