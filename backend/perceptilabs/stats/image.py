from typing import Tuple

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.stats.base import TrainingStatsTracker
from perceptilabs.stats.iou import IouStatsTracker, IouStats
from perceptilabs.stats.loss import LossStatsTracker, LossStats



class ImageOutputStats:
    def __init__(self, iou=None, loss=None):
        self.iou = iou
        self.loss = loss
        

class ImageOutputStatsTracker(TrainingStatsTracker):
    def __init__(self):
        self._iou_tracker = IouStatsTracker()
        self._loss_tracker = LossStatsTracker()  

    def update(self, **kwargs):
        self._iou_tracker.update(**kwargs)
        self._loss_tracker.update(**kwargs)
        
    def save(self):
        """ Save the tracked values into a TrainingStats object """

        iou = self._iou_tracker.save()
        loss = self._loss_tracker.save()
        
        return ImageOutputStats(iou, loss)

