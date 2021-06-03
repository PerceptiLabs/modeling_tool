import pytest
import tensorflow as tf
import numpy as np
import os
import cv2
import skimage.io as sk
import tempfile
from unittest.mock import MagicMock

from perceptilabs.data.pipelines import ImagePipelineBuilder


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
def cifar10_red_paths():  # Only use the red channel [assuming RGB]
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    x_train = x_train[:, :, :, 0]        
    yield convert_numpy_images_to_csv(x_train, num_images=8, start=2)


@pytest.fixture(scope='session')
def mnist_images(mnist_paths):
    images = []
    for path in mnist_paths:
        images.append(sk.imread(path))
    yield images


@pytest.fixture(scope='session')
def cifar10_red_images(cifar10_red_paths):
    images = []
    for path in cifar10_red_paths:
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
    image = np.random.randint(0, 255, size=(16, 16, 3)).astype(np.uint16)
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

    
def test_normalize_standard_norm_for_single_sample(temp_path):
    image = np.random.randint(0, 255, size=(16, 16, 3)).astype(np.uint8)
        
    # Create the dataset
    tensor_inputs = save_image_to_disk(image, temp_path, ext='.png', repeats=9)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'normalize': {'type': 'standardization'}}
    
    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    

    processed_image = next(iter(processed_dataset)).numpy()
    
    # Since there's only one image, it should have zero mean and unit variance
    assert np.isclose(processed_image.mean(), 0.0)
    assert np.isclose(processed_image.std(), 1.0)    
    

def test_normalize_minmax_norm_for_single_sample(temp_path):
    max_value = 200
    min_value = 100
    
    image = np.random.randint(min_value, max_value+1, size=(16, 16, 3)).astype(np.uint8)
    
    def normalize(x):
        y = (x - min_value)/(max_value-min_value)
        return y.astype(np.float32)

    expected_image = normalize(image)
    
    # Create the dataset
    tensor_inputs = save_image_to_disk(image, temp_path, ext='.png', repeats=9)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'normalize': {'type': 'min-max'}}
    
    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    
    actual_image = next(iter(processed_dataset)).numpy()

    assert np.isclose(actual_image, normalize(image)).all()
    assert actual_image.max() == 1.0  # Since there's only one image, it will contain the max value
    assert actual_image.min() == 0.0  # Since there's only one image, it will contain the min value

    
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

    
def test_image_random_crop_has_correct_shape(mnist_paths):
    dataset = tf.data.Dataset.from_tensor_slices(mnist_paths)

    height = 10
    width = 15
    expected_shape = (height, width, 1)

    feature_spec = MagicMock()
    feature_spec.preprocessing = {'random_crop': {'height': height, 'width': width, 'seed': 1234}}

    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    
    for sample in processed_dataset:
        assert sample.shape == expected_shape

    assert pipeline.image_shape == expected_shape  # Verify that the pipeline records shape    

def test_image_random_crop_two_datasets_with_same_seed_are_cropped_uniformly(mnist_paths, mnist_images):
    dataset1 = tf.data.Dataset.from_tensor_slices(mnist_paths)
    dataset2 = tf.data.Dataset.from_tensor_slices(mnist_paths)    

    height = 10
    width = 15
    
    def apply_pipeline(dataset, seed):
        feature_spec = MagicMock()
        feature_spec.preprocessing = {'random_crop': {'height': height, 'width': width, 'seed': seed}}
    
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

    
def test_image_random_crop_two_datasets_with_different_seed_are_not_cropped_uniformly(mnist_paths, mnist_images):
    dataset1 = tf.data.Dataset.from_tensor_slices(mnist_paths)
    dataset2 = tf.data.Dataset.from_tensor_slices(mnist_paths)    

    height = 10
    width = 15
    
    def apply_pipeline(dataset, seed):
        feature_spec = MagicMock()
        feature_spec.preprocessing = {'random_crop': {'height': height, 'width': width, 'seed': seed}}
    
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
        processed_dataset = dataset.map(lambda x: pipeline(x))
        return processed_dataset

    processed1 = apply_pipeline(dataset1, seed=1234)
    processed2 = apply_pipeline(dataset2, seed=2000)

    images_matches = [
        (sample1.numpy() == sample2.numpy()).all()
        for sample1, sample2 in zip(processed1, processed2)
    ]
    assert not all(images_matches)
    

@pytest.mark.parametrize("extension", ['.png', '.tiff'])
def test_image_resize_has_correct_shape(extension, temp_path):
    image = np.random.randint(0, 255, size=(16, 16, 4)).astype(np.uint8)
    
    height, width = 10, 15
    expected_shape = (height, width, 3)
    
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'resize': {'mode': 'custom', 'height': height, 'width': width}}

    # Create the dataset
    tensor_inputs = save_image_to_disk(image, temp_path, ext=extension, repeats=3)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    pipeline, _, _ = ImagePipelineBuilder().build(feature_dataset=dataset, feature_spec=feature_spec)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    for sample in processed_dataset:
        assert sample.shape == expected_shape
    
    # See if the actual concrete value has the same shape as we expect
    assert pipeline.image_shape == expected_shape  # Verify that the pipeline records shape    
    

def test_image_resize_has_correct_shape_for_mixed_shape_images(mnist_paths, cifar10_red_paths, mnist_images, cifar10_red_images):
    assert mnist_images[0].shape != cifar10_red_images[0].shape

    paths = mnist_paths + cifar10_red_paths
    dataset = tf.data.Dataset.from_tensor_slices(paths)

    height = 10
    width = 15
    expected_shape = (height, width, 1)

    feature_spec = MagicMock()
    feature_spec.preprocessing = {'resize': {'mode': 'custom', 'height': height, 'width': width}}

    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    for sample in processed_dataset:
        assert sample.shape == expected_shape

    assert pipeline.image_shape == expected_shape  # Verify that the pipeline records shape    



def test_image_resize_automatic_has_mode_shape(mnist_paths, cifar10_red_paths, mnist_images, cifar10_red_images):
    assert mnist_images[0].shape != cifar10_red_images[0].shape

    paths = mnist_paths + cifar10_red_paths
    dataset = tf.data.Dataset.from_tensor_slices(paths)

    assert len(mnist_images) != len(cifar10_red_images)
    expected_shape = tuple(mnist_images[0].shape) + (1,)  # more mnist images, so thats the most common shape (mathematical 'mode')
        
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'resize': {'mode': 'automatic', 'type': 'mode'}}

    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    for sample in processed_dataset:
        assert sample.shape == expected_shape

    assert pipeline.image_shape == expected_shape  # Verify that the pipeline records shape    


def test_image_resize_automatic_has_mean_shape(mnist_paths, cifar10_red_paths, mnist_images, cifar10_red_images):
    assert mnist_images[0].shape != cifar10_red_images[0].shape

    paths = mnist_paths + cifar10_red_paths
    dataset = tf.data.Dataset.from_tensor_slices(paths)

    mean_shape = [0, 0, 1]
    count = 0

    for image in mnist_images + cifar10_red_images:
        h, w = image.shape
        mean_shape[0] += h
        mean_shape[1] += w
        count += 1

    mean_shape[0] = int(mean_shape[0]/count)
    mean_shape[1] = int(mean_shape[1]/count)
    expected_shape = tuple(mean_shape)
        
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'resize': {'mode': 'automatic', 'type': 'mean'}}

    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    for sample in processed_dataset:
        assert sample.shape == expected_shape

    assert pipeline.image_shape == expected_shape  # Verify that the pipeline records shape    


def test_image_resize_automatic_has_max_shape(mnist_paths, cifar10_red_paths, mnist_images, cifar10_red_images):
    assert mnist_images[0].shape != cifar10_red_images[0].shape

    paths = mnist_paths + cifar10_red_paths
    dataset = tf.data.Dataset.from_tensor_slices(paths)

    max_height = max(mnist_images[0].shape[0], cifar10_red_images[0].shape[0])
    max_width = max(mnist_images[0].shape[1], cifar10_red_images[0].shape[1])    
    expected_shape = (max_height, max_width, 1)
        
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'resize': {'mode': 'automatic', 'type': 'max'}}

    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    for sample in processed_dataset:
        assert sample.shape == expected_shape

    assert pipeline.image_shape == expected_shape  # Verify that the pipeline records shape    


def test_image_rotation_two_datasets_with_different_seed_are_not_rotated_uniformly(mnist_paths, mnist_images):
    dataset1 = tf.data.Dataset.from_tensor_slices(mnist_paths)
    dataset2 = tf.data.Dataset.from_tensor_slices(mnist_paths)    

    def apply_pipeline(dataset, seed):        
        feature_spec = MagicMock()
        feature_spec.preprocessing = {'random_rotation': {'seed': seed, 'fill_mode': 'reflect', 'factor': 1.0}}
    
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
    
    
def test_image_rotation_two_datasets_with_same_seed_are_rotated_uniformly(mnist_paths, mnist_images):
    dataset1 = tf.data.Dataset.from_tensor_slices(mnist_paths)
    dataset2 = tf.data.Dataset.from_tensor_slices(mnist_paths)    

    def apply_pipeline(dataset, seed):        
        feature_spec = MagicMock()
        feature_spec.preprocessing = {'random_rotation': {'seed': seed, 'fill_mode': 'reflect', 'factor': 1.0}}
    
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

    
def test_image_resize_automatic_has_min_shape(mnist_paths, cifar10_red_paths, mnist_images, cifar10_red_images):
    assert mnist_images[0].shape != cifar10_red_images[0].shape

    paths = mnist_paths + cifar10_red_paths
    dataset = tf.data.Dataset.from_tensor_slices(paths)

    min_height = min(mnist_images[0].shape[0], cifar10_red_images[0].shape[0])
    min_width = min(mnist_images[0].shape[1], cifar10_red_images[0].shape[1])    
    expected_shape = (min_height, min_width, 1)
        
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'resize': {'mode': 'automatic', 'type': 'min'}}

    pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    for sample in processed_dataset:
        assert sample.shape == expected_shape

    assert pipeline.image_shape == expected_shape  # Verify that the pipeline records shape    

    
def test_image_random_crop_two_datasets_with_different_seed_are_not_cropped_uniformly(mnist_paths, mnist_images):
    dataset1 = tf.data.Dataset.from_tensor_slices(mnist_paths)
    dataset2 = tf.data.Dataset.from_tensor_slices(mnist_paths)    

    height = 10
    width = 15
    
    def apply_pipeline(dataset, seed):
        feature_spec = MagicMock()
        feature_spec.preprocessing = {'random_crop': {'height': height, 'width': width, 'seed': seed}}
    
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
        processed_dataset = dataset.map(lambda x: pipeline(x))
        return processed_dataset

    processed1 = apply_pipeline(dataset1, seed=1234)
    processed2 = apply_pipeline(dataset2, seed=2000)

    images_matches = [
        (sample1.numpy() == sample2.numpy()).all()
        for sample1, sample2 in zip(processed1, processed2)
    ]
    assert not all(images_matches)
    

def test_image_random_crop_raises_error_too_high(mnist_paths):
    dataset = tf.data.Dataset.from_tensor_slices(mnist_paths)

    height = 100
    width = 15
    
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'random_crop': {'height': height, 'width': width, 'seed': 1234}}

    with pytest.raises(ValueError):
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    

def test_image_random_crop_raises_error_too_wide(mnist_paths):
    dataset = tf.data.Dataset.from_tensor_slices(mnist_paths)

    height = 100
    width = 15
    
    feature_spec = MagicMock()
    feature_spec.preprocessing = {'random_crop': {'height': height, 'width': width, 'seed': 1234}}

    with pytest.raises(ValueError):
        pipeline, _, _ = ImagePipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    
