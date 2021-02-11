import pandas as pd
import tensorflow as tf
from typing import Dict
from collections import namedtuple


FeatureSpec = namedtuple('FeatureSpec', ['datatype', 'iotype'])


class DataLoader:
    def __init__(self, data_frame: pd.DataFrame, feature_specs: Dict[str, FeatureSpec]):
        self._feature_specs = feature_specs
        self._df = data_frame
    
    @classmethod
    def from_csv(cls, feature_specs: Dict[str, FeatureSpec], path: str) -> 'DataLoader':
        """ Creates a DataLoader given a csv file

        Arguments:
            feature_specs: the feature specs
            path: the path to the csv file
        """
        df = pd.read_csv(path)
        return cls(df, feature_specs)

    def get_dataset(self) -> tf.data.Dataset:
        """ Returns a TensorFlow dataset """
        input_columns = [name for name, feature_spec in self._feature_specs.items() if feature_spec.iotype=='input']
        target_columns = [name for name, feature_spec in self._feature_specs.items() if feature_spec.iotype=='output']

        input_dataset = tf.data.Dataset.from_tensor_slices(self._df[input_columns].to_dict(orient='list'))
        target_dataset = tf.data.Dataset.from_tensor_slices(self._df[target_columns].to_dict(orient='list'))
        
        dataset = tf.data.Dataset.zip((input_dataset, target_dataset))
        return dataset

    @property
    def feature_specs(self) -> Dict[str, FeatureSpec]:
        """ Returns the feature specs """
        return self._feature_specs.copy()

