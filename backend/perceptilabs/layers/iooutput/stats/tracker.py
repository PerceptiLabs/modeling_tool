import tensorflow as tf

from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.accuracy import AccuracyStatsTracker
from perceptilabs.stats.loss import LossStatsTracker
from perceptilabs.stats.iou import IouStatsTracker
from perceptilabs.stats.r_squared import RSquaredStatsTracker
from perceptilabs.stats.mae import MeanAbsoluteErrorStatsTracker
from perceptilabs.stats.multiclass_matrix import MultiClassMatrixStatsTracker

from perceptilabs.layers.iooutput.stats.categorical import CategoricalOutputStats
from perceptilabs.layers.iooutput.stats.image import ImageOutputStats
from perceptilabs.layers.iooutput.stats.numerical import NumericalOutputStats


def should_use_categorical(datatype):
    # TODO: remove this method when we implement a separate view for numerical
    return datatype in ['categorical', 'binary']
    

class OutputStatsTracker(TrainingStatsTracker):
    def __init__(self, datatype):
        self._datatype = datatype

        self._loss_tracker = LossStatsTracker()            
        
        if should_use_categorical(self._datatype):
            self._accuracy_tracker = AccuracyStatsTracker()
            self._multiclass_matrix_tracker = MultiClassMatrixStatsTracker()   
            self._predictions = tf.constant([0.0])
            self._targets = tf.constant([0.0])
        elif self._datatype == 'image':
            self._iou_tracker = IouStatsTracker()
            self._predictions = tf.constant([0.0])
            self._targets = tf.constant([0.0])
        elif self._datatype == 'numerical':
            self._r_squared_tracker = RSquaredStatsTracker()
            self._mae_tracker = MeanAbsoluteErrorStatsTracker()
            self._predictions = tf.constant([0.0])
            self._targets = tf.constant([0.0])

    def update(self, **kwargs):
        self._loss_tracker.update(**kwargs)
        
        if should_use_categorical(self._datatype):        
            self._accuracy_tracker.update(**kwargs)
            self._multiclass_matrix_tracker.update(**kwargs)
            self._predictions = kwargs['predictions_batch']
            self._targets = kwargs['targets_batch']
        elif self._datatype == 'image':        
            self._iou_tracker.update(**kwargs)
            self._predictions = kwargs['predictions_batch']
            self._targets = kwargs['targets_batch']
        elif self._datatype == 'numerical':
            self._r_squared_tracker.update(**kwargs)
            self._mae_tracker.update(**kwargs)
            self._predictions = kwargs['predictions_batch']
            self._targets = kwargs['targets_batch']
            
    def save(self):
        """ Save the tracked values into a TrainingStats object """
        if should_use_categorical(self._datatype): 
            return CategoricalOutputStats(
                accuracy=self._accuracy_tracker.save(),
                loss=self._loss_tracker.save(),                
                predictions=self._predictions.numpy(),
                multiclass_matrix=self._multiclass_matrix_tracker.save(),
                targets=self._targets.numpy()                
            )
        elif self._datatype == 'image':
            return ImageOutputStats(
                loss=self._loss_tracker.save(),                                
                iou=self._iou_tracker.save(),
                predictions=self._predictions.numpy(),
                targets=self._targets.numpy()                
            )
        elif self._datatype == 'numerical':
            return NumericalOutputStats(
                loss=self._loss_tracker.save(),                                
                r_squared=self._r_squared_tracker.save(),
                mae=self._mae_tracker.save(),
                predictions=self._predictions.numpy(),
                targets=self._targets.numpy()                
            )
