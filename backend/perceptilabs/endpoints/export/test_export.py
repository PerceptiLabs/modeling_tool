import os
import pytest
import json


from perceptilabs.endpoints.base import create_app
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings
from perceptilabs.exporter.base import Exporter
from perceptilabs.resources.files import FileAccess


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def export_settings(path, type_):
    return {
        "Location": path,
        "Type": type_,
        "name": "Model 36"
    }


@pytest.fixture
def dataset_settings_dict():
    settings = {
        "randomizedPartitions": True,
        "randomSeed": 123,
        "partitions": [
            70,
            20,
            10
        ],
        "filePath": "perceptilabs/endpoints/network_data/test_data.csv",        
        "featureSpecs": {
            "x1": {
                "iotype": "Input",
                "datatype": "numerical",
                "preprocessing": {
                    "resize": {
                        "mode": "automatic",
                        "type": "mode"
                    }
                }
            },
            "y1": {
                "iotype": "Target",
                "datatype": "numerical",
                "preprocessing": {}
            }
        }
    }
    yield settings

@pytest.fixture
def network():
    yield {
        "0": {
            "Name": "Input_1",
            "Type": "IoInput",
            "endPoints": [],
            "Properties": {
                "Type": "IoInput",
                "FeatureName": "x1",
                "DataType": "numerical",
                "testInfoIsInput": True,
                "accessProperties": {
                    "Sources": []
                }
            },
            "Code": None,
            "backward_connections": [],
            "forward_connections": [
                {
                    "src_var": "output",
                    "dst_id": "1",
                    "dst_var": "input"
                }
            ],
            "visited": False,
            "previewVariable": "output",
            "getPreview": True
        },
        "1": {
            "Name": "Dense_1",
            "Type": "DeepLearningFC",
            "endPoints": [],
            "Properties": {
                "Activation_function": "None",
                "Batch_norm": False,
                "Dropout": False,
                "Keep_prob": 0,
                "Neurons": 3
            },
            "Code": None,
            "backward_connections": [
                {
                    "src_id": "0",
                    "src_var": "output",
                    "dst_var": "input"
                }
            ],
            "forward_connections": [
                {
                    "src_var": "output",
                    "dst_id": "2",
                    "dst_var": "input"
                }
            ],
            "visited": False,
            "previewVariable": "output",
            "getPreview": True
        },
        "2": {
            "Name": "Target_1",
            "Type": "IoOutput",
            "endPoints": [],
            "Properties": {
                "Type": "IoInput",
                "FeatureName": "y1",
                "DataType": "categorical",
                "testInfoIsInput": True,
                "accessProperties": {
                    "Sources": []
                }
            },
            "Code": None,
            "backward_connections": [
                {
                    "src_id": "1",
                    "src_var": "output",
                    "dst_var": "input"
                }
            ],
            "forward_connections": [],
            "visited": False,
            "previewVariable": "output",
            "getPreview": True
        }
    }


@pytest.fixture
def checkpoint_directory(temp_path):
    yield os.path.join(temp_path, 'checkpoint')


@pytest.fixture(scope="function", params=["Standard", "Compressed", 'Quantized'])
def basic_request(request, dataset_settings_dict, temp_path, network, checkpoint_directory):
    yield {
        "exportSettings": export_settings(temp_path, request.param),
        "datasetSettings": dataset_settings_dict,
        "network": network,
        "checkpointDirectory": checkpoint_directory
    }


def create_model_checkpoint(dataset_settings_dict, network, checkpoint_directory, script_factory):
    csv_path = dataset_settings_dict['filePath']  # TODO: move one level up
    file_access = FileAccess(os.path.dirname(csv_path)) 
    
    dataset_settings = DatasetSettings.from_dict(dataset_settings_dict)    
    data_loader = DataLoader.from_csv(file_access, csv_path, dataset_settings)
    graph_spec = GraphSpec.from_dict(network)
    training_model = TrainingModel(script_factory, graph_spec)

    checkpoint_path = os.path.join(checkpoint_directory, "checkpoint-0001.ckpt")
    exporter = Exporter(graph_spec, training_model, data_loader)
    exporter.export_checkpoint(checkpoint_path)


def test_basic(client, basic_request, dataset_settings_dict, network, checkpoint_directory, script_factory):
    create_model_checkpoint(dataset_settings_dict, network, checkpoint_directory, script_factory)
    response = client.post('/export', json=basic_request)
    assert (response.json.startswith("Model exported to ") or response.json.startswith("Model not compatible"))


def test_try_to_export_without_training(client, basic_request, dataset_settings_dict, network, checkpoint_directory, script_factory):
    response = client.post('/export', json=basic_request)
    assert response.json == "Cannot export an untrained model. Make sure to run training first."


