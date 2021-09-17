from abc import ABC, abstractmethod
import pickle

# TODO: docs

class TrainingStats(ABC):
    def get_data_objects(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError


class OutputStats(TrainingStats):
    @abstractmethod
    def get_summary(self):
        """ Gets the stats summary for this layer

        Returns:
            A dictionary with metric names and values (floats)
        """
        raise NotImplementedError

class PreviewStats(ABC):
    def get_preview_content(self):
        raise NotImplementedError
class TrainingStatsTracker(ABC):
    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def save(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)

