import os
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
import tensorflow as tf
from typing import Dict

import perceptilabs.data.pipelines as pipelines


class FeatureSpec:
    def __init__(self, datatype, iotype, file_path=''):
        self.datatype = datatype
        self.iotype = iotype
        self.file_path = file_path


class DataLoader:
    def __init__(self, data_frame, feature_specs, partitions=None, base_directory=None, randomized_partitions=False, randomized_partitions_seed=None, shuffle_seed=None):
        partitions = partitions or {'training': 0.7, 'validation': 0.2, 'test': 0.1}        
        self._feature_specs = feature_specs
        
        self._randomized_partitions = randomized_partitions
        self._randomized_partitions_seed = randomized_partitions_seed
        
        self._validate_partitions(partitions)
        self._validate_feature_specs(data_frame.columns, feature_specs)
        
        if base_directory is not None:
            data_frame = self._make_paths_absolute(data_frame, feature_specs, base_directory)
        
        self._unprocessed_datasets, self._pipelines = self._build_datasets_and_pipelines(
            data_frame, feature_specs, partitions
        )

    @classmethod
    def from_dict(cls, dict_):
        """ Creates a DataLoader given a settings dict """
        feature_specs = {}

        for feature_name, feature_dict in dict_['featureSpecs'].items():
            feature_specs[feature_name] = FeatureSpec(
                iotype=feature_dict['iotype'].lower(),
                datatype=feature_dict['datatype'].lower(),
                file_path=feature_dict['csv_path']
            )

        partitions = {
            'training': dict_['partitions'][0]/100.0,
            'validation': dict_['partitions'][1]/100.0,
            'test': dict_['partitions'][2]/100.0,
        }
        
        data_loader = cls.from_features(
            feature_specs=feature_specs,
            randomized_partitions=dict_['randomizedPartitions'],
            partitions=partitions
        )
        return data_loader        

    @classmethod
    def from_graph_spec(cls, graph_spec, partitions=None):
        """ Derives a data loader from a graph spec 
        
        NOTE: use from_dict instead!
        """
        feature_specs = {}
        paths = []
        for layer_spec in graph_spec.get_ordered_layers():
            if layer_spec.is_input_layer or layer_spec.is_output_layer:
                iotype = 'input' if layer_spec.is_input_layer else 'output'
                paths.append(layer_spec.file_path)
                
                feature_specs[layer_spec.feature_name] = FeatureSpec(
                    iotype=iotype,
                    datatype=layer_spec.datatype,
                    file_path=layer_spec.file_path
                )
        if len(set(paths)) != 1:
            raise NotImplementedError("Exactly one data file is supported!")

        return cls.from_features(feature_specs, partitions=partitions)
        
    @classmethod
    def from_features(cls, feature_specs, partitions=None, randomized_partitions=False, randomized_partitions_seed=None) -> 'DataLoader':
        """ Creates a DataLoader given set of features

        Arguments:
            feature_specs: the feature specs
        """
        paths = set()
        for spec in feature_specs.values():
            paths.add(spec.file_path)

        if len(paths) != 1:
            raise ValueError(f"Feature specs must contain exactly _one_ CSV path. Got {len(paths)}")

        path = next(iter(paths))
        df = pd.read_csv(path)
        data_loader = cls(
            df,
            feature_specs,
            partitions=partitions,
            randomized_partitions=randomized_partitions,
            randomized_partitions_seed=randomized_partitions_seed,
            base_directory=os.path.dirname(path)
        )
        return data_loader

    def _select_columns_by_iotype(self, df, feature_specs, iotype):
        """ Selects input or output components from the dataframe """
        assert iotype in ['input', 'output']
        column_names = [name for name, feature_spec in feature_specs.items() if feature_spec.iotype==iotype]        
        return df[column_names]

    def _create_datasets_and_pipelines_from_dataframe(self, df, feature_specs, partitions):
        """ Creates pre- and post-processing pipelines for the dataframe and then splits it into 3 tensorflow datasets """
        per_feature_training_sets = {}
        per_feature_validation_sets = {}
        per_feature_test_sets = {}

        pipelines = {}

        for feature_name in df.columns:                    
            feature_datasets, feature_pipelines = self._load_and_preprocess_feature(
                df, feature_specs, feature_name, partitions
            )
            feature_training_set, feature_validation_set, feature_test_set = feature_datasets
            per_feature_training_sets[feature_name] = feature_training_set
            per_feature_validation_sets[feature_name] = feature_validation_set
            per_feature_test_sets[feature_name] = feature_test_set            

            training_pipeline, inference_pipeline, postprocessing_pipeline = feature_pipelines
            pipelines[feature_name] = {
                'training': training_pipeline,
                'inference': inference_pipeline,
                'postprocessing': postprocessing_pipeline
            }

        training_set = tf.data.Dataset.zip(per_feature_training_sets)
        validation_set = tf.data.Dataset.zip(per_feature_validation_sets)
        test_set = tf.data.Dataset.zip(per_feature_test_sets)
        datasets = (training_set, validation_set, test_set)        
        return datasets, pipelines

    def _load_and_preprocess_feature(self, df, feature_specs, feature_name, partitions):
        """ Loads a single column from the dataframe and splits it into a set of preprocessed tf.data.Datasets """
        feature_values = df[feature_name].values.tolist()  # Create a dataset for an individual column
        feature_dataset = tf.data.Dataset.from_tensor_slices(feature_values)

        feature_training_set, feature_validation_set, feature_test_set = self._split_dataset(
            feature_dataset, len(df), partitions
        )
        training_pipeline, inference_pipeline, postprocessing_pipeline = self._build_pipelines(
            feature_specs[feature_name], feature_training_set
        )
        
        feature_datasets = (feature_training_set, feature_validation_set, feature_test_set)
        feature_pipelines = (training_pipeline, inference_pipeline, postprocessing_pipeline)
        
        return feature_datasets, feature_pipelines

    def _split_dataset(self, full_dataset, dataset_size, partitions):
        """ Splits a dataset. NOTE: this is per column, so shuffling here is not recommended. """
        training_size = int(partitions['training'] * dataset_size)
        validation_size = int(partitions['validation'] * dataset_size)
        
        training_set = full_dataset.take(training_size)
        test_val_set = full_dataset.skip(training_size)
        validation_set = test_val_set.take(validation_size)        
        test_set = test_val_set.skip(validation_size)        

        return training_set, validation_set, test_set

    def _build_pipelines(self, feature_spec, feature_training_set):
        """ Build pipelines. 
        
        Returns:
            Two preprocessing pipelines: one for training and one for inference.
            One postprocessing pipeline.
        """
        build_pipeline = self._get_pipeline_builder(feature_spec.datatype)
        
        training_pipeline, inference_pipeline, postprocessing_pipeline = build_pipeline(
            feature_spec=feature_spec,
            feature_dataset=feature_training_set
        )
        if inference_pipeline is None:
            inference_pipeline = training_pipeline
            
        if postprocessing_pipeline is None:
            postprocessing_pipeline = tf.keras.Model()  # Identity: do nothing.

        return training_pipeline, inference_pipeline, postprocessing_pipeline
    
    def _get_pipeline_builder(self, feature_datatype):
        """ Get pipeline builder """
        if feature_datatype == 'numerical':
            return pipelines.build_numerical_pipelines
        elif feature_datatype == 'image':
            return pipelines.build_image_pipelines
        elif feature_datatype == 'binary':
            return pipelines.build_binary_pipelines
        elif feature_datatype == 'categorical':
            return pipelines.build_categorical_pipelines
        else:
            raise NotImplementedError(f"No pipeline defined for type '{feature_datatype}'")

    def get_dataset(self, partition='training', shuffle=False, shuffle_seed=None):
        """ Returns a TensorFlow dataset """
        dataset = self._unprocessed_datasets[partition]

        if shuffle:
            size = self.get_dataset_size(partition=partition)
            dataset = dataset.shuffle(buffer_size=size, seed=shuffle_seed) 

        mode = 'training' if partition == 'training' else 'inference'
        dataset = self._apply_pipelines(dataset, mode)
        return dataset

    def get_dataset_size(self, partition='training'):
        """ Returns size of a partition TensorFlow dataset """
        size = len(list(self._unprocessed_datasets[partition]))
        return size

    def get_preprocessing_pipeline(self, feature_name, mode='training'):
        """ Get the preprocessing pipeline associated with a feature """
        if mode not in ['training', 'inference']:
            raise ValueError("Valid preprocessing modes are 'training' and 'inference'")
        
        return self._pipelines[feature_name][mode]        
        
    def get_postprocessing_pipeline(self, feature_name):
        """ Get the postprocessing pipeline associated with a feature """
        return self._pipelines[feature_name]['postprocessing']        
        
    def _build_datasets_and_pipelines(self, df, feature_specs, partitions):
        if self._randomized_partitions:
            df = df.sample(
                frac=1, axis=0, random_state=self._randomized_partitions_seed
            ).reset_index(drop=True)  
        
        input_dataframe = self._select_columns_by_iotype(df, feature_specs, 'input')
        target_dataframe = self._select_columns_by_iotype(df, feature_specs, 'output')
        
        input_datasets, input_pipelines = self._create_datasets_and_pipelines_from_dataframe(
            input_dataframe, feature_specs, partitions
        )
        target_datasets, target_pipelines = self._create_datasets_and_pipelines_from_dataframe(
            target_dataframe, feature_specs, partitions
        )

        input_training_set, input_validation_set, input_test_set = input_datasets
        target_training_set, target_validation_set, target_test_set = target_datasets

        training_set = tf.data.Dataset.zip((input_training_set, target_training_set))
        validation_set = tf.data.Dataset.zip((input_validation_set, target_validation_set))
        test_set = tf.data.Dataset.zip((input_test_set, target_test_set))

        datasets = {
            'training': training_set.cache(),
            'validation': validation_set.cache(),
            'test': test_set.cache()                
        }
        
        pipelines = {}
        pipelines.update(input_pipelines)
        pipelines.update(target_pipelines)

        return datasets, pipelines


    def _apply_pipelines(self, dataset, mode):
        
        class Pipelines(tf.keras.Model):
            def __init__(self, pipelines):
                super().__init__()
                self._pipelines = pipelines
            
            def __call__(self, x):
                inputs, targets = x

                processed_inputs = {}
                for name, value in inputs.items():
                    pipeline = self._pipelines[name][mode]
                    processed_inputs[name] = pipeline(value)


                processed_targets = {}
                for name, value in targets.items():
                    pipeline = self._pipelines[name][mode]                    
                    processed_targets[name] = pipeline(value)
                    
                y = (processed_inputs, processed_targets)
                return y

        pipelines = Pipelines(self._pipelines)
        dataset = dataset.map(lambda x, y: pipelines((x, y)))
        return dataset

    def get_feature_shape(self, feature_name):
        """ Returns the shape of a feature. """
        dataset = self.get_dataset()
        inputs_batch, targets_batch = next(iter(dataset))
        shape = inputs_batch[feature_name].shape
        return shape
    
    def _make_paths_absolute(self, df, feature_specs, base_directory):
        """ Converts relative paths in the dataframe to absolute paths"""
        path_cols = [
            feature_name
            for feature_name, feature_spec in feature_specs.items()
            if feature_spec.datatype in ['image']
        ]

        def make_absolute(series):
            """ convert from <file_name> to <base_directory>/<file_name> """
            return str(base_directory + os.path.sep) + series  

       
        df[path_cols] = df[path_cols].apply(make_absolute)
        return df
    
    def _validate_partitions(self, partitions):
        """ Check that data partitions add up to 100% """
        sum_ = partitions['training'] + partitions['validation'] + partitions['test']
        if not np.isclose(sum_, 1.0):
            raise ValueError("Partitions must sum to 1.0!")        

    def _validate_feature_specs(self, columns, feature_specs):
        """ Assert that the there is a one-to-one mapping between the columns and feature specs. Also, that atleast one input and one output is specified """
        for column in columns:
            if column not in feature_specs:
                raise ValueError(f"Column '{column}' not in feature specs")
        
        inputs = set()
        outputs = set()
        
        for name, spec in feature_specs.items():
            if name not in columns:
                raise ValueError(f"Feature '{name}' not in columns")
            
            if spec.iotype.lower() == 'input':
                inputs.add(name)
            elif spec.iotype == 'output':
                outputs.add(name)

        if len(inputs) == 0:
            raise ValueError("No inputs specified!")
        if len(outputs) == 0:
            raise ValueError("No outputs specified!")

    @property
    def feature_specs(self):
        return self._feature_specs

