import pytest
import copy

from perceptilabs.data.settings import DatasetSettings, FeatureSpec, Partitions, NumericalPreprocessingSpec, ImagePreprocessingSpec, FeatureSpec


@pytest.fixture(scope='function')
def settings_dict():
    settings = {
        "randomizedPartitions": True,
        "partitions": [
            70,
            20,
            10
        ],
        "featureSpecs": {
            "x1": {
                "csv_path": "~/test_data.csv",
                "iotype": "Input",
                "datatype": "image",
                "preprocessing": {
                    "resize": {
                        "mode": "automatic",
                        "type": "mean",
                    },
                    "random_flip": {
                        "mode": "horizontal",
                        "seed": 2000
                    },
                    "normalize": {
                        "type": "standardization"
                    },
                }
            },
            "x2": {
                "csv_path": "~/test_data.csv",
                "iotype": "Do not use",
                "datatype": "numerical",
                "preprocessing": {}
            },
            "y1": {
                "csv_path": "~/test_data.csv",                
                "iotype": "Target",
                "datatype": "numerical",
                "preprocessing": {
                    "normalize": {
                        "type": "min-max"
                    }
                }
            }
        }
    }
    yield settings


def test_settings_from_dict(settings_dict):
    settings = DatasetSettings.from_dict(settings_dict)

    assert settings.partitions.randomized
    assert settings.partitions.seed == 123
    assert settings.partitions.training_ratio == 0.7
    assert settings.partitions.validation_ratio == 0.2
    assert settings.partitions.test_ratio == 0.1

    assert settings.feature_specs['x1'].iotype == 'input'
    assert settings.feature_specs['x1'].datatype == 'image'
    
    assert settings.feature_specs['x1'].preprocessing.resize
    assert settings.feature_specs['x1'].preprocessing.resize_mode == 'automatic'
    assert settings.feature_specs['x1'].preprocessing.resize_height is None
    assert settings.feature_specs['x1'].preprocessing.resize_width is None
    assert settings.feature_specs['x1'].preprocessing.resize_automatic_mode == 'mean'
    
    assert settings.feature_specs['x1'].preprocessing.random_flip
    assert settings.feature_specs['x1'].preprocessing.random_flip_mode == 'horizontal'
    assert settings.feature_specs['x1'].preprocessing.random_flip_seed == 2000    

    assert settings.feature_specs['x1'].preprocessing.normalize
    assert settings.feature_specs['x1'].preprocessing.normalize_mode == 'standardization'
    
    assert not settings.feature_specs['x1'].preprocessing.random_rotation
    assert not settings.feature_specs['x1'].preprocessing.random_crop    

    assert settings.feature_specs['y1'].preprocessing.normalize
    assert settings.feature_specs['y1'].preprocessing.normalize_mode == 'min-max'

    assert (
        settings.feature_specs['x2'].iotype == "do not use" and
        'x2' not in settings.used_feature_specs
    )


def test_equal_partitions_have_equal_hash():
    p1 = Partitions(training_ratio=0.7, validation_ratio=0.2, test_ratio=0.1)
    p2 = Partitions(training_ratio=0.7, validation_ratio=0.2, test_ratio=0.1)    

    assert p1 == p2
    assert p1.compute_hash() == p2.compute_hash()    


def test_unequal_partitions_have_unequal_hash():
    p1 = Partitions(training_ratio=0.7, validation_ratio=0.2, test_ratio=0.1)
    p2 = Partitions(training_ratio=0.1, validation_ratio=0.2, test_ratio=0.7)
    p3 = Partitions(training_ratio=0.7, validation_ratio=0.1, test_ratio=0.2)
    p4 = Partitions(training_ratio=0.2, validation_ratio=0.7, test_ratio=0.1)            

    assert p1 != p2 != p3 != p4
    assert p1.compute_hash() != p2.compute_hash() != p3.compute_hash() != p4.compute_hash()    

    
def test_equal_numerical_preprocessing_have_equal_hash():
    a = NumericalPreprocessingSpec()
    b = NumericalPreprocessingSpec()    
    assert a.compute_hash() == b.compute_hash()


def test_unequal_numerical_preprocessing_have_unequal_hash():
    a = NumericalPreprocessingSpec(normalize=True, normalize_mode='abc')
    b = NumericalPreprocessingSpec(normalize=False, normalize_mode='abc')
    c = NumericalPreprocessingSpec(normalize=True, normalize_mode='def')        
    assert a.compute_hash() != b.compute_hash() != c.compute_hash()
    

def test_equal_image_preprocessing_have_equal_hash():
    a = ImagePreprocessingSpec()
    b = ImagePreprocessingSpec()    
    assert a.compute_hash() == b.compute_hash()


def test_unequal_image_preprocessing_have_unequal_hash():
    cases = [
        ImagePreprocessingSpec(),        
        ImagePreprocessingSpec(resize=True),
        ImagePreprocessingSpec(resize_mode='123'),
        ImagePreprocessingSpec(resize_height=10),
        ImagePreprocessingSpec(resize_width=10),
        ImagePreprocessingSpec(resize_automatic_mode='abc'),
        ImagePreprocessingSpec(random_flip=True),
        ImagePreprocessingSpec(random_flip_mode='bla'),
        ImagePreprocessingSpec(random_flip_seed=500),
        ImagePreprocessingSpec(random_rotation=True),
        ImagePreprocessingSpec(random_rotation_seed=500),
        ImagePreprocessingSpec(random_rotation_fill_mode='bla'),
        ImagePreprocessingSpec(random_rotation_fill_value=10.5),
        ImagePreprocessingSpec(random_rotation_interpolation='lalala'),
        ImagePreprocessingSpec(random_crop=True),
        ImagePreprocessingSpec(random_crop_height=10),
        ImagePreprocessingSpec(random_crop_width=10),
        ImagePreprocessingSpec(random_crop_seed=10),                
        ImagePreprocessingSpec(normalize=True),
        ImagePreprocessingSpec(normalize_mode='abc')
    ]

    hashes = [case.compute_hash() for case in cases]
    assert len(hashes) == len(set(hashes))  # Assert all are unique

    
def test_equal_settings_have_equal_hash(settings_dict):
    s1 = DatasetSettings.from_dict(settings_dict)
    s2 = DatasetSettings.from_dict(settings_dict)
    assert s1.compute_hash() == s2.compute_hash()


def test_settings_hash_depend_on_file_path():
    a = DatasetSettings(file_path='abc')
    b = DatasetSettings(file_path='xyz')
    assert a.compute_hash() != b.compute_hash()


def test_settings_hash_depend_on_partitions():
    p1 = Partitions(randomized=True)
    p2 = Partitions(randomized=False)
    s1 = DatasetSettings(partitions=p1)
    s2 = DatasetSettings(partitions=Partitions(randomized=False))
    assert p1.compute_hash() != p2.compute_hash()
    assert s1.compute_hash() != s2.compute_hash()


def test_settings_hash_depend_on_feature_specs():
    f1 = FeatureSpec(datatype='image')
    f2 = FeatureSpec(datatype='numerical')
    s1 = DatasetSettings(feature_specs={'a': f1})
    s2 = DatasetSettings(feature_specs={'a': f2})
    assert f1.compute_hash() != f2.compute_hash()
    assert s1.compute_hash() != s2.compute_hash()
    

def test_unequal_settings_have_unequal_hash(settings_dict):
    sd1 = copy.deepcopy(settings_dict)
    sd2 = copy.deepcopy(settings_dict)

    sd2['featureSpecs']['x1'] = copy.deepcopy(sd1['featureSpecs']['x2'])
    sd2['featureSpecs']['x2'] = copy.deepcopy(sd1['featureSpecs']['x1'])

    s1 = DatasetSettings.from_dict(sd1)
    s2 = DatasetSettings.from_dict(sd2)

    assert s1.compute_hash() != s2.compute_hash()

    
