from abc import ABC, abstractmethod
import pickle
import time
import tensorflow as tf
import logging
import codecs
from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


def serialize(obj):
    return codecs.encode(pickle.dumps(obj), "base64").decode()


def deserialize(pickled):
    return pickle.loads(codecs.decode(pickled.encode(), "base64"))


class BasePipeline(tf.keras.Model):
    def __init__(self, preprocessing=None, metadata=None):
        super().__init__()

        self.preprocessing = preprocessing
        self.metadata = metadata or {}

    def get_config(self):
        return {
            'preprocessing': serialize(self.preprocessing),
            'metadata': serialize(self.metadata)
        }

    @classmethod
    def from_config(cls, config):
        return cls(
            preprocessing=deserialize(config['preprocessing']),
            metadata=deserialize(config['metadata'])
        )    


class IdentityPipeline(BasePipeline):
    def call(self, x):
        return x

    
class DefaultAugmenter(BasePipeline):
    def call(self, x):
        index, value = x
        return value    


class PipelineBuilder(ABC):
    def load_from_metadata(self, preprocessing, metadata):
        """ Returns (loader_step, augmenter_step, preprocessing_step, postprocessing_step) """
        
        loader_step = self._get_loader_step(preprocessing, metadata.get('loader'))
        augmenter_step = self._get_augmenter_step(preprocessing, metadata.get('augmenter'))
        preprocessing_step = self._get_preprocessing_step(preprocessing, metadata.get('preprocessing'))
        postprocessing_step = self._get_postprocessing_step(preprocessing, metadata.get('postprocessing'))
        return (loader_step, augmenter_step, preprocessing_step, postprocessing_step)

    def build_from_dataset(self, preprocessing, dataset):
        """ Use for testing only """
        dataset_size = len(dataset)        
        indices = tf.data.Dataset.from_tensor_slices(tf.range(dataset_size))
        indexed_dataset = tf.data.Dataset.zip((indices, dataset))  # This helps us map samples back
        return self.build_from_indexed_dataset(preprocessing, indexed_dataset)

    def build_from_indexed_dataset(self, preprocessing, indexed_dataset):
        t0 = time.perf_counter()
        loader_metadata = self._compute_loader_metadata(preprocessing, indexed_dataset.map(lambda index, value: value, num_parallel_calls=tf.data.AUTOTUNE))
        loader_step = self._get_loader_step(preprocessing, loader_metadata)
        loaded_dataset = indexed_dataset.map(lambda index, value: (index, loader_step(value)), num_parallel_calls=tf.data.AUTOTUNE)

        t1 = time.perf_counter()
        augmenter_metadata = self._compute_augmenter_metadata(preprocessing, loaded_dataset)
        augmenter_step = self._get_augmenter_step(preprocessing, augmenter_metadata)
        augmented_dataset = loaded_dataset.map(lambda index, value: augmenter_step((index, value)), num_parallel_calls=tf.data.AUTOTUNE)

        t2 = time.perf_counter()
        preprocessing_metadata, postprocessing_metadata = self._compute_processing_metadata(preprocessing, augmented_dataset)
        preprocessing_step = self._get_preprocessing_step(preprocessing, preprocessing_metadata)
        postprocessing_step = self._get_postprocessing_step(preprocessing, postprocessing_metadata)
        
        t3 = time.perf_counter()
        logger.info(f"Built pipelines. Durations for loader={t1-t0:.3f}s, augmenter={t2-t1:.3f}s, pre- and post-processing={t3-t2:.3f}s")        
        
        return (loader_step, augmenter_step, preprocessing_step, postprocessing_step)

    def _get_loader_step(self, preprocessing, metadata):
        cls = self._loader_class or IdentityPipeline
        return cls(preprocessing=preprocessing, metadata=metadata)

    def _get_augmenter_step(self, preprocessing, metadata):
        cls = self._augmenter_class or DefaultAugmenter
        return cls(preprocessing=preprocessing, metadata=metadata)

    def _get_preprocessing_step(self, preprocessing, metadata):
        cls = self._preprocessing_class or IdentityPipeline
        return cls(preprocessing=preprocessing, metadata=metadata)
    
    def _get_postprocessing_step(self, preprocessing, metadata):
        cls = self._postprocessing_class or IdentityPipeline
        return cls(preprocessing=preprocessing, metadata=metadata)    
    
    @property
    @abstractmethod    
    def _loader_class(self):
        raise NotImplementedError        

    @property
    @abstractmethod
    def _augmenter_class(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def _preprocessing_class(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def _postprocessing_class(self):
        raise NotImplementedError    
    
    def _compute_loader_metadata(self, preprocessing, dataset):
        return {}

    def _compute_augmenter_metadata(self, preprocessing, indexed_dataset):
        return {}

    def _compute_processing_metadata(self, preprocessing, dataset):
        return {}, {}
    
    @property
    def has_loader(self):
        return self._loader_class is not None
    
