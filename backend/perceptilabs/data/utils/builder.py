import os
import tempfile
from uuid import uuid1
from collections import UserDict
from contextlib import contextmanager

import numpy as np
import pandas as pd
import skimage.io as sk

from perceptilabs.data.base import DataLoader, FeatureSpec
from perceptilabs.data.settings import DatasetSettings



class Row:
    def __init__(self, literals=None, file_data=None, file_type=None):
        self.literals = (literals or {}).copy()
        self.file_data = (file_data or {}).copy()
        self.file_type = (file_type or {}).copy()

    def __setitem__(self, key, value):
        self.literals[key] = value

    def __getitem__(self, key, value):
        if key in self.literals:
            return self.literals[key] 
        elif key in self.file_data:
            return self.file_data[key]
        else:
            raise KeyError

    @property
    def fields(self):
        fields = set()
        
        for field in self.literals.keys():
            fields.add(field)
            
        for field in self.file_data.keys():
            fields.add(field)
            
        return fields

    def create(self, directory, index):
        dict_ = self.literals.copy()

        for feature, array in self.file_data.items():

            if feature in dict_:
                raise ValueError("Duplicate entry for feature '{feature}'")
            
            file_type = self.file_type.get(feature, '.npy')
            file_name = f"feature_{index}" + file_type
            file_path = os.path.join(directory, file_name)
            
            if file_type == '.npy':
                np.save(file_path, array)
            elif file_type in ('.png', '.jpg', '.tiff'):
                sk.imsave(file_path, array)                                
            else:
                raise ValueError(f"Unsupported file type '{file_type}'")
            
            dict_[feature] = file_path
        
        return dict_


class DatasetBuilder:
    def __init__(self, settings, metadata=None, num_repeats=1):
        self.settings = settings
        self.metadata = metadata
        self.num_repeats = num_repeats
        
        self.fields = set(settings.used_feature_specs.keys())
        self.rows = []
        self.directories = []

    @classmethod
    def from_features(cls, feature_specs, metadata=None, num_repeats=1):
        for name, spec in feature_specs.items():
            if isinstance(spec, dict):  
                feature_specs[name] = FeatureSpec(
                    datatype=spec['datatype'],
                    iotype=spec['iotype']
                )
        
        settings = DatasetSettings(feature_specs=feature_specs)
        return cls(settings, metadata=metadata, num_repeats=num_repeats)

    @classmethod
    def from_features(cls, feature_specs, metadata=None, num_repeats=1):
        settings = DatasetSettings(feature_specs=feature_specs)
        return cls(settings, metadata=metadata, num_repeats=num_repeats)

    @contextmanager
    def create_row(self):
        row = Row()
        yield row
        self._save_row(row)        

    def add_row(self, literals=None, file_data=None, file_type=None):
        row = Row(literals=literals, file_data=file_data, file_type=file_type)
        self._save_row(row)

    def _save_row(self, row):
        missing = self.fields - row.fields
        extraneous = row.fields - self.fields
        
        if missing:
            raise ValueError("Missing values for columns " + ", ".join(missing))

        if extraneous:
            raise ValueError("Got extra values for columns " + ", ".join(extraneous))

        self.rows.append(row)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for directory in self.directories:
            directory.cleanup()

    def get_data_loader(self):
        directory = tempfile.TemporaryDirectory()
        self.directories.append(directory)
        
        df = pd.DataFrame(columns=self.fields)
        
        for index, row in enumerate(self.rows):
            row_dict = row.create(directory.name, index)
            
            df = df.append(
                row_dict,
                ignore_index=True,
                verify_integrity=True,
                sort=True
            )
            
        data_loader = DataLoader(
            df, self.settings, metadata=self.metadata, num_repeats=self.num_repeats)
        return data_loader        
        

