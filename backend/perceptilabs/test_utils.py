from contextlib import contextmanager
import numpy as np
import os
import pandas as pd
import skimage.io as sk

from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, DatasetSettings, Partitions


def remove_nothrow(*paths):
    for path in paths:
        try:
            os.remove(path)
        except:
            pass

@contextmanager
def file_cleanup(*paths):
    try:
        yield paths
    finally:
        remove_nothrow(*paths)


@contextmanager
def make_data_loader(data):
    files = []
    if data['x1']['type'] == 'image':
        for path in data['x1']['values']:
            image = np.random.randint(0, 255, data['x1']['shape'], dtype=np.uint8)
            sk.imsave(path, image)
            files.append(path)

    with file_cleanup(*files):

        feature_specs = {
            'x1': FeatureSpec(iotype='input', datatype=data['x1']['type']),
            'y1': FeatureSpec(iotype='target', datatype=data['y1']['type'])
        }
        partitions = Partitions(training_ratio=1.0, validation_ratio=0.0, test_ratio=0.0)

        dataset_settings = DatasetSettings(
            feature_specs=feature_specs,
            partitions=partitions,
        )

        df = pd.DataFrame({'x1': data['x1']['values'], 'y1': data['y1']['values']})
        dl = DataLoader(df, dataset_settings)
        yield dl
