import numpy as np
import tensorflow as tf

from perceptilabs.data.pipelines.base import PipelineBuilder, BasePipeline
from perceptilabs.data.pipelines.image.loader import Loader
from perceptilabs.data.pipelines.image.augmenter import Augmenter
from perceptilabs.data.pipelines.image.preprocessing import ImagePreprocessing, MaskPreprocessing
from perceptilabs.data.pipelines.image.postprocessing import MaskPostprocessing


class ImagePipelineBuilder(PipelineBuilder):
    _loader_class = Loader
    _augmenter_class = Augmenter
    _preprocessing_class = ImagePreprocessing
    _postprocessing_class = None

    def _compute_loader_metadata(self, preprocessing, dataset):
        return Loader.compute_metadata(dataset, preprocessing)

    def _compute_augmenter_metadata(self, preprocessing, indexed_dataset):
        return Augmenter.compute_metadata(indexed_dataset, preprocessing)

    def _compute_processing_metadata(self, preprocessing, dataset, on_status_updated=None):
        preprocessing_metadata = ImagePreprocessing.compute_metadata(preprocessing, dataset, on_status_updated=on_status_updated)
        return preprocessing_metadata, {}



class MaskPipelineBuilder(PipelineBuilder):
    _loader_class = Loader
    _augmenter_class = Augmenter
    _preprocessing_class = MaskPreprocessing
    _postprocessing_class = MaskPostprocessing

    def _compute_loader_metadata(self, preprocessing, dataset):
        return Loader.compute_metadata(dataset, preprocessing)

    def _compute_augmenter_metadata(self, preprocessing, indexed_dataset):
        return Augmenter.compute_metadata(indexed_dataset, preprocessing)

    def _compute_processing_metadata(self, preprocessing, dataset, on_status_updated=None):
        preprocessing_metadata = MaskPreprocessing.compute_metadata(preprocessing, dataset, on_status_updated=on_status_updated)
        return preprocessing_metadata, {}

