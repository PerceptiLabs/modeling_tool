import pytest
import tensorflow as tf
import numpy as np
import os
import skimage.io as sk
import tempfile
from unittest.mock import MagicMock

from perceptilabs.data.pipelines import ImagePipelineBuilder
from perceptilabs.data.settings import ImagePreprocessingSpec


def convert_numpy_images_to_csv(matrix, num_images, start=0):
    directory = tempfile.mkdtemp().replace('\\', '/')    

    paths = []
    for i in range(start, num_images+start):
        path = os.path.join(directory, f'{i}.png')
        image = matrix[i]
        sk.imsave(path, image)
        paths.append(path)
    return paths


@pytest.fixture(scope='session')
def mnist_paths():
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    yield convert_numpy_images_to_csv(x_train, num_images=10, start=2)


@pytest.fixture(scope='session')
def mnist_images(mnist_paths):
    images = []
    for path in mnist_paths:
        images.append(np.atleast_3d(sk.imread(path)))
    yield images


def plot_dataset(dataset):
    import matplotlib.pyplot as plt
    for img in dataset:
        plt.imshow(img.numpy())
        plt.show()
    

def save_image_to_disk(image, directory, ext='.png', repeats=1):
    inputs = list()

    plugin = None
    if ext in ['.tif', '.tiff']:
        plugin = 'tifffile'        
    
    # Save images into a dataset
    for i in range(repeats):
        path = os.path.join(directory, f'{i}{ext}')

        if os.path.exists(path):
            os.remove(path)

        sk.imsave(path, image)

        saved_image = sk.imread(path, plugin=plugin)
        assert np.all(saved_image == image)
        assert os.path.exists(path)        
        inputs.append(path)

    return tf.constant(inputs)    


def test_build_from_metadata_gives_same_results(mnist_paths):
    dataset = tf.data.Dataset.from_tensor_slices(mnist_paths)

    preprocessing = ImagePreprocessingSpec(normalize=True, normalize_mode='min-max')        
    loader1, augmenter1, preprocessing1, _ = ImagePipelineBuilder().build_from_dataset(preprocessing, dataset)

    metadata = {'loader': loader1.metadata, 'augmenter': augmenter1.metadata, 'preprocessing': preprocessing1.metadata}
    loader2, augmenter2, preprocessing2, _ = ImagePipelineBuilder().load_from_metadata(preprocessing, metadata)

    dataset1 = dataset \
        .map(lambda x: loader1(x)) \
        .map(lambda x: augmenter1((0, x))) \
        .map(lambda x: preprocessing1(x))                 

    dataset2 = dataset \
        .map(lambda x: loader2(x)) \
        .map(lambda x: augmenter2((0, x))) \
        .map(lambda x: preprocessing2(x)) 
    
    for sample1, sample2 in tf.data.Dataset.zip((dataset1, dataset2)):
        assert np.all(sample1 == sample2)
