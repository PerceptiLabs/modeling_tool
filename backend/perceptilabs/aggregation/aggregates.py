import numpy as np
from abc import ABC, abstractmethod

class Aggregate(ABC):
    @abstractmethod
    def _run_internal(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def num_inputs(self):
        raise NotImplementedError

    def run(self):
        try:
            result = self._run_internal()
        except:
            return None
        else:
            return result

class AverageAggregate(Aggregate):
    num_inputs = 1

    def __init__(self, data, moving=False, window_size=None):
        self._data = data
        self._moving = moving
        self._window_size = window_size
        
    def _run_internal(self):
        value = np.nanmean(self._data, axis=0)
        return value

    
class MaxAggregate(Aggregate):
    num_inputs = 1

    def __init__(self, data):
        self._data = data
        
    def _run_internal(self):
        value = np.nanmax(self._data, axis=0)
        return value

    
class MinAggregate(Aggregate):
    num_inputs = 1

    def __init__(self, data):
        self._data = data
        
    def _run_internal(self):
        value = np.nanmin(self._data, axis=0)
        return value
        
    
class SubtractAggregate(Aggregate):
    num_inputs = 2
    
    def __init__(self, x1, x2):
        self._x1 = x1
        self._x2 = x2
        
    def _run_internal(self):
        value = np.subtract(self._x1, self._x2)
        return value

    
class EpochFinalValue(Aggregate):
    num_inputs = 2

    def __init__(self, series, epochs):
        self._series = np.asarray(series)
        self._epochs = np.asarray(epochs)

    def _run_internal(self):
        end_of_epoch = self._epochs[:-1] != self._epochs[1:]
        end_of_epoch = np.hstack((end_of_epoch, np.array([True]))) # Include last iteration
        values = self._series[np.where(end_of_epoch)]
        return values


class Identity(Aggregate):
    num_inputs = 1

    def __init__(self, x):
        self._x = x
        
    def _run_internal(self):
        return np.array(self._x)

    
class ProcessWeights(Aggregate):
    num_inputs = 1

    def __init__(self, raw_weights):
        self._raw_weights = raw_weights
        
    def _run_internal(self):
        # TODO: implement downsampling 
        return self._raw_weights


class Transpose(Aggregate):
    num_inputs = 1
    
    def __init__(self, data):
        self._data = data
    
    def _run_internal(self):
        data_dims = np.array(self._data)
        dimensions = [x for x in range(len(data_dims.shape))]
        dimensions[-1], dimensions[-2] = dimensions[-2], dimensions[-1]
        
        value = data_dims.transpose(*dimensions)
        return value
