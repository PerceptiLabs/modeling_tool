from abc import ABC, abstractmethod

# TODO: docs

class TrainingStats(ABC):
    @abstractmethod
    def get_data_objects(self):
        raise NotImplementedError


class OutputStats(TrainingStats):
    @abstractmethod
    def get_summary(self):
        """ Gets the stats summary for this layer 

        Returns:
            A dictionary with metric names and values (floats)
        """        
        raise NotImplementedError
    
    
class TrainingStatsTracker(ABC):
    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def save(self):
        raise NotImplementedError


    
