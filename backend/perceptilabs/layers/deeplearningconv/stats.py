import numpy as np

from perceptilabs.createDataObject import createDataObject
from perceptilabs.stats.base import PreviewStats

class ConvPreviewStats(PreviewStats):

    def get_preview_content(self, sample):
        sample_array = np.asarray(sample)
        sample_layer_shape = sample_array.shape
        layer_sample_data_points = int(np.prod(sample_layer_shape))
        sample_data = list()
        if np.all(sample_array) != None:
            for idx in range(sample_array.shape[-1]):
                sample_data.append(sample_array[:,:,idx])
        type_list = None
        return sample_data, sample_layer_shape, layer_sample_data_points, type_list

