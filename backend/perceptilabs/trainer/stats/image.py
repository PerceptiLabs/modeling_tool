from dataclasses import dataclass
from typing import Tuple

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.trainer.stats.base import TrainingStatsTracker
from perceptilabs.trainer.stats.iou import IouStatsTracker, IouStats
from perceptilabs.trainer.stats.loss import LossStatsTracker, LossStats



@dataclass(frozen=True)
class ImageOutputStats:
    iou: IouStats = None
    loss: LossStats = None


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

