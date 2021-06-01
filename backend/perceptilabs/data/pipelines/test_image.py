import pytest
import tensorflow as tf
import numpy as np
import os
import skimage.io as sk
import tempfile
from unittest.mock import MagicMock

from perceptilabs.data.pipelines import ImagePipelineBuilder


@pytest.fixture(scope='session')
def mnist_paths():
    num_images = 8
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

    directory = tempfile.mkdtemp().replace('\\', '/')    

    paths = []
    for i in range(2, num_images+2):
        path = os.path.join(directory, f'{i}.png')
        image = x_train[i]
        sk.imsave(path, image)
        paths.append(path)
    yield paths
    

@pytest.fixture(scope='session')
def mnist_images(mnist_paths):
    images = []
    for path in mnist_paths:
        images.append(sk.imread(path))
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


def test_image_preprocessing_for_png(temp_path):
    image = np.random.randint(0, 255, size=(16, 16, 3)).astype(np.uint8)
    expected = image.astype(np.float32)
        
    # Create the dataset
    tensor_inputs = save_image_to_disk(image, temp_path, ext='.png', repeats=9)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    pipeline, _, _ = ImagePipelineBuilder().build(feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    
    # See if the actual concrete value has the same shape as we expect
    actual = next(iter(processed_dataset)).numpy()
    
    assert np.all(actual == expected)

    assert actual.shape == expected.shape
    assert pipeline.image_shape == expected.shape  # Verify that the pipeline records shape


def test_image_preprocessing_for_tiff(temp_path):
    image = np.random.randint(0, 255, size=(16, 16, 4)).astype(np.uint16)
    expected = image.astype(np.float32) 
        
    # Create the dataset
    tensor_inputs = save_image_to_disk(image, temp_path, ext='.tiff', repeats=9)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    pipeline, _, _ = ImagePipelineBuilder().build(feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    
    # See if the actual concrete value has the same shape as we expect
    actual = next(iter(processed_dataset)).numpy()

    assert np.all(actual == expected)

    
def test_image_preprocessing_normalization_for_single_sample(temp_path):
    image = np.random.randint(0, 255, size=(16, 16, 3)).astype(np.uint8)
        
    # Create the dataset
    tensor_inputs = save_image_to_disk(image, temp_path, ext='.png', repeats=9)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'normalize': True}
    
    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    

    processed_image = next(iter(processed_dataset)).numpy()
    
    # Since there's only one image, it should have zero mean and unit variance
    assert np.isclose(processed_image.mean(), 0.0)
    assert np.isclose(processed_image.std(), 1.0)    
    

def test_image_preprocessing_horizontal_flip(mnist_paths, mnist_images):
    dataset = tf.data.Dataset.from_tensor_slices(mnist_paths)

    def create_pipeline_and_get_sample(horizontal_flip):        
        feature_spec = MagicMock()
        if horizontal_flip:
            feature_spec.preprocessing = {'random_flip': {'mode': 'horizontal', 'seed': 1234}}
        else:
            feature_spec.preprocessing = {}
    
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
        processed_dataset = dataset.map(lambda x: pipeline(x))
        sample = next(iter(processed_dataset)).numpy()        
        return sample

    expected = np.fliplr(create_pipeline_and_get_sample(horizontal_flip=False))
    actual = create_pipeline_and_get_sample(horizontal_flip=True)
    assert (actual == expected).all()


def test_image_preprocessing_vertical_flip(mnist_paths, mnist_images):
    dataset = tf.data.Dataset.from_tensor_slices(mnist_paths)

    def create_pipeline_and_get_sample(vertical_flip):        
        feature_spec = MagicMock()
        if vertical_flip:
            feature_spec.preprocessing = {'random_flip': {'mode': 'vertical', 'seed': 1234}}
        else:
            feature_spec.preprocessing = {}
    
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
        processed_dataset = dataset.map(lambda x: pipeline(x))
        sample = next(iter(processed_dataset)).numpy()        
        return sample

    expected = np.flipud(create_pipeline_and_get_sample(vertical_flip=False))
    actual = create_pipeline_and_get_sample(vertical_flip=True)
    
    assert (actual == expected).all()

    

def test_image_preprocessing_horizontal_and_vertical_flip(mnist_paths, mnist_images):
    dataset = tf.data.Dataset.from_tensor_slices(mnist_paths)

    def create_pipeline_and_get_sample(flip):        
        feature_spec = MagicMock()
        if flip:
            feature_spec.preprocessing = {'random_flip': {'mode': 'both', 'seed': 1234}}
        else:
            feature_spec.preprocessing = {}
    
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
        processed_dataset = dataset.map(lambda x: pipeline(x))
        sample = next(iter(processed_dataset)).numpy()        
        return sample

    expected = np.fliplr(np.flipud(create_pipeline_and_get_sample(flip=False)))
    actual = create_pipeline_and_get_sample(flip=True)
    
    assert (actual == expected).all()


def test_image_preprocessing_two_datasets_with_same_seed_are_flipped_uniformly(mnist_paths, mnist_images):
    dataset1 = tf.data.Dataset.from_tensor_slices(mnist_paths)
    dataset2 = tf.data.Dataset.from_tensor_slices(mnist_paths)    

    def apply_pipeline(dataset, seed):        
        feature_spec = MagicMock()
        feature_spec.preprocessing = {'random_flip': {'mode': 'both', 'seed': seed}}
    
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
        processed_dataset = dataset.map(lambda x: pipeline(x))
        return processed_dataset

    processed1 = apply_pipeline(dataset1, seed=1234)
    processed2 = apply_pipeline(dataset2, seed=1234)

    images_matches = [
        (sample1.numpy() == sample2.numpy()).all()
        for sample1, sample2 in zip(processed1, processed2)
    ]
    assert all(images_matches)


def test_image_preprocessing_two_datasets_with_different_seed_are_not_flipped_uniformly(mnist_paths, mnist_images):
    dataset1 = tf.data.Dataset.from_tensor_slices(mnist_paths)
    dataset2 = tf.data.Dataset.from_tensor_slices(mnist_paths)    

    def apply_pipeline(dataset, seed):        
        feature_spec = MagicMock()
        feature_spec.preprocessing = {'random_flip': {'mode': 'both', 'seed': seed}}
    
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
        processed_dataset = dataset.map(lambda x: pipeline(x))
        return processed_dataset

    processed1 = apply_pipeline(dataset1, seed=1000)
    processed2 = apply_pipeline(dataset2, seed=2000)

    images_matches = [
        (sample1.numpy() == sample2.numpy()).all()
        for sample1, sample2 in zip(processed1, processed2)
    ]
    assert not all(images_matches)


def test_image_validation_pipeline_does_not_flip_images(mnist_paths, mnist_images):
    dataset = tf.data.Dataset.from_tensor_slices(mnist_paths)

    def apply_validation_pipeline(dataset, flip, training):        
        feature_spec = MagicMock()

        if flip:
            feature_spec.preprocessing = {'random_flip': {'mode': 'horizontal', 'seed': 123}}
        else:
            feature_spec.preprocessing = {}
    
        training_pipeline, validation_pipeline, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
        pipeline = training_pipeline if training else validation_pipeline
        
        processed_dataset = dataset.map(lambda x: pipeline(x))
        return processed_dataset

    processed1 = apply_validation_pipeline(dataset, flip=False, training=True)    
    processed2 = apply_validation_pipeline(dataset, flip=True, training=True)
    processed3 = apply_validation_pipeline(dataset, flip=True, training=False)

    training_images_match_original = [
        (sample1.numpy() == sample2.numpy()).all()
        for sample1, sample2 in zip(processed1, processed2)
    ]

    validation_images_match_original = [
        (sample1.numpy() == sample3.numpy()).all()
        for sample1, sample3 in zip(processed1, processed3)
    ]
    
    assert not all(training_images_match_original) and all(validation_images_match_original)
    
    


    

    
