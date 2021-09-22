import os
import pytest
import tempfile
import requests

import numpy as np
import pandas as pd
import skimage.io as sk

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.script import ScriptFactory
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, DatasetSettings, Partitions
from perceptilabs.graph.builder import GraphSpecBuilder


import pytest
from unittest.mock import MagicMock
from retrying import retry
import requests
from gradio.inputs import InputComponent
from gradio.outputs import OutputComponent
from gradio.processing_utils import encode_file_to_base64

from perceptilabs.serving.gradio_serving import GradioLauncher


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def wait_for_gradio_up(launcher):
    assert launcher.get_url() is not None
    
    r = requests.head(launcher.get_url(), timeout=3)
    assert r.status_code == 200


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def wait_for_gradio_down(launcher):
    assert launcher.get_url() is not None

    with pytest.raises(requests.exceptions.ConnectionError):
        r = requests.head(launcher.get_url(), timeout=3)


def test_launcher_starts_endpoint():
    model_access = MagicMock()
    
    launcher = GradioLauncher(
        model_access=model_access,
        epochs_access=MagicMock()
    )

    launcher.start(
        graph_spec=MagicMock(),
        data_loader=MagicMock(),
        checkpoint_directory=MagicMock(),
        model_name='my model'                
    )
    wait_for_gradio_up(launcher)

    with pytest.raises(NotImplementedError):
        launcher.stop()  
        # wait_for_gradio_down(launcher)  # TODO: enable when removing not implemented error



INPUT_OUTPUT_CONVERSION_DATA = [
    {'datatype': 'numerical', 'metadata': {}},
    {'datatype': 'image', 'metadata': {'loader': {'n_channels': 1}}},
    {'datatype': 'image', 'metadata': {'loader': {'n_channels': 3}}},
    {'datatype': 'text', 'metadata': {}},
    {'datatype': 'categorical', 'metadata': {'preprocessing': {'mapping': {'cat': 0, 'dog': 2}}}}
]


@pytest.mark.parametrize("data", INPUT_OUTPUT_CONVERSION_DATA)
def test_get_gradio_input_returns_value(data):
    component = GradioLauncher.get_gradio_input(
        feature_name='x',
        datatype=data['datatype'],
        metadata=data['metadata']
    )
    assert isinstance(component, InputComponent)


@pytest.mark.parametrize("data", INPUT_OUTPUT_CONVERSION_DATA)
def test_get_gradio_output_returns_value(data):
    component = GradioLauncher.get_gradio_output(
        feature_name='x',
        datatype=data['datatype'],
        metadata=data['metadata']
    )
    assert isinstance(component, OutputComponent)
    


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

    df = pd.DataFrame({'x1': data['x1']['values'], 'y1': data['y1']['values']})

    feature_specs = {
        'x1': FeatureSpec(iotype='input', datatype=data['x1']['type']),
        'y1': FeatureSpec(iotype='target', datatype=data['y1']['type'])
    }
    partitions = Partitions(training_ratio=1.0, validation_ratio=0.0, test_ratio=0.0)
    
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions,
        file_path=os.path.join(working_dir, 'data.csv')
    )
    
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
    

def test_predictions_endpoint(script_factory, data_loader):
    launcher = GradioLauncher(
        model_access=ModelAccess(script_factory),
        epochs_access=EpochsAccess()
    )
    
    launcher.start(
        graph_spec=make_graph_spec(data_loader),
        data_loader=data_loader,
        checkpoint_directory=None,
        model_name='my model'        
    )
    wait_for_gradio_up(launcher)

    inputs, outputs = data_loader.get_example_batch(
        batch_size=None, output_type='list', apply_pipelines=None)

    data = []
    for value in inputs.values():
        if isinstance(value, (str, bytes)) and os.path.isfile(value):
            encoded_file = encode_file_to_base64(value)                  
            data.append(encoded_file)
        else:
            data.append(value)        

    url = launcher.get_url() + 'api/predict/'
    response = requests.post(url, json={'data': data})

    assert response.status_code == 200
    assert response.json() != {}  # TODO: validate response

    with pytest.raises(NotImplementedError):
        launcher.stop()  
        # wait_for_gradio_down(launcher)  # TODO: enable when removing not implemented error
    
