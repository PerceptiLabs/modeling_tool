import os
import pytest
import tempfile

import tensorflow as tf
import numpy as np
import pandas as pd
import skimage.io as sk
from fastapi.testclient import TestClient

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.script import ScriptFactory
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, DatasetSettings, Partitions
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.exporter.base import Exporter
import perceptilabs.exporter.fastapi_utils as fastapi_utils


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


@pytest.fixture(params=[data0, data1, data2])
def data_loader(request, temp_path):
    yield make_data_loader(request.param, temp_path)

    
@pytest.fixture(params=[data0, data1])
def data_loader_except_image(request, temp_path):
    yield make_data_loader(request.param, temp_path)
    

@pytest.fixture()
def data_loader_numerical(temp_path):
    yield make_data_loader(data0, temp_path)

    
@pytest.fixture()
def data_loader_categorical(temp_path):
    yield make_data_loader(data1, temp_path)    


@pytest.fixture()
def data_loader_image(temp_path):
    yield make_data_loader(data2, temp_path)    
    

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


def equal_layer_outputs(dict1, dict2):
    """ Checks if two layers have equal output """
    if dict1.keys() != dict2.keys():
        return False

    for var_name in dict1.keys():
        values1 = dict1[var_name].numpy()
        values2 = dict2[var_name].numpy()

        if not np.all(values1 == values2):
            return False

    return True


def equal_training_model_outputs(all1, all2):
    """ Checks if two training models have equal output """
    output1, hidden1 = all1
    output2, hidden2 = all2

    if not equal_layer_outputs(output1, output2):
        return False

    if hidden1.keys() != hidden2.keys():
        return False

    for layer_id in hidden1.keys():
        if not equal_layer_outputs(hidden1[layer_id], hidden2[layer_id]):
            return False

    return True


def has_inference_model(target_dir):
    return (
        os.path.isfile(os.path.join(target_dir, 'saved_model.pb')) and
        os.path.isdir(os.path.join(target_dir, 'variables')) and 
        os.path.isdir(os.path.join(target_dir, 'assets'))
    )


def module_from_path(module_path, module_name='my_module'):
    import sys    
    import importlib
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module 
    spec.loader.exec_module(module)
    return module


def test_create_exporter_from_graph(script_factory, data_loader, temp_path):
    # Use data loader to feed data through the model
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)
    assert exporter is not None


def test_export_inference_model(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)    
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)

    target_dir = os.path.join(temp_path, 'inference_model')
    assert not os.path.isdir(target_dir)

    exporter.export(target_dir, mode='Standard')

    assert has_inference_model(target_dir)

    
def test_export_compressed_model(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)        
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)

    target_dir = os.path.join(temp_path, 'inference_model')
    assert not os.path.isdir(target_dir)

    exporter.export(target_dir, mode='Compressed')

    assert os.path.isfile(os.path.join(target_dir, 'model.tflite'))


def test_export_quantized_model(script_factory, data_loader_numerical, temp_path):
    graph_spec = make_graph_spec(data_loader_numerical)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_numerical)

    target_dir = os.path.join(temp_path, 'inference_model')
    assert not os.path.isdir(target_dir)

    output = exporter.export(target_dir, mode='Quantized')
    assert (os.path.isfile(os.path.join(target_dir, 'quantized_model.tflite')) or output)

    
def test_export_checkpoint_creates_files(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)
    target_dir = os.path.join(temp_path, 'checkpoint_dir')
    assert not os.path.isdir(target_dir)
    assert tf.train.latest_checkpoint(target_dir) is None

    exporter.export_checkpoint(target_dir)
    ckpt = tf.train.latest_checkpoint(target_dir)
    assert ckpt is not None
    training_model.load_weights(ckpt).assert_consumed()


def test_export_checkpoint_creates_multiple_files(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)

    target_dir = os.path.join(temp_path, 'checkpoint_dir')
    assert not os.path.isdir(target_dir)
    assert tf.train.latest_checkpoint(target_dir) is None

    exporter.export_checkpoint(target_dir, epoch=0)
    first_ckpt = tf.train.latest_checkpoint(target_dir)
    assert first_ckpt is not None
    training_model.load_weights(first_ckpt).assert_consumed()

    exporter.export_checkpoint(target_dir, epoch=1)
    second_ckpt = tf.train.latest_checkpoint(target_dir)
    assert second_ckpt is not None
    assert second_ckpt != first_ckpt

    training_model.load_weights(second_ckpt).assert_consumed() # Make sure weights can be loaded
    training_model.load_weights(first_ckpt).assert_consumed() # Make sure 1st ckpt is still valid


def test_loading_different_checkpoints_consistent_results(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)

    exporter = Exporter(graph_spec, training_model, data_loader)
    target_dir = os.path.join(temp_path, 'checkpoint_dir')

    inputs, targets = data_loader.get_example_batch(2)

    # Infer and export for epoch 0
    expected_output_epoch_0 = training_model(inputs)
    exporter.export_checkpoint(target_dir, epoch=0)
    ckpt_epoch_0 = tf.train.latest_checkpoint(target_dir)

    # Update the weights with random values to simulate a new epoch
    epoch_0_weights = training_model.get_weights()
    epoch_1_weights = [np.random.random() * w for w in epoch_0_weights]
    training_model.set_weights(epoch_1_weights)

    # Infer and export for epoch 1
    expected_output_epoch_1 = training_model(inputs)
    exporter.export_checkpoint(target_dir, epoch=1)
    ckpt_epoch_1 = tf.train.latest_checkpoint(target_dir)

    # Check that two different checkpoints exist
    assert ckpt_epoch_0 != ckpt_epoch_1

    # Load weights from epoch 0 and check consistent output
    training_model.load_weights(ckpt_epoch_0)
    actual_output_epoch_0 = training_model(inputs)
    assert equal_training_model_outputs(
        actual_output_epoch_0, expected_output_epoch_0)

    # Load weights from epoch 1 and check consistent output
    training_model.load_weights(ckpt_epoch_1)
    actual_output_epoch_1 = training_model(inputs)
    assert equal_training_model_outputs(
        actual_output_epoch_1, expected_output_epoch_1)

    # Check that the models produced different outputs for each epoch
    assert not equal_training_model_outputs(actual_output_epoch_0, actual_output_epoch_1)
    assert not equal_training_model_outputs(expected_output_epoch_0, expected_output_epoch_1)


def test_restore_model_from_disk(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    # Use data loader to feed data through the model
    training_model = TrainingModel(script_factory, graph_spec)
    x = {'x1': np.array([1.0, 2.0, 3.0])}
    expected = training_model(x)

    exporter = Exporter(graph_spec, training_model, data_loader)

    exporter.export_checkpoint(temp_path)
    assert len(os.listdir(temp_path)) > 0

    # Create an equivalent model using the checkpoint
    exporter = Exporter.from_disk(
        temp_path, graph_spec, script_factory, data_loader)
    assert exporter is not None

    loaded_training_model = exporter.training_model
    assert loaded_training_model != training_model

    actual = loaded_training_model(x)
    assert (actual[0]['y1'] == expected[0]['y1']).numpy().all()
    assert (actual[1]['1']['output'] == \
            expected[1]['1']['output']).numpy().all()

    
def test_inference_outputs_numerical(script_factory, data_loader_numerical):
    graph_spec = make_graph_spec(data_loader_numerical)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_numerical)
    inference_model = exporter.get_inference_model()

    x = {'x1': np.array([1.0, 2.0, 3.0])}
    y = inference_model(x)

    assert y['y1'].dtype == tf.float32
    assert y['y1'].shape == (3,)


def test_inference_retains_batch_size(script_factory, data_loader_except_image):
    graph_spec = make_graph_spec(data_loader_except_image)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_except_image)
    inference_model = exporter.get_inference_model()

    for batch_size in range(1, 4):
        inputs_batch, targets_batch = data_loader_except_image \
            .get_example_batch(batch_size, apply_pipelines=None)
        
        assert targets_batch['y1'].shape[0] == inputs_batch['x1'].shape[0]        
        
        outputs_batch = inference_model(inputs_batch)
        assert outputs_batch['y1'].shape[0] == inputs_batch['x1'].shape[0]

    
def test_inference_outputs_categorical(script_factory, data_loader_categorical):
    graph_spec = make_graph_spec(data_loader_categorical)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_categorical)
    inference_model = exporter.get_inference_model()

    x = {'x1': np.array(['cat', 'dog', 'house'])}
    y = inference_model(x)

    for prediction in y['y1'].numpy():  # Loop over each prediction in batch
        assert prediction in [b'animal', b'non-animal']


def test_inference_takes_matrix_input(script_factory, data_loader_image):
    graph_spec = make_graph_spec(data_loader_image)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_image)
    inference_model = exporter.get_inference_model()

    x = {'x1': np.random.random((5, 16, 16, 3))}
    y = inference_model(x)

    for prediction in y['y1'].numpy():  # Loop over each prediction in batch
        assert prediction in [b'animal', b'non-animal']

        
def test_export_fastapi_files_are_present(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)


    required_files = [
        fastapi_utils.SCRIPT_FILE,
        fastapi_utils.REQUIREMENTS_FILE,
        fastapi_utils.EXAMPLE_REQUIREMENTS_FILE,
        fastapi_utils.EXAMPLE_JSON_FILE,        
        fastapi_utils.EXAMPLE_SCRIPT_FILE,
        fastapi_utils.EXAMPLE_CSV_FILE
    ]
    
    assert not has_inference_model(temp_path)        
    for file_name in required_files:
        assert not os.path.isfile(os.path.join(temp_path, file_name))
        
    exporter.export(temp_path, mode='FastAPI')

    assert has_inference_model(temp_path)        
    for file_name in required_files:
        assert os.path.isfile(os.path.join(temp_path, file_name))

def test_export_fastapi_endpoint_healthy(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)
    exporter.export(temp_path, mode='FastAPI')

    module = module_from_path(os.path.join(temp_path, fastapi_utils.SCRIPT_FILE))

    app = module.create_app()
    client = TestClient(app)

    response = client.get("/healthy")
    assert response.status_code == 200
    assert response.json() == {"healthy": True}


@pytest.mark.parametrize("data", [data0, data1, data2, data3])
def test_export_fastapi_endpoint_predict(data, script_factory, temp_path):
    data_loader = make_data_loader(data, temp_path)
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)
    exporter.export(temp_path, mode='FastAPI')
    
    
    module = module_from_path(os.path.join(temp_path, fastapi_utils.SCRIPT_FILE))
    app = module.create_app()
    client = TestClient(app)

    def make_payload(dict_):
        payload = {}
        for feature, tensor in dict_.items():
            def f(x):
                if isinstance(x, bytes):
                    x = x.decode()
                return x

            payload[feature] = [f(x) for x in tensor.numpy().tolist()]
        return payload
    
    inference_model = exporter.get_inference_model()
    for batch_size in [1, 3]:
        x, _ = data_loader.get_example_batch(batch_size=batch_size, apply_pipelines='loader')
        y_expected = make_payload(inference_model(x))

        response = client.post("/predict", json=make_payload(x))
        y_actual = response.json()
        
        assert response.status_code == 200
        assert y_actual == y_expected

        
@pytest.mark.parametrize("data", [data0, data1, data2, data3])
def test_export_fastapi_endpoint_predict_using_example_script(data, script_factory, temp_path):
    data_loader = make_data_loader(data, temp_path)
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)
    exporter.export(temp_path, mode='FastAPI')

    server_module = module_from_path(os.path.join(temp_path, fastapi_utils.SCRIPT_FILE))
    app = server_module.create_app()
    client = TestClient(app)

    example_module = module_from_path(os.path.join(temp_path, fastapi_utils.EXAMPLE_SCRIPT_FILE))
    data = example_module.make_payload()
    response = client.post("/predict", json=data).json()
    
    batch_size = len(next(iter(data.values())))  #  length of arbitrary feature vector
    _, targets = data_loader.get_example_batch(batch_size=batch_size, apply_pipelines='loader')

    for feature_name in response.keys():
        assert np.shape(response[feature_name]) == np.shape(targets[feature_name])
    

    
