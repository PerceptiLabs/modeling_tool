import tensorflow as tf

from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.accuracy import AccuracyStatsTracker
from perceptilabs.stats.iou import IouStatsTracker
from perceptilabs.layers.iooutput.stats.categorical import CategoricalOutputStats
from perceptilabs.layers.iooutput.stats.image import ImageOutputStats


def should_use_categorical(datatype):
    # TODO: remove this method when we implement a separate view for numerical
    return datatype in ['categorical', 'numerical']
    

class OutputStatsTracker(TrainingStatsTracker):
    def __init__(self, datatype):
        self._datatype = datatype
        
        if should_use_categorical(self._datatype):
            self._accuracy_tracker = AccuracyStatsTracker()
            self._predictions = tf.constant([0.0])
            self._targets = tf.constant([0.0])
        elif self._datatype == 'image':
            self._iou_tracker = IouStatsTracker()
            self._predictions = tf.constant([0.0])
            self._targets = tf.constant([0.0])

    def update(self, **kwargs):
        if should_use_categorical(self._datatype):        
            self._accuracy_tracker.update(**kwargs)
            self._predictions = kwargs['predictions_batch']
            self._targets = kwargs['targets_batch']
        elif self._datatype == 'image':        
            self._iou_tracker.update(**kwargs)
            self._predictions = kwargs['predictions_batch']
            self._targets = kwargs['targets_batch']
            
    def save(self):
        """ Save the tracked values into a TrainingStats object """
        if should_use_categorical(self._datatype):                
            return CategoricalOutputStats(
                accuracy=self._accuracy_tracker.save(),
                predictions=self._predictions.numpy(),
                targets=self._targets.numpy()                
            )
        elif self._datatype == 'image':
            return ImageOutputStats(
                iou=self._iou_tracker.save(),
                predictions=self._predictions.numpy(),
                targets=self._targets.numpy()                
            )
