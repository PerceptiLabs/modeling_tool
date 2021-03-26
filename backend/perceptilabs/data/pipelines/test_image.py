import pytest
import tensorflow as tf
import numpy as np
import os
import skimage.io as sk


from perceptilabs.data.pipelines import build_image_pipelines


@pytest.mark.tf2x
def test_image_preprocessing(temp_path):
    expected = np.random.random((128,128,3)).astype(np.float32)
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
    tensor_inputs = tf.constant(inputs)
    dataset = tf.data.Dataset.from_tensor_slices(tensor_inputs)

    # Create the pipeline
    pipeline, _, _ = build_image_pipelines(dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    # See if the actual concrete value has the same shape as we expect
    actual = next(iter(processed_dataset)).numpy()

    assert actual.shape == expected.shape

    


    
