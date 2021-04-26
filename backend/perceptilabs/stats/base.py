from abc import ABC, abstractmethod

# TODO: docs

class TrainingStats(ABC):
    @abstractmethod
    def get_data_objects(self):
        raise NotImplementedError

    
class TrainingStatsTracker(ABC):
    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def save(self):
        raise NotImplementedError


    
