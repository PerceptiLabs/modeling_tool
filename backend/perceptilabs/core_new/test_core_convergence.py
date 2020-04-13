import sys
import time
import pytest
import logging
import tempfile
import numpy as np
from queue import Queue
from shutil import copyfile
import os

from perceptilabs.core_new.layers.script import ScriptFactory
from perceptilabs.core_new.core2 import Core
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.layers import TrainingLayer
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP
from perceptilabs.core_new.deployment import InProcessDeploymentPipe, LocalEnvironmentPipe


logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                    level=logging.DEBUG)


@pytest.fixture
def graph_spec_binary_classification():
    n_classes = 10
    n_samples = 30

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.random((n_samples, 28*28*1))
    np.save(f1.name, mat)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = f1.name.replace("\\","/")
    labels_path = f2.name.replace("\\","/")    

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
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
                "forward_connections": [["3", "reshape"]],
                "Code": None,
                "checkpoint": []
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
                "forward_connections": [["5", "one_hot"]],
                "Code": None,
                "checkpoint": []
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [["1", "data_inputs"]],
                "forward_connections": [["4", "fc"]],
                "Code": None,
                "checkpoint": []
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
                "backward_connections": [["3", "reshape"]],
                "forward_connections": [["6", "training"]],
                "Code": None,
                "checkpoint": []
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [["2", "data_labels"]],
                "forward_connections": [["6", "training"]],
                "Code": None,
                "checkpoint": []
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 200,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Learning_rate": "0.05",
                    "Distributed": False
                },
                "backward_connections": [["4", "fc"], ["5", "one_hot"]],
                "forward_connections": [],
                "Code": None,
                "checkpoint": []
            }
        }
    }

    yield json_network

    f1.close()
    f2.close()

class FileCopier():
    def __init__(self, to_name):
        self.to_name = to_name

    def copy_train_script(self, original_name):
        if not os.path.isdir('./training_scripts'):
            os.mkdir('./training_scripts')
        
        copyfile(original_name, os.path.join('./training_scripts/',self.to_name))
        print("training_script has been saved")

#Disabling these tests while intermittent failures are being worked on

@pytest.mark.slow
def test_train_normal_converges(graph_spec_binary_classification):
    script_factory = ScriptFactory()
    file_copier = FileCopier('train_normal_training_script.py')
    deployment_pipe = InProcessDeploymentPipe(script_factory, file_copier.copy_train_script)
    #deployment_pipe = LocalEnvironmentPipe('/home/anton/Source/perceptilabs/backend/venv-user/bin/python', script_factory)    

    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
    graph_builder = GraphBuilder(replica_by_name)    
    
    core = Core(
        graph_builder,
        deployment_pipe,
    )

    core.run(graph_spec_binary_classification)

    #print("POST RUN CALL")
    
    while core.is_running:

        #graphs = core.graphs
        #print("aaaa", graph)
        #print(graph.active_training_node.layer.layer_gradients.keys())
    
        time.sleep(1)


    accuracy_list = []
    for graph in core.graphs:
        acc = graph.active_training_node.layer.accuracy_training
        accuracy_list.append(acc)

    print("Accuracy: ", np.mean(accuracy_list[-10:]))
    
    assert np.mean(accuracy_list[-10:]) >= 0.75


@pytest.mark.slow
def test_train_normal_distributed_converges(graph_spec_binary_classification):
    script_factory = ScriptFactory()
    file_copier = FileCopier('train_normal_distr_training_script.py')
    deployment_pipe = InProcessDeploymentPipe(script_factory, file_copier.copy_train_script)
    #deployment_pipe = LocalEnvironmentPipe('/home/anton/Source/perceptilabs/backend/venv-user/bin/python', script_factory)    

    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
    graph_builder = GraphBuilder(replica_by_name)    
    
    core = Core(
        graph_builder,
        deployment_pipe,
    )

    json_network = graph_spec_binary_classification
    json_network['Layers']['6']['Properties']['Distributed'] = True

    core.run(json_network)

    #print("POST RUN CALL")
    
    while core.is_running:

        #graphs = core.graphs
        #print("aaaa", graph)
        #print(graph.active_training_node.layer.layer_gradients.keys())
    
        time.sleep(1)


    accuracy_list = []
    for graph in core.graphs:
        acc = graph.active_training_node.layer.accuracy_training
        accuracy_list.append(acc)
        #print(acc)
    
    assert np.mean(accuracy_list[-10:]) >= 0.75

