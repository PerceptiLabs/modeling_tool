from abc import ABC, abstractmethod

# TODO: docs
# TODO: add to included

class TrainingStatsTracker(ABC):
    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def save(self):
        raise NotImplementedError


    
