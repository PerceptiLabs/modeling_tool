from abc import ABC, abstractmethod
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.base import FeatureSpec


class DecoderBlueprint(ABC):
    @abstractmethod
    def build(self, builder: GraphSpecBuilder, feature_name: str, feature_spec: FeatureSpec) -> str:
        """ Adds an decoder to the graph spec builder
        
        Arguments:
            graph_spec_builder: the entity used to construct the final graph
            feature_name: name of the current feature
            feature_spec: properties of the feature
        Returns:
            the ID of the decoders first layer
        """
        raise NotImplementedError
    
