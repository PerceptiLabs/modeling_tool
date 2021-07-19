import pytest
import numpy as np
from perceptilabs.createDataObject import grayscale2RGBA


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
