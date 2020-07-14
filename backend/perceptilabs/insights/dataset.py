import numpy as np
from typing import Dict


class DatasetDistribution:
    def __init__(self):
        self._running_sum = {}
        self._running_squared_sum = {}
        self._current_max = {}
        self._current_min = {}
        self._count = 0

    def draw_sample(self, batches: Dict[str, np.ndarray]):
        """ A dict of dataset minibatches (from the same iteration) """
        first_batches = self._count == 0
        
        for layer_id, batch in batches.items():
            batch = batch.astype(np.longdouble) # To prevent overflow
            
            if first_batches:
                self._draw_first(layer_id, batch)
            else:
                self._draw_next(layer_id, batch)
            self._count += len(batch)
                
    def _draw_first(self, layer_id, batch):
        self._running_sum[layer_id] = batch.sum(axis=0)
        self._running_squared_sum[layer_id] = np.square(batch).sum(axis=0)
        
        # Select the most extreme samples. E.g., brightest/darkest
        average_element = batch.mean(axis=tuple(range(1, batch.ndim)))
        idx_max = np.argmax(average_element)
        idx_min = np.argmin(average_element)
        
        self._current_max[layer_id] = batch[idx_max]
        self._current_min[layer_id] = batch[idx_min]

    def _draw_next(self, layer_id, batch):
        self._running_sum[layer_id] += batch.sum(axis=0)
        self._running_squared_sum[layer_id] += np.square(batch).sum(axis=0)

        # Select the most extreme samples. E.g., brightest/darkest                
        average_element = batch.mean(axis=tuple(range(1, batch.ndim)))                                                
        idx_max = np.argmax(average_element)
        idx_min = np.argmin(average_element)

        # Possibly replace existing
        self._current_max[layer_id] = batch[idx_max] if average_element[idx_max] > self._current_max[layer_id].mean() else self._current_max[layer_id]
        self._current_min[layer_id] = batch[idx_min] if average_element[idx_min] < self._current_min[layer_id].mean() else self._current_min[layer_id]

    @property
    def shape(self):
        shapes = {}

        for layer_id in self._running_sum:
            shapes[layer_id] = self._running_sum[layer_id].shape
        return shapes
    
    @property
    def sample_distribution(self):
        """ Mean and standard deviation.

        computed using: https://en.wikipedia.org/wiki/Standard_deviation#Identities_and_mathematical_properties 
        """
        
        means = {}
        stddevs = {}
        for layer_id in self._running_sum.keys():
            average_sample = self._running_sum[layer_id] / self._count
            average_squared_sample = self._running_squared_sum[layer_id] / self._count

            means[layer_id] = average_sample
            stddevs[layer_id] = np.sqrt(average_squared_sample - np.square(average_sample)) 
        return means, stddevs

    @property
    def sample_max(self):
        """ Returns the highest average element (i.e., brightest sample) """        
        return self._current_max

    @property
    def sample_min(self):
        """ Returns the lowest average element (i.e., darkest sample) """
        return self._current_min
    
    
            
            
            
        


    

    
    




