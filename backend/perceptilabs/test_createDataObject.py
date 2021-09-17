import pytest
import numpy as np
from perceptilabs.createDataObject import mask, grayscale2RGBA


def test_grayscale2RGBA_returns_image_for_2_dimensional_large_input():
    data = np.random.random((200,200))
    output = grayscale2RGBA(data)
    #grayscale2RGBA returns flattened array
    assert output.shape == (200*200*4,)


def test_grayscale2RGBA_returns_image_for_3_dimensional_large_input():
    data = np.random.random((200, 200, 1))
    output = grayscale2RGBA(data)
    #grayscale2RGBA returns flattened array
    assert output.shape == (200*200*4,)

def test_grayscale2RGBA_returns_image_for_2_dimensional_small_input():
    data = np.random.random((1, 1))
    output = grayscale2RGBA(data)
    #grayscale2RGBA returns flattened array
    assert output.shape == (1*1*4,)


def test_grayscale2RGBA_returns_image_for_3_dimensional_small_input():
    data = np.random.random((1, 1, 1))
    output = grayscale2RGBA(data)
    #grayscale2RGBA returns flattened array
    assert output.shape == (1*1*4,)


def test_mask_type_works_with_2d_input():
    sample = np.random.randint(0,256,(224,224))
    output = mask(sample,1)
    assert output['height'] == 224
    assert output['width'] == 224


def test_mask_type_works_with_3d_binary_input():
    sample = np.random.randint(0,2,(224,224,2))
    output = mask(sample,1)
    assert output['height'] == 224
    assert output['width'] == 224

def test_mask_type_rks_with_3d_multiclass_input():
    sample = np.random.randint(0,10,(224,224,10))
    output = mask(sample,1)
    assert output['height'] == 224
    assert output['width'] == 224