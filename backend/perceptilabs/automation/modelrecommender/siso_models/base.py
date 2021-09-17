# TODO: update docstrings w/ dataloader
from abc import ABC, abstractmethod
from perceptilabs.graph.builder import GraphSpecBuilder


class SISOModelBlueprint(ABC):
    @abstractmethod
    def build(self, builder, input_feature_name, target_feature_name, input_feature_spec, target_feature_spec, data_loader=None):
        """ Adds Single Input Single Output(SISO) model to the graph spec builder

        Arguments:
            graph_spec_builder: the entity used to construct the final graph
            input_feature_name: name of the input feature
            target_feature_name: name of the target feature
            input_feature_spec: properties of the input feature
            target_feature_spec: properties of the target feature
        """
        raise NotImplementedError

