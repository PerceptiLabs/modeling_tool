import os
import filecmp
import pkg_resources


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

    path = os.path.join(get_tutorial_data_directory(),
                        'mnist_small', 'data.csv')

    feature_specs = {
        'image_path': FeatureSpec(datatype='image', iotype='input', file_path=path),
        'target': FeatureSpec(datatype='categorical', iotype='target', file_path=path)
    }
    loader = DataLoader.from_features(feature_specs, file_path=path)
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
            file_path=path
        ),
        'labels': FeatureSpec(
            datatype='categorical',
            iotype='target',
            file_path=path
        )
    }
    partitions = Partitions(randomized=True)
    settings = DatasetSettings(
        file_path=path,
        feature_specs=feature_specs,
        partitions=partitions
    )

    loader = DataLoader.from_settings(settings)
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
            file_path=path
        ),
        'labels': FeatureSpec(
            datatype='categorical',
            iotype='target',
            file_path=path
        )
    }

    partitions = Partitions(randomized=True)
    settings = DatasetSettings(
        file_path=path,
        feature_specs=feature_specs,
        partitions=partitions
    )
    loader = DataLoader.from_settings(settings)    
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
            file_path=path
        ),
        'labels': FeatureSpec(
            datatype='categorical',
            iotype='target',
            file_path=path
        )
    }

    partitions = Partitions(randomized=True)
    settings = DatasetSettings(
        file_path=path,
        feature_specs=feature_specs,
        partitions=partitions
    )
    loader = DataLoader.from_settings(settings)    
    return loader
