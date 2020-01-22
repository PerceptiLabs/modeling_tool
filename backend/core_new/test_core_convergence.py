import sys
import time
import pytest
import tempfile
import numpy as np
from queue import Queue

from code.factory import ScriptFactory
from core_new.core2 import Core
from core_new.graph.builder import ReplicatedGraphBuilder
from core_new.graph import Graph
from core_new.layers import TrainingLayer
from core_new.deployment import InProcessDeploymentPipe
from core_new.layers.communication import ZmqClient

@pytest.fixture
def graph_spec_binary_classification():
    n_classes = 10
    n_samples = 30

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy')
    mat = np.random.random((n_samples, 28*28*1))
    np.save(f1.name, mat)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy')
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = f1.name
    labels_path = f2.name    

    json_network = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Batch_size": 8,
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": ["3"],
                "Code": ""
            },
            "2": {
                "Name": "data_labels",
                "Type": "DataData",
                "Properties": {
                    "Type": "DataData",
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": labels_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Batch_size": 8,
                        "Shuffle_data": False,
                        "Columns": []
                    },
                },
                "backward_connections": [],
                "forward_connections": ["5"],
                "Code": ""
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": ["1"],
                "forward_connections": ["4"],
                "Code": ""
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1"
                },
                "backward_connections": ["3"],
                "forward_connections": ["6"],
                "Code": ""
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": ["2"],
                "forward_connections": ["6"],
                "Code": ""
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": "100",
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "ADAM",
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Learning_rate": "0.001",
                    "Distributed": False
                },
                "backward_connections": ["4", "5"],
                "forward_connections": [],
                "Code": ""
            }
        }
    }

    yield json_network

    f1.close()
    f2.close()

    

@pytest.mark.slow
def test_train_normal_converges(graph_spec_binary_classification):
    
    script_factory = ScriptFactory()
    deployment_pipe = InProcessDeploymentPipe(interpreter=sys.executable,
                                              script_factory=script_factory)

    graph_builder = ReplicatedGraphBuilder(client=None)    
    command_queue = Queue()
    result_queue = Queue()
    #client.start()
    
    core = Core(
        graph_builder,
        deployment_pipe,
        command_queue,
        result_queue,
    )

    core.run(graph_spec_binary_classification)

    time.sleep(5)
    accuracy = core.graph.nodes[-1].layer.accuracy_training
    assert np.isclose(accuracy[-1], 1.000, atol=0.001)

    
    core.stop()    
