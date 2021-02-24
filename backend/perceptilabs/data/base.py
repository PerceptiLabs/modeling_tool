import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd
import numpy as np
import tensorflow as tf
from typing import Dict

import perceptilabs.data.preprocessing as preprocessing

@dataclass
class FeatureSpec:
    datatype: str
    iotype: str
    file_path: str = ''


class DataLoader:
    def __init__(self, data_frame, feature_specs, base_directory=None):
        self._feature_specs = feature_specs
        self._preprocessing_pipelines = {}

        if base_directory is not None:
            self._df = self._make_paths_absolute(data_frame, base_directory)
        else:
            self._df = data_frame

    def _make_paths_absolute(self, df, base_directory):
        path_cols = [
            feature_name
            for feature_name, feature_spec in self._feature_specs.items()
            if feature_spec.datatype in ['image']
        ]

        def make_absolute(series):
            """ convert from <file_name> to <base_directory>/<file_name> """
            return str(base_directory + os.path.sep) + series  

        df[path_cols] = df[path_cols].apply(make_absolute)
        return df
    
    @classmethod
    def from_graph_spec(cls, graph_spec, default_dataset=None):
        # TODO: docs
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

        if default_dataset is not None and default_dataset.feature_specs == feature_specs:
            # If the new dataset would be equivalent to the default dataset, don't create a new one.
            return default_dataset
        else:
            return cls.from_features(feature_specs)
        
    @classmethod
    def from_features(cls, feature_specs: Dict[str, FeatureSpec]) -> 'DataLoader':
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
        return cls(df, feature_specs, base_directory=os.path.dirname(path))

    def _select_columns_by_iotype(self, iotype):
        # TODO: docs
        assert iotype in ['input', 'output']
        column_names = [name for name, feature_spec in self._feature_specs.items() if feature_spec.iotype==iotype]        
        return self._df[column_names]

    def _create_dataset_from_dataframe(self, df):
        per_feature_datasets = {
            feature_name: self._load_and_preprocess_feature(df, feature_name) 
            for feature_name in df.columns            
        }
        dict_dataset = tf.data.Dataset.zip(per_feature_datasets)
        return dict_dataset

    def _load_and_preprocess_feature(self, df, feature_name):
        feature_dataset = tf.data.Dataset.from_tensor_slices(df[feature_name].values.tolist())

        feature_datatype = self._feature_specs[feature_name].datatype        
        pipeline = self._preprocessing_pipelines[feature_name] = self._build_preprocessing_pipeline(
            feature_datatype, feature_dataset
        )
        feature_dataset = feature_dataset.map(lambda x: pipeline(x))  # Apply the pipeline
        return feature_dataset

    def _build_preprocessing_pipeline(self, feature_datatype, feature_dataset):
        # TODO: validation and test data shouldn't be used to build the pipeline (data leakage) [story 1537]
        if feature_datatype == 'numerical':
            return preprocessing.build_numerical_pipeline(feature_dataset)        
        elif feature_datatype == 'image':
            return preprocessing.build_image_pipeline(feature_dataset)
        else:
            raise NotImplementedError(f"No preprocessing pipeline defined for type '{feature_datatype}'")

    def get_dataset(self):
        """ Returns a TensorFlow dataset """
        input_dataframe = self._select_columns_by_iotype('input')
        target_dataframe = self._select_columns_by_iotype('output')
        
        input_dataset = self._create_dataset_from_dataframe(input_dataframe)
        target_dataset = self._create_dataset_from_dataframe(target_dataframe)
        
        dataset = tf.data.Dataset.zip((input_dataset, target_dataset))
        dataset = dataset.cache()  # Caches the preprocessed data in memory.        
        return dataset

    @property
    def feature_specs(self) -> Dict[str, FeatureSpec]:
        """ Returns the feature specs """
        return self._feature_specs.copy()

    def get_feature_shape(self, feature_name):
        """ Returns the shape of a feature. """
        dataset = self.get_dataset()
        inputs_batch, targets_batch = next(iter(dataset))
        shape = inputs_batch[feature_name].shape
        return shape

    def to_pandas(self):
        return self._df
