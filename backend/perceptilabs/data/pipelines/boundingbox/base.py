import numpy as np
import tensorflow as tf

from perceptilabs.data.pipelines.base import PipelineBuilder, BasePipeline
from perceptilabs.data.pipelines.boundingbox.preprocessing import (
    BoundingBoxPreprocessing,
)


class BoundingBoxPipelineBuilder(PipelineBuilder):
    _loader_class = None
    _augmenter_class = None
    _preprocessing_class = BoundingBoxPreprocessing
    _postprocessing_class = None

    def _compute_processing_metadata(
        self, preprocessing, dataset, on_status_updated=None
    ):
        preprocessing_metadata = BoundingBoxPreprocessing.compute_metadata(
            preprocessing, dataset, on_status_updated=on_status_updated
        )
        return preprocessing_metadata, {}
