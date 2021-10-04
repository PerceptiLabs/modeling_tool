import numpy as np
from perceptilabs.data.settings import DatasetSettings, FeatureSpec
from perceptilabs.data.utils.builder import DatasetBuilder

    
def test_build_dataset_using_create():
    dataset_settings = DatasetSettings(
        feature_specs={
            'image': FeatureSpec(datatype='image', iotype='input'),
            'digit': FeatureSpec(datatype='numerical', iotype='target')
        }
    )

    expected_images = []
    expected_digits = []
    
    for i in range(30):
        image = np.random.random((28, 28, 3)).astype(np.float32)
        digit = np.float32(np.random.randint(0, 10))
        
        expected_images.append(image)
        expected_digits.append(digit)

        
    with DatasetBuilder(dataset_settings) as builder:
        for image, digit in zip(expected_images, expected_digits):
            with builder.create_row() as row:
                row.file_data['image'] = image
                row.file_type['image'] = '.png'
                row.literals['digit'] = digit
        
        data_loader = builder.get_data_loader()
        dataset = data_loader.get_dataset(partition='all')

        actual_images = []
        actual_digits = []        
        
        for inputs, targets in dataset:
            actual_digits.append(targets['digit'].numpy())            

        assert np.all(actual_digits == expected_digits)
        
    
def test_build_dataset_using_add():
    dataset_settings = DatasetSettings(
        feature_specs={
            'image': FeatureSpec(datatype='image', iotype='input'),
            'digit': FeatureSpec(datatype='numerical', iotype='target')
        }
    )

    expected_images = []
    expected_digits = []
    
    for i in range(30):
        image = np.random.random((28, 28, 3)).astype(np.float32)
        digit = np.float32(np.random.randint(0, 10))
        
        expected_images.append(image)
        expected_digits.append(digit)

        
    with DatasetBuilder(dataset_settings) as builder:
        for image, digit in zip(expected_images, expected_digits):
            builder.add_row(
                literals={'digit': digit},
                file_data={'image': image},
                file_type={'image': '.png'}
            )
            
        data_loader = builder.get_data_loader()
        dataset = data_loader.get_dataset(partition='all')

        actual_images = []
        actual_digits = []        
        
        for inputs, targets in dataset:
            actual_digits.append(targets['digit'].numpy())            

        assert np.all(actual_digits == expected_digits)
        
    
