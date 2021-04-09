import pytest
import tensorflow as tf
import numpy as np
import os
import skimage.io as sk


from perceptilabs.data.pipelines import build_image_pipelines


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


@pytest.mark.tf2x
def test_image_preprocessing_for_png(temp_path):
    image = np.random.randint(0, 255, size=(16, 16, 3)).astype(np.uint8)
    expected = image.astype(np.float32)
    inputs = list()

    # Save images into a dataset
    for i in range (1, 9):
        file_name = str(i) + '.png'
        path=os.path.join(temp_path, file_name)

        assert file_name not in os.listdir(temp_path)

        sk.imsave(path, expected)

        inputs.append(path)

        assert file_name in os.listdir(temp_path)

    # Create the dataset
    tensor_inputs = save_image_to_disk(image, temp_path, ext='.png', repeats=9)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    pipeline, _, _ = build_image_pipelines(feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    
    # See if the actual concrete value has the same shape as we expect
    actual = next(iter(processed_dataset)).numpy()
    
    assert np.all(actual == expected)

    assert actual.shape == expected.shape
    assert pipeline.image_shape == expected.shape  # Verify that the pipeline records shape


@pytest.mark.tf2x
def test_image_preprocessing_for_tiff(temp_path):
    image = np.random.randint(0, 255, size=(16, 16, 4)).astype(np.uint16)
    expected = image.astype(np.float32) 
        
    # Create the dataset
    tensor_inputs = save_image_to_disk(image, temp_path, ext='.tiff', repeats=9)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    pipeline, _, _ = build_image_pipelines(feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    
    # See if the actual concrete value has the same shape as we expect
    actual = next(iter(processed_dataset)).numpy()

    assert np.all(actual == expected)



    
