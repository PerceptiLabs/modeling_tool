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
    from perceptilabs.data.base import DataLoader, FeatureSpec

    path = os.path.join(get_tutorial_data_directory(),
                        'Wildfires', 'data.csv')

    feature_specs = {
        'images': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing={'resize': {
                'mode': 'custom', 'width': 224, 'height': 224}},
            file_path=path
        ),
        'labels': FeatureSpec(
            datatype='categorical',
            iotype='target',
            preprocessing={},
            file_path=path
        )
    }

    loader = DataLoader.from_features(feature_specs, randomized_partitions=True, file_path=path)
    return loader
