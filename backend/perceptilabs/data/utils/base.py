import os
import filecmp
import pkg_resources
from perceptilabs.resources.files import FileAccess


def is_file_based_feature(datatype):
    return datatype in ['image', 'mask']


def localize_file_based_features(df, dataset_settings, file_access):
    """ Converts relative paths in the dataframe to absolute paths"""
    
    path_cols = [
        feature_name
        for feature_name, feature_spec in dataset_settings.used_feature_specs.items()
        if is_file_based_feature(feature_spec.datatype)
    ]        
    
    df[path_cols] = df[path_cols].applymap(
        lambda file_id: file_access.get_local_path(file_id))
    
    return df
    

def get_tutorial_data_directory():
    """ Retrieves the tutorial data directory """
    path = pkg_resources.resource_filename('perceptilabs', 'tutorial_data')
    return path


def get_tutorial_data_files():
    """ Gets the absolute path of every file in the tutorial data directory"""

    root = get_tutorial_data_directory()
    for path, subdirs, files in os.walk(root):
        for name in files:
            full_path = os.path.abspath(os.path.join(path, name))
            yield full_path


def is_tutorial_data_file(path):
    """ Checks whether a file path matches the tutorial data directory"""
    path = os.path.abspath(path)

    for other in get_tutorial_data_files():
        if os.path.exists(path) and filecmp.cmp(path, other, shallow=True):
            return True
    return False


def get_mnist_loader():
    from perceptilabs.data.base import DataLoader, FeatureSpec
    from perceptilabs.data.settings import DatasetSettings

    path = os.path.join(get_tutorial_data_directory(),
                        'mnist_small', 'data.csv')

    feature_specs = {
        'image_path': FeatureSpec(datatype='image', iotype='input'),
        'target': FeatureSpec(datatype='categorical', iotype='target')
    }

    settings = DatasetSettings(feature_specs=feature_specs)
    file_access = FileAccess(os.path.dirname(path))
    loader = DataLoader.from_csv(file_access, path, settings)
    return loader


def get_wildfire_loader():
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings, FeatureSpec, ImagePreprocessingSpec, Partitions

    path = os.path.join(get_tutorial_data_directory(),
                        'Wildfires', 'data.csv')
    feature_specs = {
        'images': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                resize=True,
                resize_mode='custom',
                resize_height=224,
                resize_width=224
            ),
        ),
        'labels': FeatureSpec(
            datatype='categorical',
            iotype='target',
        )
    }
    partitions = Partitions(randomized=True)
    settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )

    file_access = FileAccess(os.path.dirname(path))
    loader = DataLoader.from_csv(file_access, path, settings)
    return loader


def get_humanactivity_loader():
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings, FeatureSpec, Partitions
    
    path = os.path.join(get_tutorial_data_directory(),
                        'HumanActivity', 'data.csv')

    feature_specs = {
        'images': FeatureSpec(
            datatype='image',
            iotype='input',
        ),
        'labels': FeatureSpec(
            datatype='categorical',
            iotype='target',
        )
    }

    partitions = Partitions(randomized=True)
    settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    
    file_access = FileAccess(os.path.dirname(path))
    loader = DataLoader.from_csv(file_access, path, settings)
    return loader


def get_covid19_loader():
    from perceptilabs.data.base import DataLoader
    from perceptilabs.data.settings import DatasetSettings, FeatureSpec, Partitions    

    path = os.path.join(get_tutorial_data_directory(),
                        'Covid-19', 'data.csv')

    feature_specs = {
        'images': FeatureSpec(
            datatype='image',
            iotype='input',
        ),
        'labels': FeatureSpec(
            datatype='categorical',
            iotype='target',
        )
    }

    partitions = Partitions(randomized=True)
    settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    
    file_access = FileAccess(os.path.dirname(path))
    loader = DataLoader.from_csv(file_access, path, settings)
    return loader
