from typing import Dict
import numpy as np

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.stats.base import TrainingStatsTracker


class SampleStats:
    """ Used for tracking Input/Target/Prediction values. 

    There is one input value per IoInput layer and there is one target/prediction pair per IoOutput layer. This class contains utility methods to help accessing these values using the layer ID.
    """

    def __init__(self, id_to_feature, sample_batch):
        self.id_to_feature = id_to_feature
        self.sample_batch = sample_batch

    def __eq__(self, other):
        if self.id_to_feature != other.id_to_feature:
            return False

        for (name1, value1), (name2, value2) in zip(self.sample_batch.items(), other.sample_batch.items()):
            if name1 != name2:
                return False

            if np.any(value1 != value2):
                return False

        return True

    def get_sample_by_layer_id(self, layer_id: str):
        """ Return a sample from the batch for a given layer ID """        
        try:
            feature_name = self.id_to_feature[layer_id]
            batch = self.sample_batch[feature_name]
            value = batch[-1]
        except:
            value = 0.0
        finally:
            return value

    def get_batch_average(self, layer_id: str):
        """ Return the average sample in the batch """
        try:
            feature_name = self.id_to_feature[layer_id]            
            batch = self.sample_batch[feature_name]
            average_sample = np.average(batch, axis=0)
        except Exception as e:
            average_sample = 0.0
        finally:
            return average_sample

    def get_arbitrary_sample(self):
        """ Get an arbitrary sample from an arbitrary layer """
        # TODO: create story to remove this method
        batch = next(iter(self.sample_batch.values()), [0.0])
        value = batch[-1]
        return value        


class SampleStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self.id_to_feature = {}
        self.sample_batch = {}
    
    def update(self, **kwargs):
        """ Update the tracked samples """
        self.id_to_feature = kwargs['id_to_feature']
        self.sample_batch = kwargs['sample_batch']

    def save(self):
        """ Save the tracked values into a TrainingStats object """                
        evaluated_batch = {}
        
        for feature_name, feature_batch in self.sample_batch.items():
            array = feature_batch.numpy()
            array.setflags(write=False)
            evaluated_batch[feature_name] = array
            
        return SampleStats(self.id_to_feature, evaluated_batch)

    def __eq__(self, other):
        if self.id_to_feature != other.id_to_feature:
            return False

        for (name1, value1), (name2, value2) in zip(self.sample_batch.items(), other.sample_batch.items()):
            if name1 != name2:
                return False

            if np.any(value1 != value2):
                return False

        return True

    
