from typing import Tuple, Dict, Type, Any, List, Union
from abc import abstractmethod
import numpy as np
import hashlib
from pydantic import root_validator

from perceptilabs.utils import MyPydanticBaseModel


class Partitions(MyPydanticBaseModel):
    randomized: bool = False
    seed: Union[int, None] = 123
    training_ratio: float = 0.7
    validation_ratio: float = 0.2
    test_ratio: float = 0.1

    @classmethod
    def from_dict(cls, dict_):
        return cls(
            randomized=dict_['randomizedPartitions'],
            training_ratio=dict_['partitions'][0]/100.0,
            validation_ratio=dict_['partitions'][1]/100.0,
            test_ratio=dict_['partitions'][2]/100.0            
        )

    @root_validator    
    def _validate_partitions(cls, values):
        """ Check that data partitions add up to 100% """
        sum_ = values['training_ratio'] + values['validation_ratio'] + values['test_ratio']
        if not np.isclose(sum_, 1.0):
            raise ValueError("Partitions must sum to 1.0!")
        
        return values

    def compute_hash(self):
        hasher = hashlib.sha256()
        hasher.update(str(self.randomized).encode())
        hasher.update(str(self.seed).encode())
        hasher.update(str(self.training_ratio).encode())
        hasher.update(str(self.validation_ratio).encode())
        hasher.update(str(self.test_ratio).encode())
        return hasher.hexdigest()


class PreprocessingSpec(MyPydanticBaseModel):
    @classmethod
    @abstractmethod
    def from_dict(cls, dict_):
        return cls()

    def compute_hash(self):
        hasher = hashlib.sha256()
        hashable_types = (int, float, bool, str, type(None))
        
        for key, value in self.__dict__.items():
            if isinstance(value, hashable_types):
                hasher.update(str(value).encode())
            else:
                raise ValueError(f"Can only hash types: f{hashable_types}, not f{type(value)}") 

        return hasher.hexdigest()            

    
class NumericalPreprocessingSpec(PreprocessingSpec):    
    normalize: bool = False
    normalize_mode: str = None

    @classmethod
    def from_dict(cls, dict_):
        kwargs = {}        
        if 'normalize' in dict_:
            kwargs['normalize'] = True
            kwargs['normalize_mode'] = dict_['normalize']['type']

        return cls(**kwargs)


class ImagePreprocessingSpec(PreprocessingSpec):    
    resize: bool = False
    resize_mode: str = None
    resize_height: int = None
    resize_width: int = None
    resize_automatic_mode: str = None

    random_flip: bool = False
    random_flip_mode: str = None
    random_flip_seed: int = None
    
    random_rotation: bool = False
    random_rotation_seed: int = None
    random_rotation_factor: float = None
    random_rotation_fill_mode: str = None
    random_rotation_fill_value: float = None
    random_rotation_interpolation: str = None

    random_crop: bool = False
    random_crop_seed: int = None    
    random_crop_height: int = None
    random_crop_width: int = None

    normalize: bool = False
    normalize_mode: str = None


    @classmethod
    def from_dict(cls, dict_):
        kwargs = {}
        
        if 'normalize' in dict_:
            kwargs['normalize'] = True
            kwargs['normalize_mode'] = dict_['normalize']['type']

        if 'resize' in dict_:
            kwargs['resize'] = True
            kwargs['resize_mode'] = dict_['resize']['mode']

            if dict_['resize']['mode'] == 'automatic':
                kwargs['resize_automatic_mode'] = dict_['resize']['type']
            elif dict_['resize']['mode'] == 'custom':
                kwargs['resize_height'] = dict_['resize']['height']
                kwargs['resize_width'] = dict_['resize']['width']

        if 'random_flip' in dict_:
            kwargs['random_flip'] = True
            kwargs['random_flip_mode'] = dict_['random_flip']['mode']
            kwargs['random_flip_seed'] = dict_['random_flip']['seed']

        if 'random_rotation' in dict_:            
            kwargs['random_rotation'] = True
            kwargs['random_rotation_seed'] = dict_['random_rotation']['seed']
            kwargs['random_rotation_factor'] = dict_['random_rotation']['factor']
            kwargs['random_rotation_fill_mode'] = dict_['random_rotation']['fill_mode']
            kwargs['random_rotation_fill_value'] = 0.0
            kwargs['random_rotation_interpolation'] = 'bilinear'

        if 'random_crop' in dict_:
            kwargs['random_crop'] = True
            kwargs['random_crop_seed'] = dict_['random_crop']['seed']
            kwargs['random_crop_height'] = dict_['random_crop']['height']
            kwargs['random_crop_width'] = dict_['random_crop']['width']            

        return cls(**kwargs)

    
class FeatureSpec(MyPydanticBaseModel):
    datatype: str = None
    iotype: str = None
    file_path: str = None
    preprocessing: PreprocessingSpec = None

    @classmethod
    def from_dict(cls, dict_):
        datatype = dict_['datatype'].lower()

        preprocessing = None
        if datatype == 'numerical':
            preprocessing = NumericalPreprocessingSpec.from_dict(dict_['preprocessing'])
        elif datatype == 'image':
            preprocessing = ImagePreprocessingSpec.from_dict(dict_['preprocessing'])

        return cls(
            iotype=dict_['iotype'].lower(),
            datatype=datatype,
            preprocessing=preprocessing,
            file_path=dict_['csv_path']            
        )

    def compute_hash(self):
        hasher = hashlib.sha256()
        hasher.update(str(self.datatype).encode())
        hasher.update(str(self.iotype).encode())
        hasher.update(str(self.file_path).encode())

        if self.preprocessing:
            hasher.update(self.preprocessing.compute_hash().encode())
            
        return hasher.hexdigest()
    

class DatasetSettings(MyPydanticBaseModel):
    feature_specs: Dict[str, FeatureSpec] = {}
    partitions: Partitions = Partitions()
    file_path: str = ''

    @classmethod
    def from_dict(cls, dict_):
        feature_specs = {
            feature_name: FeatureSpec.from_dict(feature_dict)
            for feature_name, feature_dict in dict_['featureSpecs'].items()
        }
        partitions = Partitions.from_dict(dict_)

        file_path = dict_.get('file_path')
        if not file_path:
            file_path = cls._resolve_file_path(feature_specs)
        
        return cls(
            file_path=file_path,
            partitions=partitions,
            feature_specs=feature_specs
        )

    @staticmethod
    def _resolve_file_path(feature_specs):
        """ Resolves file path from feature specs """
        paths = set()
        for spec in feature_specs.values():
            paths.add(spec.file_path)

        if len(paths) == 0:
            return None
        else:
            path = next(iter(paths))
            return path
    
    @property
    def used_feature_specs(self):
        return {
            name: spec for name, spec in self.feature_specs.items()
            if spec.iotype in ["target", "input"]
        }

    def compute_hash(self):
        hasher = hashlib.md5()
        hasher.update(str(self.file_path).encode())
        hasher.update(self.partitions.compute_hash().encode())

        for name, spec in self.feature_specs.items():
            hasher.update(name.encode())            
            hasher.update(spec.compute_hash().encode())
        return hasher.hexdigest()

    def __getitem__(self, feature_name):
        return self.feature_specs[feature_name]
