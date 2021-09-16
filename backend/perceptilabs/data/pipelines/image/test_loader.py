import os
import pytest
import numpy as np
import pandas as pd
import skimage.io as sk
import tensorflow as tf


from perceptilabs.data.pipelines.image.loader import Loader  
from perceptilabs.data.settings import ImagePreprocessingSpec

def random_image(shape, temp_path, ext):
    image = np.random.randint(0, 255, shape, dtype=np.uint8)
    idx = len(os.listdir(temp_path))
    image_path = os.path.join(temp_path, f'image{idx}{ext}')
    sk.imsave(image_path, image)
    return image_path, image


@pytest.mark.parametrize("ext", ['.png', '.tiff'])
def test_image_data_is_loaded_correctly(temp_path, ext):
    image_path, expected_image = random_image((32, 32, 3), temp_path, ext)    

    dataset = tf.data.Dataset.from_tensor_slices([image_path, image_path, image_path])
    loader = Loader.from_data(dataset)

    actual_image = loader(image_path)
    assert np.all(actual_image == expected_image)
    assert len(actual_image.shape) == 3  # Always 3 dim
    assert actual_image.shape[-1] == 3  # No alpha channel


@pytest.mark.parametrize("ext", ['.png', '.tiff'])
def test_rank_two_image_is_rank_three_tensor(temp_path, ext):
    image_path, image = random_image((32, 32), temp_path, ext)    

    dataset = tf.data.Dataset.from_tensor_slices([image_path, image_path, image_path])
    loader = Loader.from_data(dataset)

    loaded_image = loader(image_path)
    assert loaded_image.shape == [32, 32, 1]


@pytest.mark.parametrize("ext", ['.png', '.tiff'])
def test_grayscale_image_is_rank_three_tensor(temp_path, ext):
    image_path, image = random_image((32, 32, 1), temp_path, ext)    

    dataset = tf.data.Dataset.from_tensor_slices([image_path, image_path, image_path])
    loader = Loader.from_data(dataset)

    loaded_image = loader(image_path)
    assert loaded_image.shape == [32, 32, 1]


@pytest.mark.parametrize("ext", ['.png', '.tiff'])    
@pytest.mark.parametrize("shape_and_channels", [((32, 32, 1), 1), ((32, 32), 1), ((32, 32, 3), 3), ((32, 32, 4), 3)])
def test_image_has_correct_num_channels(temp_path, ext, shape_and_channels):
    image_shape, expected_channels = shape_and_channels    
    image_path, image = random_image(image_shape, temp_path, ext)    

    dataset = tf.data.Dataset.from_tensor_slices([image_path, image_path, image_path])
    loader = Loader.from_data(dataset)
    
    loaded_image = loader(image_path)
    assert loaded_image.shape[2] == expected_channels
    assert loader.metadata['n_channels'] == expected_channels    


@pytest.mark.parametrize("ext", ['.png', '.tiff'])
def test_image_data_is_loaded_with_custom_size(temp_path, ext):
    image_path, _ = random_image((32, 32, 3), temp_path, ext)        

    expected_height = 16
    expected_width = 6

    dataset = tf.data.Dataset.from_tensor_slices([image_path, image_path, image_path])
    preprocessing = ImagePreprocessingSpec(resize=True, resize_mode='custom', resize_height=expected_height, resize_width=expected_width)
    loader = Loader.from_data(dataset, preprocessing=preprocessing)
    
    image = loader(image_path)
    assert image.shape == (expected_height, expected_width, 3)


@pytest.mark.parametrize(
    "preprocessing",
    [
        None,
        ImagePreprocessingSpec(resize=False),
        ImagePreprocessingSpec(resize=True, resize_mode='custom'),
        ImagePreprocessingSpec(resize=True, resize_mode='automatic', resize_automatic_mode='min'),
        ImagePreprocessingSpec(resize=True, resize_mode='automatic', resize_automatic_mode='max'),
        ImagePreprocessingSpec(resize=True, resize_mode='automatic', resize_automatic_mode='mode'),               
    ]
)
def test_loader_has_target_shape(temp_path, preprocessing):
    image_path, _ = random_image((32, 32, 3), temp_path, '.png')        

    dataset = tf.data.Dataset.from_tensor_slices([image_path, image_path, image_path])
    loader = Loader.from_data(dataset, preprocessing=preprocessing)

    assert len(loader.metadata['target_shape']) == 2
    

@pytest.mark.parametrize("ext", ['.png', '.tiff'])
def test_image_data_is_loaded_with_automatic_shape_min(temp_path, ext):

    path1, _ = random_image((32, 32, 3), temp_path, ext)
    path2, _ = random_image((16, 8, 3), temp_path, ext)
    path3, _ = random_image((4, 32, 3), temp_path, ext)

    paths = [path1, path2, path3]
    dataset = tf.data.Dataset.from_tensor_slices([path1, path2, path3])    

    preprocessing = ImagePreprocessingSpec(resize=True, resize_mode='automatic', resize_automatic_mode='min')
    loader = Loader.from_data(dataset, preprocessing=preprocessing)

    y1 = loader(path1)
    y2 = loader(path2)
    y3 = loader(path3)

    assert y1.shape == (4, 8, 3)
    assert y2.shape == (4, 8, 3)
    assert y3.shape == (4, 8, 3)    


@pytest.mark.parametrize("ext", ['.png', '.tiff'])
def test_image_data_is_loaded_with_automatic_shape_max(temp_path, ext):
    path1, _ = random_image((64, 32, 3), temp_path, ext)
    path2, _ = random_image((16, 8, 3), temp_path, ext)
    path3, _ = random_image((4, 48, 3), temp_path, ext)
    dataset = tf.data.Dataset.from_tensor_slices([path1, path2, path3])    

    preprocessing = ImagePreprocessingSpec(resize=True, resize_mode='automatic', resize_automatic_mode='max')    
    loader = Loader.from_data(dataset, preprocessing=preprocessing)

    y1 = loader(path1)
    y2 = loader(path2)
    y3 = loader(path3)
    
    assert y1.shape == (64, 48, 3)
    assert y2.shape == (64, 48, 3)
    assert y3.shape == (64, 48, 3)    


@pytest.mark.parametrize("ext", ['.png', '.tiff'])
def test_image_data_is_loaded_with_automatic_shape_mean(temp_path, ext):
    path1, _ = random_image((64, 32, 3), temp_path, ext)
    path2, _ = random_image((16, 8, 3), temp_path, ext)
    path3, _ = random_image((4, 48, 3), temp_path, ext)
    dataset = tf.data.Dataset.from_tensor_slices([path1, path2, path3])
    
    expected_height = int((64+16+4)/3)
    expected_width = int((32+8+48)/3)

    preprocessing = ImagePreprocessingSpec(resize=True, resize_mode='automatic', resize_automatic_mode='mean')        
    loader = Loader.from_data(dataset, preprocessing=preprocessing)

    y1 = loader(path1)
    y2 = loader(path2)
    y3 = loader(path3)

    assert y1.shape == (expected_height, expected_width, 3)
    assert y2.shape == (expected_height, expected_width, 3)
    assert y3.shape == (expected_height, expected_width, 3)

    
@pytest.mark.parametrize("ext", ['.png', '.tiff'])
def test_image_data_is_loaded_with_automatic_shape_mode(temp_path, ext):
    path1, _ = random_image((64, 32, 3), temp_path, ext)
    path2, _ = random_image((16, 8, 3), temp_path, ext)
    path3, _ = random_image((32, 32, 3), temp_path, ext)
    path4, _ = random_image((16, 8, 3), temp_path, ext)

    dataset = tf.data.Dataset.from_tensor_slices([path1, path2, path3, path4])

    preprocessing = ImagePreprocessingSpec(resize=True, resize_mode='automatic', resize_automatic_mode='mode')            
    loader = Loader.from_data(dataset, preprocessing=preprocessing)

    y1 = loader(path1)
    y2 = loader(path2)
    y3 = loader(path3)
    y4 = loader(path4)    
    
    assert y1.shape == (16, 8, 3)
    assert y2.shape == (16, 8, 3)
    assert y3.shape == (16, 8, 3)
    assert y4.shape == (16, 8, 3)    
    

    
