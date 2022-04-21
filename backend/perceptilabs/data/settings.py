from typing import Tuple, Dict, Type, Any, List, Union
from abc import abstractmethod
import numpy as np
import hashlib
from pydantic import root_validator
import copy

from perceptilabs.utils import MyPydanticBaseModel
from perceptilabs.utils import get_dataframe_type

FILE_BASED_DATATYPES = ["image", "mask"]  # Datatypes whose value is a path to a file


class Partitions(MyPydanticBaseModel):
    randomized: bool = False
    seed: Union[int, None] = 123
    training_ratio: float = 0.7
    validation_ratio: float = 0.2
    test_ratio: float = 0.1

    @classmethod
    def from_dict(cls, dict_):
        return cls(
            randomized=dict_["randomizedPartitions"],
            seed=int(dict_.get("randomSeed", 123)),
            training_ratio=dict_["partitions"][0] / 100.0,
            validation_ratio=dict_["partitions"][1] / 100.0,
            test_ratio=dict_["partitions"][2] / 100.0,
        )

    @root_validator
    def _validate_partitions(cls, values):
        """Check that data partitions add up to 100%"""
        sum_ = (
            values["training_ratio"] + values["validation_ratio"] + values["test_ratio"]
        )
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
    @property
    def num_augmentations(self):
        return 0

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
                raise ValueError(
                    f"Can only hash types: f{hashable_types}, not f{type(value)}"
                )

        return hasher.hexdigest()


class NumericalPreprocessingSpec(PreprocessingSpec):
    normalize: bool = False
    normalize_mode: str = None

    @classmethod
    def from_dict(cls, dict_):
        kwargs = {}
        if "normalize" in dict_:
            kwargs["normalize"] = True
            kwargs["normalize_mode"] = dict_["normalize"]["type"]

        return cls(**kwargs)


class BaseImagePreprocessingSpec(PreprocessingSpec):

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

    grayscale: bool = False

    @property
    def num_augmentations(self):
        count = 0

        if self.random_crop:
            count += 1
        if self.random_flip:
            count += 1
        if self.random_rotation:
            count += 1

    def _get_base_kwargs(self, dict_):
        kwargs = {}

        if "resize" in dict_:
            kwargs["resize"] = True
            kwargs["resize_mode"] = dict_["resize"]["mode"]

            if dict_["resize"]["mode"] == "automatic":
                kwargs["resize_automatic_mode"] = dict_["resize"]["type"]
            elif dict_["resize"]["mode"] == "custom":
                kwargs["resize_height"] = dict_["resize"]["height"]
                kwargs["resize_width"] = dict_["resize"]["width"]

        if "random_flip" in dict_:
            kwargs["random_flip"] = True
            kwargs["random_flip_mode"] = dict_["random_flip"]["mode"]
            kwargs["random_flip_seed"] = dict_["random_flip"]["seed"]

        if "random_rotation" in dict_:
            kwargs["random_rotation"] = True
            kwargs["random_rotation_seed"] = dict_["random_rotation"]["seed"]
            kwargs["random_rotation_factor"] = dict_["random_rotation"]["factor"]
            kwargs["random_rotation_fill_mode"] = dict_["random_rotation"]["fill_mode"]
            kwargs["random_rotation_fill_value"] = 0.0
            kwargs["random_rotation_interpolation"] = "bilinear"

        if "random_crop" in dict_:
            kwargs["random_crop"] = True
            kwargs["random_crop_seed"] = dict_["random_crop"]["seed"]
            kwargs["random_crop_height"] = dict_["random_crop"]["height"]
            kwargs["random_crop_width"] = dict_["random_crop"]["width"]

        if "grayscale" in dict_:
            kwargs["grayscale"] = dict_["grayscale"]

        return kwargs


class ImagePreprocessingSpec(BaseImagePreprocessingSpec):

    normalize: bool = False
    normalize_mode: str = None

    @classmethod
    def from_dict(cls, dict_):
        kwargs = cls()._get_base_kwargs(dict_)

        if "normalize" in dict_:
            kwargs["normalize"] = True
            kwargs["normalize_mode"] = dict_["normalize"]["type"]

        return cls(**kwargs)


class MaskPreprocessingSpec(BaseImagePreprocessingSpec):
    @classmethod
    def from_dict(cls, dict_):
        kwargs = cls()._get_base_kwargs(dict_)

        return cls(**kwargs)


class BoundingBoxPreprocessingSpec(BaseImagePreprocessingSpec):
    @classmethod
    def from_dict(cls, dict_):
        kwargs = cls()._get_base_kwargs(dict_)

        if "normalize" in dict_:
            kwargs["normalize"] = True
            kwargs["normalize_mode"] = dict_["normalize"]["type"]


class BoundingBoxPreprocessingSpec(BaseImagePreprocessingSpec):
    @classmethod
    def from_dict(cls, dict_):
        kwargs = cls()._get_base_kwargs(dict_)

        if "normalize" in dict_:
            kwargs["normalize"] = True
            kwargs["normalize_mode"] = dict_["normalize"]["type"]

        return cls(**kwargs)


class FeatureSpec(MyPydanticBaseModel):
    datatype: str = None
    iotype: str = None
    preprocessing: PreprocessingSpec = None

    @classmethod
    def from_dict(cls, dict_):
        datatype = dict_["datatype"].lower()

        preprocessing = None
        if datatype == "numerical":
            preprocessing = NumericalPreprocessingSpec.from_dict(dict_["preprocessing"])
        elif datatype == "image":
            preprocessing = ImagePreprocessingSpec.from_dict(dict_["preprocessing"])
        elif datatype == "mask":
            preprocessing = MaskPreprocessingSpec.from_dict(dict_["preprocessing"])
        elif datatype == "boundingbox":
            preprocessing = None
        return cls(
            iotype=dict_["iotype"].lower(),
            datatype=datatype,
            preprocessing=preprocessing,
        )

    def compute_hash(self):
        hasher = hashlib.sha256()
        hasher.update(str(self.datatype).encode())
        hasher.update(str(self.iotype).encode())

        if self.preprocessing:
            hasher.update(self.preprocessing.compute_hash().encode())

        return hasher.hexdigest()

    @property
    def is_file_based(self):
        return self.datatype in FILE_BASED_DATATYPES


class ObjectDetectionDatasetSettingsDict:
    @classmethod
    def resolve_from_dict(self, dict_):
        feature_spec_dict = dict_["featureSpecs"]

        feature_spec_dict["bounding_box"] = {}
        feature_spec_dict["bounding_box"]["datatype"] = "boundingbox"
        feature_spec_dict["bounding_box"]["iotype"] = "target"
        feature_spec_dict["bounding_box"]["preprocessing"] = {}

        for feature_name in list(feature_spec_dict):
            if feature_spec_dict[feature_name]["datatype"].lower() == "image":
                feature_spec_dict[feature_name]["iotype"] = "input"
                feature_spec_dict[feature_name]["preprocessing"] = {}
            elif feature_spec_dict[feature_name]["datatype"].lower() == "boundingbox":
                pass
            else:
                del feature_spec_dict[feature_name]

        dict_["featureSpecs"] = feature_spec_dict
        return dict_


class DatasetSettings(MyPydanticBaseModel):
    feature_specs: Dict[str, FeatureSpec] = {}
    partitions: Partitions = Partitions()
    dataset_id: str = ""

    @classmethod
    def from_dict(cls, dict_):
        dataset_id = str(dict_["datasetId"])
        partitions = Partitions.from_dict(dict_)
        dict_copy = copy.deepcopy(dict_)
        new_settings_dict = cls.resolve_dataset_settings_dict(dict_copy)
        feature_specs = {
            feature_name: FeatureSpec.from_dict(feature_dict)
            for feature_name, feature_dict in new_settings_dict["featureSpecs"].items()
        }
        return cls(
            partitions=partitions, feature_specs=feature_specs, dataset_id=dataset_id
        )

    @property
    def used_feature_specs(self):
        return {
            name: spec
            for name, spec in self.feature_specs.items()
            if spec.iotype in ["target", "input"]  # I.e., skip "do not use"
        }

    def compute_hash(self):
        hasher = hashlib.md5()
        hasher.update(self.partitions.compute_hash().encode())
        hasher.update(self.dataset_id.encode())
        for name, spec in self.feature_specs.items():
            hasher.update(name.encode())
            hasher.update(spec.compute_hash().encode())
        return hasher.hexdigest()

    def __getitem__(self, feature_name):
        return self.feature_specs[feature_name]

    @property
    def file_based_features(self):
        return [name for name, spec in self.feature_specs.items() if spec.is_file_based]

    @property
    def num_augmentations(self):
        count = 0
        for spec in self.feature_specs.values():
            preprocessing = spec.preprocessing

            if (
                preprocessing is not None
                and preprocessing.num_augmentations is not None
            ):
                count += preprocessing.num_augmentations

        return count

    @property
    def num_recommended_repeats(self):
        """Repeat data once per enabled augmentation setting.

        Temporary until we have a frontend solution
        """
        return self.num_augmentations + 1

    @classmethod
    def resolve_dataset_settings_dict(cls, settings_dict):
        dataframe_type = get_dataframe_type(settings_dict)
        if dataframe_type == "ObjectDetection":
            return ObjectDetectionDatasetSettingsDict.resolve_from_dict(settings_dict)
        else:
            return settings_dict
