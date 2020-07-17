import numpy as np

from perceptilabs.aggregation.base import Aggregate


class AverageAggregate(Aggregate):
    def __init__(self, data, moving=False, window_size=None):
        self._data = data
        self._moving = moving
        self._window_size = window_size
        
    def _run_internal(self):
        value = np.average(self._data, axis=0)
        return value

    
class MaxAggregate(Aggregate):
    def __init__(self, data):
        self._data = data
        
    def _run_internal(self):
        value = np.amax(self._data, axis=0)
        return value

    
class MinAggregate(Aggregate):
    def __init__(self, data):
        self._data = data
        
    def _run_internal(self):
        value = np.amin(self._data, axis=0)
        return value
        
    
class SubtractAggregate(Aggregate):
    def __init__(self, x1, x2):
        self._x1 = x1
        self._x2 = x2
        
    def _run_internal(self):
        value = np.subtract(self._x1, self._x2).tolist()
        return value

    
class EpochFinalValue(Aggregate):
    def __init__(self, series, epochs):
        self._series = np.asarray(series)
        self._epochs = np.asarray(epochs)

    def _run_internal(self):
        end_of_epoch = self._epochs[:-1] != self._epochs[1:]
        end_of_epoch = np.hstack((end_of_epoch, np.array([True]))) # Include last iteration
        values = self._series[np.where(end_of_epoch)].tolist()
        return values


class Identity(Aggregate):
    def __init__(self, x):
        self._x = x
        
    def _run_internal(self):
        return self._x

    
class ProcessWeights(Aggregate):
    def __init__(self, raw_weights):
        self._raw_weights = raw_weights
        
    def _run_internal(self):
        # TODO: implement downsampling 
        return self._raw_weights

