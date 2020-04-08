import pytest
import tempfile
import numpy as np


from perceptilabs.core_new.lightweight2 import LightweightCore
from perceptilabs.utils import sanitize_path


@pytest.fixture(scope='function')
def graph_spec_binary_classification():
    n_classes = 10
    n_samples = 30

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.random((n_samples, 28*28*1))
    np.save(f1.name, mat)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

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


def test_out_shapes_ok(graph_spec_binary_classification):
    lw_core = LightweightCore()
    results, instance_errors, strategy_errors = lw_core.run(graph_spec_binary_classification)
 
    assert results['1'].out_shape == (784,) # Datadata inputs
    assert results['2'].out_shape == (1,) # Datadata labels
    assert results['3'].out_shape == (28, 28, 1) # Reshape
    assert results['4'].out_shape == (10,) # FC
    assert results['5'].out_shape == (10,) # One hot
    assert results['6'].out_shape is None

    
def test_out_shapes_ok_partial_graph(graph_spec_binary_classification):
    del graph_spec_binary_classification['Layers']['2']['Properties']['accessProperties']
    
    lw_core = LightweightCore()
    results, instance_errors, strategy_errors = lw_core.run(graph_spec_binary_classification)
 
    assert results['1'].out_shape == (784,) # Datadata inputs
    assert results['2'].out_shape == None # Datadata labels
    assert results['3'].out_shape == (28, 28, 1) # Reshape
    assert results['4'].out_shape == (10,) # FC
    assert results['5'].out_shape == None # One hot
    assert results['6'].out_shape is None
    

def test_out_shapes_ok_with_syntax_error(graph_spec_binary_classification):
    code  = "print('hello')\n"
    code += "!!!" # Bad syntax
    graph_spec_binary_classification['Layers']['3']['Code'] = {"Output": code}
    
    lw_core = LightweightCore()
    results, instance_errors, strategy_errors = lw_core.run(graph_spec_binary_classification)
 
    assert results['1'].out_shape == (784,) # Datadata inputs
    assert results['2'].out_shape == (1,) # Datadata labels
    assert results['3'].out_shape == None # Reshape
    assert results['4'].out_shape == None # FC
    assert results['5'].out_shape == (10,) # One hot
    assert results['6'].out_shape is None


def test_errors_ok_with_syntax_error(graph_spec_binary_classification):
    code  = "print('hello')\n"
    code += "!!!" # Bad syntax
    graph_spec_binary_classification['Layers']['3']['Code'] = {"Output": code}
    
    lw_core = LightweightCore()
    results, instance_errors, strategy_errors = lw_core.run(graph_spec_binary_classification)

    assert instance_errors['3'].line_number == 2


def test_out_shapes_ok_with_runtime_error(graph_spec_binary_classification):
    code  = "print('hello')\n"
    code += "1/0" # Will generate runtime error
    graph_spec_binary_classification['Layers']['3']['Code'] = {"Output": code}
    
    lw_core = LightweightCore()
    results, instance_errors, strategy_errors = lw_core.run(graph_spec_binary_classification)
 
    assert results['1'].out_shape == (784,) # Datadata inputs
    assert results['2'].out_shape == (1,) # Datadata labels
    assert results['3'].out_shape == None # Reshape
    assert results['4'].out_shape == None # FC
    assert results['5'].out_shape == (10,) # One hot
    assert results['6'].out_shape is None
    

def test_errors_ok_with_runtime_error(graph_spec_binary_classification):
    code  = "print('hello')\n"
    code += "1/0" # Will generate runtime error
    graph_spec_binary_classification['Layers']['3']['Code'] = {"Output": code}
    
    lw_core = LightweightCore()
    results, instance_errors, strategy_errors = lw_core.run(graph_spec_binary_classification)

    assert '3' in instance_errors


def test_errors_detected_in_training_layer(graph_spec_binary_classification):
    code  = "print('hello')\n"
    code += "1/0" # Will generate runtime error
    graph_spec_binary_classification['Layers']['6']['Code'] = {"Output": code}
    
    lw_core = LightweightCore()
    results, instance_errors, strategy_errors = lw_core.run(graph_spec_binary_classification)

    assert '6' in instance_errors

    
