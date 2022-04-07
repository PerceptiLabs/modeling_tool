from abc import ABC, abstractmethod
import pickle
import numpy as np


class TrainingStats(ABC):
    def get_data_objects(self, view=None):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError


class OutputStats(TrainingStats):
    @abstractmethod
    def get_summary(self):
        """Gets the stats summary for this layer

        Returns:
            A dictionary with metric names and values (floats)
        """
        raise NotImplementedError

    @abstractmethod
    def get_end_results(self):
        raise NotImplementedError


class PreviewStats:
    def get_preview_content(self, sample):
        sample_array = np.asarray(sample)
        sample_layer_shape = sample_array.shape

        type_list = None
        sample_data = [self._reduce_to_2d(sample_array).squeeze()]

        return sample_data, sample_layer_shape, type_list

    def _reduce_to_2d(self, data):
        data_shape = np.shape(np.squeeze(data))

        is_scalar = len(data_shape) <= 1
        is_vector = len(data_shape) == 2
        is_image = len(data_shape) == 3 and (data_shape[-1] == 3 or data_shape[-1] == 1)

        if is_scalar or is_vector or is_image:
            return data
        else:
            return self._reduce_to_2d(data[..., -1])


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
