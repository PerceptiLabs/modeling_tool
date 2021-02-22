# TODO: add to included files
# TODO: docs
from dataclasses import dataclass
from typing import Dict
import numpy as np

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.trainer.stats.base import TrainingStatsTracker


@dataclass(frozen=True)
class TargetStats:
    graph_spec: GraphSpec
    targets_batch: Dict[str, np.ndarray]  # Dict[feature_name, target values]

    def get_value_by_layer_id(self, layer_id: str):
        """ Return a sample from the batch for a given layer ID """
        try:
            layer_spec = self.graph_spec[layer_id]        
            batch = self.targets_batch[layer_spec.feature_name]
            value = batch[-1]
        except:
            value = 0.0
        finally:
            return value


class TargetStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self.graph_spec = None
        self.targets_batch = {}
    
    def update(self, **kwargs):
        self.graph_spec = kwargs['graph_spec']
        self.targets_batch = kwargs['targets_batch']

    def save(self):
        """ Save the tracked values into a TrainingStats object """        
        evaluated_batch = {}
        
        for feature_name, feature_batch in self.targets_batch.items():
            array = feature_batch.numpy()
            array.setflags(write=False)
            evaluated_batch[feature_name] = array
            
        return TargetStats(self.graph_spec, evaluated_batch)

