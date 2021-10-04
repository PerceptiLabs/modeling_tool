import os
import pytest
import tempfile

import numpy as np
import pandas as pd
import skimage.io as sk

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.script import ScriptFactory
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, DatasetSettings, Partitions
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.resources.files import FileAccess
import perceptilabs.data.utils as data_utils            

data0 = {
    'x1': {
        'type': 'numerical',
        'values': [123.0, 24.0, 13.0, 45.0, 20.0, 200.0, 421.0, 300.0, 254.0, 217.0, 363.0, 500.0]
    },
    'y1': {
        'type': 'numerical',
        'values': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
    }
}


data1 = {
    'x1': {
        'type': 'categorical',
        'values': ['cat', 'house', 'horse', 'dog']
    },
    'y1': {
        'type': 'categorical',
        'values': ['animal', 'non-animal', 'animal', 'animal']
    }
}

data2 = {
    'x1': {
        'type': 'image',
        'values': ['1.jpg', '2.jpg', '3.jpg', '5.jpg'],
        'shape': (16, 16, 3)
    },
    'y1': {
        'type': 'categorical',
        'values': ['animal', 'non-animal', 'animal', 'animal']
    }
}

data3 = {
    'x1': {
        'type': 'categorical',
        'values': [0, 1, 2, 3]
    },
    'y1': {
        'type': 'categorical',
        'values': [1, 2, 0, 1]
    }
}


def make_data_loader(data, working_dir):
    if data['x1']['type'] == 'image':
        for path in data['x1']['values']:
            image = np.random.randint(0, 255, data['x1']['shape'], dtype=np.uint8)
            sk.imsave(os.path.join(working_dir, path), image)

    feature_specs = {
        'x1': FeatureSpec(iotype='input', datatype=data['x1']['type']),
        'y1': FeatureSpec(iotype='target', datatype=data['y1']['type'])
    }
    partitions = Partitions(training_ratio=1.0, validation_ratio=0.0, test_ratio=0.0)
    
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions,
    )

    file_access = FileAccess(working_dir)            
    df = pd.DataFrame({'x1': data['x1']['values'], 'y1': data['y1']['values']})
    df = data_utils.localize_file_based_features(df, dataset_settings, file_access)
    
    dl = DataLoader(df, dataset_settings)
    return dl


@pytest.fixture(params=[data0, data1, data2, data3])
def data_loader(request, temp_path):
    yield make_data_loader(request.param, temp_path)


def make_graph_spec(data_loader):
    gsb = GraphSpecBuilder()
    dirpath = tempfile.mkdtemp()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': data_loader.settings['x1'].datatype, 'feature_name': 'x1'}
    )

    if data_loader.settings['y1'].datatype == 'categorical':
        n_neurons = len(data_loader.get_preprocessing_pipeline('y1').metadata['mapping'])
    else:
        n_neurons = 1

    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': n_neurons}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': data_loader.settings['y1'].datatype, 'feature_name': 'y1'}
    )

    # Connect the layers
    gsb.add_connection(
        source_id=id1, source_var='output',
        dest_id=id2, dest_var='input'
    )
    gsb.add_connection(
        source_id=id2, source_var='output',
        dest_id=id3, dest_var='input'
    )

    graph_spec = gsb.build()
    return graph_spec
    

@pytest.mark.parametrize("batch_size", [1, 8])
def test_training_model_can_predict(script_factory, data_loader, batch_size):
    x, y_true = data_loader.get_example_batch(batch_size=batch_size)
    
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)

    y_pred, _ = training_model(x)

    for target in y_true.keys():
        assert target in y_pred
        assert y_pred[target].dtype == y_true[target].dtype
        assert y_pred[target].shape == y_true[target].shape
        

@pytest.mark.parametrize("batch_size", [1, 8])
def test_inference_model_can_predict_with_loaded_and_preprocessed_data(script_factory, data_loader, batch_size):
    x, y_true = data_loader.get_example_batch(
        batch_size=batch_size,
        apply_pipelines='all'  # load and preprocess
    )
    
    graph_spec = make_graph_spec(data_loader)
    inference_model = TrainingModel(script_factory, graph_spec) \
        .as_inference_model(
            data_loader,
            include_preprocessing=False,  # Data already preprocessed
        )

    y_pred = inference_model(x)

    for target in y_true.keys():
        assert target in y_pred
        assert y_pred[target].dtype == y_true[target].dtype
        assert y_pred[target].shape == y_true[target].shape
        

@pytest.mark.parametrize("batch_size", [1, 8])
def test_inference_model_can_predict_with_loaded_but_not_preprocessed_data(script_factory, data_loader, batch_size):
    x, y_true = data_loader.get_example_batch(
        batch_size=batch_size,
        apply_pipelines='loader'
    )

    graph_spec = make_graph_spec(data_loader)
    
    inference_model = TrainingModel(script_factory, graph_spec) \
        .as_inference_model(
            data_loader,
            include_preprocessing=True,  # Data is NOT already preprocessed
        )

    y_pred = inference_model(x)

    for target in y_true.keys():
        assert target in y_pred
        assert y_pred[target].dtype == y_true[target].dtype
        assert y_pred[target].shape == y_true[target].shape
        

