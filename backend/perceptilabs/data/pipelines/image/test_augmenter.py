import numpy as np
import pytest

from perceptilabs.data.pipelines.image.augmenter import Augmenter
from perceptilabs.data.settings import ImagePreprocessingSpec

def test_horizontal_flip():
    original_image = np.random.random((32, 32, 3))
    expected_image = np.fliplr(original_image)

    augmenter = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_flip=True, random_flip_mode='horizontal', random_flip_seed=12)                                                        
    )
    actual_image = augmenter((0, original_image))
    assert (actual_image == expected_image).numpy().all()
    
    
def test_vertical_flip():
    original_image = np.random.random((32, 32, 3))
    expected_image = np.flipud(original_image)

    augmenter = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_flip=True, random_flip_mode='vertical', random_flip_seed=12)                                                                
    )
    actual_image = augmenter((0, original_image))
    assert (actual_image == expected_image).numpy().all()


def test_vertical_and_horizontal_flip():
    original_image = np.random.random((32, 32, 3))
    expected_image = np.flipud(np.fliplr(original_image))

    augmenter = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_flip=True, random_flip_mode='both', random_flip_seed=12)                                                                        
    )
    actual_image = augmenter((0, original_image))
    assert (actual_image == expected_image).numpy().all()

    
def test_same_row_is_flipped_equally_when_seeds_are_equal():
    images = np.random.random((20, 32, 32, 3))    

    augmenter1 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_flip=True, random_flip_mode='horizontal', random_flip_seed=12)                                                                                
    )
    augmenter2 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_flip=True, random_flip_mode='horizontal', random_flip_seed=12)                                                                                        
    )    

    results1 = np.array([
        augmenter1((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])
    results2 = np.array([
        augmenter2((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])

    assert (results1 == results2).all()


def test_same_row_is_flipped_unequally_when_seeds_are_different():
    images = np.random.random((20, 32, 32, 3))    

    augmenter1 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_flip=True, random_flip_mode='horizontal', random_flip_seed=12)
    )
    augmenter2 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_flip=True, random_flip_mode='horizontal', random_flip_seed=21)
    )    

    results1 = np.array([
        augmenter1((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])
    results2 = np.array([
        augmenter2((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])

    assert (results1 != results2).any()
    

def test_rotated_image_is_different_from_original():
    original_image = np.random.random((32, 32, 3))
    
    augmenter = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_flip=True, random_flip_mode='horizontal', random_flip_seed=12)        
    )
    
    image = augmenter((0, original_image))
    assert (image != original_image).numpy().any()
    
    
def test_same_row_is_rotated_equally_when_seeds_are_equal():
    images = np.random.random((20, 32, 32, 3))    

    augmenter1 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_rotation=True, random_rotation_factor=0.5, random_rotation_fill_mode='reflect', random_rotation_seed=12)                
    )
    augmenter2 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_rotation=True, random_rotation_factor=0.5, random_rotation_fill_mode='reflect', random_rotation_seed=12)                        
    )    

    results1 = np.array([
        augmenter1((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])
    results2 = np.array([
        augmenter2((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])

    assert (results1 == results2).all()

    
def test_same_row_is_rotated_unequally_when_seeds_are_different():
    images = np.random.random((20, 32, 32, 3))    

    augmenter1 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_rotation=True, random_rotation_factor=0.5, random_rotation_fill_mode='reflect', random_rotation_seed=12)                                
    )
    augmenter2 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_rotation=True, random_rotation_factor=0.5, random_rotation_fill_mode='reflect', random_rotation_seed=21)                                        
    )    

    results1 = np.array([
        augmenter1((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])
    results2 = np.array([
        augmenter2((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])

    assert (results1 != results2).any()
    
    
def test_random_crop_has_correct_shape():
    image = np.random.random((32, 32, 3))

    augmenter = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_crop=True, random_crop_height=16, random_crop_width=16, random_crop_seed=1234)
    )
    new_image = augmenter((0, image))
    assert new_image.shape == (16, 16, 3)


def test_same_row_is_cropped_equally_when_seeds_are_equal():
    images = np.random.random((20, 32, 32, 3))    

    augmenter1 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_crop=True, random_crop_height=16, random_crop_width=16, random_crop_seed=1234)        
    )
    augmenter2 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_crop=True, random_crop_height=16, random_crop_width=16, random_crop_seed=1234)                
    )
    
    results1 = np.array([
        augmenter1((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])
    results2 = np.array([
        augmenter2((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])

    assert (results1 == results2).all()

    
def test_same_row_is_cropped_unequally_when_seeds_are_different():
    images = np.random.random((20, 32, 32, 3))    

    augmenter1 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_crop=True, random_crop_height=16, random_crop_width=16, random_crop_seed=1234)                        
    )
    augmenter2 = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_crop=True, random_crop_height=16, random_crop_width=16, random_crop_seed=12345)                                
    )    

    results1 = np.array([
        augmenter1((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])
    results2 = np.array([
        augmenter2((row, original_image)).numpy()
        for row, original_image in enumerate(images)
    ])

    assert (results1 != results2).any()
    

def test_image_random_crop_raises_error_too_high():
    image = np.random.random((32, 32, 3))

    augmenter = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_crop=True, random_crop_height=64, random_crop_width=16, random_crop_seed=12344)                                        
    )

    with pytest.raises(ValueError):
        augmenter((0, image))
    

def test_image_random_crop_raises_error_too_wide():
    image = np.random.random((32, 32, 3))

    augmenter = Augmenter(
        preprocessing=ImagePreprocessingSpec(random_crop=True, random_crop_height=16, random_crop_width=64, random_crop_seed=12344)                                                
    )

    with pytest.raises(ValueError):
        augmenter((0, image))

    
