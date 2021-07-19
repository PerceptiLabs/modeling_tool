# TODO: update docstrings w/ dataloader
from abc import ABC, abstractmethod
from perceptilabs.graph.builder import GraphSpecBuilder


class EncoderBlueprint(ABC):
    @abstractmethod
    def build(self, builder, feature_name, feature_spec, data_loader=None):
        """ Adds an encoder to the graph spec builder
        
        Arguments:
            graph_spec_builder: the entity used to construct the final graph
            feature_name: name of the current feature
            feature_spec: properties of the feature
        Returns:
            the ID of the encoders final layer
        """
        raise NotImplementedError
    
