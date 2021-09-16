import os
import time
import copy
import logging
from abc import ABC, abstractmethod



import pandas as pd
import numpy as np
import tensorflow as tf
from typing import Dict

from perceptilabs.data.pipelines.base import IdentityPipeline
from perceptilabs.data.settings import DatasetSettings
import perceptilabs.data.pipelines as pipelines
import perceptilabs.data.utils as utils
from perceptilabs.data.settings import FeatureSpec
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


def validate_pipeline_arg(arg):
    valid_pipelines = ('all', 'loader')
    if arg not in valid_pipelines and arg is not None:
        raise ValueError(
            "Pipeline argument must be 'None' or one of: " + ", ".join(valid_pipelines) + f". Got: {arg}")
    
    
class DataLoader:
    def __init__(self, data_frame, dataset_settings, metadata=None, num_repeats=1):
        self._dataset_settings = dataset_settings
        self._data_frame = data_frame
        self._metadata = metadata
        self._num_repeats = num_repeats
        self._initialized = False        
        
    def ensure_initialized(self):
        if self._initialized:
            return self
        
        logger.info("Initializing data loader...")        
    
        self._training_set, self._validation_set, self._test_set = self._build_and_partition_data(
            self._data_frame, self._dataset_settings, self._num_repeats
        )
        if self._metadata is None:
            pipelines, self._metadata = self._build_pipelines(self._dataset_settings, self._training_set)
        else:
            pipelines = self._load_pipelines(self._dataset_settings, self._metadata)
        
        self._loader_pipelines = pipelines['loader']  # TODO: create a namedtuple instead?
        self._augmenter_pipelines = pipelines['augmenter']
        self._preprocessing_pipelines = pipelines['preprocessing']
        self._postprocessing_pipelines = pipelines['postprocessing']
        self._initialized = True
        logger.info("Data loader initialized")
        return self

    @classmethod
    def compute_metadata(cls, data_frame, dataset_settings, num_repeats=1):
        training_set, _, _ = cls._build_and_partition_data(
            data_frame, dataset_settings, num_repeats
        )
        _, metadata = cls._build_pipelines(dataset_settings, training_set)
        return metadata        

    @classmethod
    def _build_and_partition_data(cls, data_frame, dataset_settings, num_repeats):
        cls._validate_feature_specs(data_frame.columns, dataset_settings.used_feature_specs)
            
        if dataset_settings.file_path is not None:
            data_frame = cls._make_paths_absolute(data_frame, dataset_settings)
            
        full_dataset, full_dataset_size = cls._create_indexed_dataset(data_frame, dataset_settings)
        
        training_set, validation_set, test_set = cls._partition_dataset(
            full_dataset, full_dataset_size, dataset_settings.partitions
        )
        
        repeated_training_set = cls._repeat_dataset(
            training_set, count=num_repeats, index_offset=full_dataset_size  # TODO: num repeats should be a property of dataset_settings
        )

        if num_repeats == 1:
            logger.info(
                f"Built and partitioned TensorFlow dataset. "
                f"Size of training: {len(repeated_training_set)}, validation: {len(validation_set)}, test: {len(test_set)} "
            )
        else:
            logger.info(
                f"Built and partitioned TensorFlow dataset. "
                f"Effective size of training set: {len(repeated_training_set)}. Original size: {len(training_set)} repeated {num_repeats} times. "
                f"Size of validation: {len(validation_set)}, test: {len(test_set)}"
            )

        return repeated_training_set, validation_set, test_set

    @staticmethod
    def _repeat_dataset(original_dataset, count, index_offset=None):
        """ Repeats this dataset so each original value is seen count times. Adds an offset to the index value"""
        t0 = time.perf_counter()
        if count < 1:
            raise ValueError(f"Repeat count must be >= 1, got {count}")            
        
        original_size = len(original_dataset)
        if index_offset is None:
            index_offset = original_size

        current_dataset = original_dataset
        for _ in range(count - 1):
            current_dataset = current_dataset.concatenate(
                original_dataset.map(lambda index, value: (index + index_offset, value), num_parallel_calls=tf.data.AUTOTUNE)
            )
            index_offset += original_size
            
        logger.info(f"Repeated dataset {count} times. Duration: {time.perf_counter() - t0:.3f}s")
        return current_dataset

    @classmethod
    def _load_pipelines(cls, dataset_settings, metadata):
        feature_specs = dataset_settings.used_feature_specs
        
        pipelines = {
            'loader': {},
            'augmenter': {},
            'preprocessing': {},
            'postprocessing': {}
        }
        
        for feature_name, feature_spec in feature_specs.items():        
            builder = cls._get_pipeline_builder(feature_spec.datatype)
            feature_metadata = metadata[feature_name]

            loader, augmenter, preprocessing, postprocessing = \
                builder.load_from_metadata(feature_spec.preprocessing, feature_metadata)

            pipelines['loader'][feature_name] = loader
            pipelines['augmenter'][feature_name] = augmenter
            pipelines['preprocessing'][feature_name] = preprocessing
            pipelines['postprocessing'][feature_name] = postprocessing            

        logger.info(f"Loaded preprocessing pipelines from metadata.")            
        return pipelines

    @classmethod
    def _build_pipelines(cls, dataset_settings, training_set):
        feature_specs = dataset_settings.used_feature_specs

        import time
        #time.sleep(4)        
        

        loader_pipelines = {}
        augmenter_pipelines = {}        
        preprocessing_pipelines = {}
        postprocessing_pipelines = {}

        for feature_name, feature_spec in feature_specs.items():
            t0 = time.perf_counter()
            feature_training_set = training_set.map(
                lambda index, values: (index, values[feature_name]),
                num_parallel_calls=tf.data.AUTOTUNE
            )
            pipeline_builder = cls._get_pipeline_builder(feature_spec.datatype)

            loader_pipeline, augmenter_pipeline, preprocessing_pipeline, postprocessing_pipeline = \
                pipeline_builder.build_from_indexed_dataset(feature_spec.preprocessing, feature_training_set)
            loader_pipelines[feature_name] = loader_pipeline
            augmenter_pipelines[feature_name] = augmenter_pipeline            
            preprocessing_pipelines[feature_name] = preprocessing_pipeline
            postprocessing_pipelines[feature_name] = postprocessing_pipeline

            logger.info(f"Built pipelines for {feature_name}. Duration: {time.perf_counter() - t0:.3f}s")
        pipelines = {
            'loader': loader_pipelines,
            'augmenter': augmenter_pipelines,
            'preprocessing': preprocessing_pipelines,
            'postprocessing': postprocessing_pipelines
        }
            
        metadata = {}
        for feature_name, feature_spec in feature_specs.items():
            metadata[feature_name] = {
                step: dict(pipelines[step][feature_name].metadata)
                for step in pipelines.keys()
            }
            
        logger.info(f"Built preprocessing pipelines.")
        return pipelines, metadata

    @classmethod
    def from_dict(cls, dict_, metadata=None, num_repeats=1):
        """ Creates a DataLoader given a settings dict """
        dataset_settings = DatasetSettings.from_dict(dict_)
        return cls.from_settings(
            dataset_settings, metadata=metadata, num_repeats=num_repeats
        )

    @classmethod
    def from_settings(cls, dataset_settings, metadata=None, num_repeats=1):
        """ Creates a DataLoader given a settings dict """
        data_frame = pd.read_csv(dataset_settings.file_path)
        data_loader = cls(
            data_frame,
            dataset_settings,
            metadata=metadata,
            num_repeats=num_repeats
        )
        return data_loader

    @classmethod
    def from_features(cls, feature_specs, file_path, metadata=None, num_repeats=1):
        dataset_settings = DatasetSettings(feature_specs=feature_specs, file_path=file_path)
        return cls.from_settings(
            dataset_settings, metadata=metadata, num_repeats=num_repeats
        )

    def _select_columns_by_iotype(self, df, feature_specs, iotype):
        """ Selects input or output components from the dataframe """
        assert iotype in ['input', 'target']
        column_names = [name for name, feature_spec in feature_specs.items() if feature_spec.iotype==iotype]        
        return df[column_names]

    @staticmethod
    def _create_indexed_dataset(df, dataset_settings):
        t0 = time.perf_counter()
        feature_datasets = {}
        
        for feature_name in dataset_settings.used_feature_specs:
            feature_values = df[feature_name].values.tolist()  # Create a dataset for an individual column
            feature_datasets[feature_name] = tf.data.Dataset.from_tensor_slices(feature_values)

        dataset = tf.data.Dataset.zip(feature_datasets)
        
        dataset_size = len(df)        
        indices = tf.data.Dataset.from_tensor_slices(tf.range(dataset_size))
        indexed_dataset = tf.data.Dataset.zip((indices, dataset))  # This helps us map samples back to rows in the dataframe when debugging

        logger.info(f"Created indexed TensorFlow dataset. Duration: {time.perf_counter() - t0:.3f}s")
        return indexed_dataset, dataset_size

    @staticmethod
    def _partition_dataset(full_dataset, dataset_size, partitions):
        """ Splits the dataset """
        t0 = time.perf_counter()
        if partitions.randomized:
            full_dataset = full_dataset.shuffle(  
                buffer_size=dataset_size, seed=partitions.seed, reshuffle_each_iteration=False
            )
        
        training_size = int(partitions.training_ratio * dataset_size)
        validation_size = int(partitions.validation_ratio * dataset_size)
        test_size = dataset_size - training_size - validation_size
        
        training_set = full_dataset.take(training_size)
        test_val_set = full_dataset.skip(training_size)
        validation_set = test_val_set.take(validation_size)        
        test_set = test_val_set.skip(validation_size)        

        if partitions.randomized:
            logger.info(
                f"Partitioned dataset into training ({training_size}), validation ({validation_size}) " 
                f"and test ({test_size}) with randomization and seed {partitions.seed}. "
                f"Duration: {time.perf_counter() - t0:.3f}s")            
        else:
            logger.info(
                f"Partitioned dataset into training ({training_size}), validation ({validation_size}) " 
                f"and test ({test_size}) without randomization. "
                f"Duration: {time.perf_counter() - t0:.3f}s"
            )            
        return training_set, validation_set, test_set

    @staticmethod
    def _get_pipeline_builder(feature_datatype):
        """ Get pipeline builder """
        if feature_datatype == 'numerical':
            return pipelines.NumericalPipelineBuilder()
        elif feature_datatype == 'image':
            return pipelines.ImagePipelineBuilder()
        elif feature_datatype == 'binary':
            return pipelines.BinaryPipelineBuilder()
        elif feature_datatype == 'categorical':
            return pipelines.CategoricalPipelineBuilder()
        elif feature_datatype == 'text':
            return pipelines.TextPipelineBuilder()
        else:
            raise NotImplementedError(f"No pipeline defined for type '{feature_datatype}'")

    def _get_dataset_partition(self, partition):
        if partition == 'training':
            return self._training_set
        elif partition == 'validation':
            return self._validation_set
        elif partition == 'test':
            return self._test_set
        elif partition == 'all':
            return self._training_set.concatenate(self._validation_set).concatenate(self._test_set)
        else:
            raise ValueError(f"Invalid partition '{partition}'. Should be 'training', 'validation' or 'test'")

    def get_dataset(self, partition='training', shuffle=False, shuffle_seed=None, drop_index=True, apply_pipelines='all'):
        """ Returns a TensorFlow dataset """
        validate_pipeline_arg(apply_pipelines)
        
        self.ensure_initialized()        
        dataset = self._get_dataset_partition(partition)

        if shuffle:
            size = self.get_dataset_size(partition=partition)
            dataset = dataset.shuffle(buffer_size=size, seed=shuffle_seed)

        preprocessed_dataset = self._apply_pipelines(dataset, which=apply_pipelines)
        split_dataset = self._split_inputs_and_targets(preprocessed_dataset)            

        if drop_index: 
            split_dataset = split_dataset.map(lambda index, inputs, targets: (inputs, targets), num_parallel_calls=tf.data.AUTOTUNE)
        
        return split_dataset

    def get_example_batch(self, batch_size=None, output_type='tensor', partition='training', shuffle=False, shuffle_seed=None, drop_index=True, apply_pipelines='all'):
        if output_type not in ('tensor', 'list', 'numpy', 'shape'):
            raise ValueError("Output type must be 'tensor', 'list', 'numpy', 'shape'")
        
        dataset = self.get_dataset(
            partition=partition,
            shuffle=shuffle,
            shuffle_seed=shuffle_seed,
            drop_index=drop_index,
            apply_pipelines=apply_pipelines
        )

        if batch_size:
            dataset = dataset.repeat().batch(batch_size)
        
        inputs_batch, targets_batch = next(iter(dataset))

        if output_type in ('list', 'numpy', 'shape'):
            def eval_fn(x):
                x = x.numpy()

                if output_type == 'list' and isinstance(x, bytes):
                    x = x.decode()
                elif output_type == 'list':
                    x = x.tolist()
                elif output_type == 'shape':
                    x = x.shape
                return x
            
            inputs_batch = {k: eval_fn(v) for k, v in inputs_batch.items()}
            targets_batch = {k: eval_fn(v) for k, v in targets_batch.items()}
            
        return inputs_batch, targets_batch

    def get_dataset_size(self, partition='training'):
        """ Returns size of a partition TensorFlow dataset """
        self.ensure_initialized()                
        dataset = self._get_dataset_partition(partition)
        size = len(dataset)  # TODO(anton.k): store the sizes instead for a speedup
        return size

    def get_loader_pipeline(self, feature_name):
        """ Get the augmenter pipeline associated with a feature """
        self.ensure_initialized()                
        return self._loader_pipelines[feature_name]    

    def get_augmenter_pipeline(self, feature_name):
        """ Get the augmenter pipeline associated with a feature """
        self.ensure_initialized()                
        return self._augmenter_pipelines[feature_name]
    
    def get_preprocessing_pipeline(self, feature_name):
        """ Get the preprocessing pipeline associated with a feature """
        self.ensure_initialized()                
        return self._preprocessing_pipelines[feature_name]

    def get_postprocessing_pipeline(self, feature_name):
        """ Get the postprocessing pipeline associated with a feature """
        self.ensure_initialized()                
        return self._postprocessing_pipelines[feature_name]

    def _apply_pipelines(self, dataset, which='all'):
        """ Applies preprocessing pipelines to the data
        
        Expects and returns a dataset with structure: (row, dict[feature_name]) 
        """
        validate_pipeline_arg(which)
        
        t0 = time.perf_counter()
        def func(index, values):
            preprocessed_data = {}
            for feature_name, feature_tensor in values.items():
                if which in ('all', 'loader'):
                    loader = self._loader_pipelines[feature_name]
                    loaded_tensor = loader(feature_tensor)
                else:
                    loaded_tensor = feature_tensor

                if which == 'all':
                    augmenter = self._augmenter_pipelines[feature_name]
                    augmented_tensor = augmenter((index, loaded_tensor))
                    
                    preprocessing = self._preprocessing_pipelines[feature_name]
                    preprocessed_data[feature_name] = preprocessing(augmented_tensor)
                else:
                    preprocessed_data[feature_name] = loaded_tensor

            return (index, preprocessed_data)

        preprocessed_dataset = dataset.map(func, num_parallel_calls=tf.data.AUTOTUNE)
        logger.debug(f"Applied pipelines to dataset. Duration: {time.perf_counter() - t0:.3f}s")
        return preprocessed_dataset

    def _split_inputs_and_targets(self, dataset):
        """ Creates a dataset with structure (dict[input_feature_name], dict[target_feature_name])

        Expects dataset with structure: (row, dict[feature_name])
        """        
        def func(indices, data):
            inputs = {}
            targets = {}

            for feature_name, feature_spec in self._dataset_settings.used_feature_specs.items():
                if feature_spec.iotype == 'input':
                    inputs[feature_name] = data[feature_name]
                elif feature_spec.iotype == 'target':                    
                    targets[feature_name] = data[feature_name]
            return (indices, inputs, targets)
                
        split_dataset = dataset.map(func, num_parallel_calls=tf.data.AUTOTUNE)
        return split_dataset

    def get_feature_shape(self, feature_name):
        """ Returns the shape of a feature. """
        self.ensure_initialized()                
        dataset = self.get_dataset()
        inputs_batch, targets_batch = next(iter(dataset))
        shape = inputs_batch[feature_name].shape
        return shape

    @staticmethod
    def _make_paths_absolute(df, dataset_settings):
        """ Converts relative paths in the dataframe to absolute paths"""
        base_directory = os.path.dirname(dataset_settings.file_path)
        
        path_cols = [
            feature_name
            for feature_name, feature_spec in dataset_settings.used_feature_specs.items()
            if feature_spec.datatype in ['image']
        ]

        def make_absolute(x):
            """ convert from <file_name> to <base_directory>/<file_name> """
            return os.path.join(base_directory, x.replace('\\', '/'))

        df[path_cols] = df[path_cols].applymap(make_absolute)
        return df

    @staticmethod
    def _validate_feature_specs(columns, feature_specs):
        """ Assert that atleast one input and one output is specified """

        inputs = set()
        targets = set()
        
        for name, spec in feature_specs.items():
            if name not in columns:
                raise ValueError(f"Feature '{name}' not in columns")
            
            if spec.iotype.lower() == 'input':
                inputs.add(name)
            elif spec.iotype == 'target':
                targets.add(name)

        if len(inputs) == 0:
            raise ValueError("No inputs specified!")
        if len(targets) == 0:
            raise ValueError("No targets specified!")

    @property
    def feature_specs(self):
        """ Returns the feature specs used to instantiate this data loader"""
        return self._dataset_settings.used_feature_specs

    @property
    def settings(self):
        return self._dataset_settings

    @property
    def is_tutorial_data(self):
        """ Returns true if the DataLoader was based on tutorial data"""
        data_file = self._dataset_settings.file_path
        return utils.is_tutorial_data_file(data_file)
        
    @property
    def metadata(self):
        self.ensure_initialized()                
        return copy.deepcopy(self._metadata)

    def get_data_frame(self, partition='original'):
        """ Reconstructs the data frame. The option 'all' is a potentially shuffled version of 'original' """
        self.ensure_initialized()                        
        partitions = ['original', 'all', 'training', 'validation', 'test']
        if partition not in partitions:
            raise ValueError("partition must be one of " + ", ".join(partitions))

        if partition == 'original':
            return self._data_frame.copy()  # Defensive copy
        else:
            dataset = self._get_dataset_partition(partition=partition)
            indices = [original_row for original_row, data in dataset]
            return self._data_frame.iloc[indices]
            
