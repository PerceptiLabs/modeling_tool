import pytest
import pandas as pd
import tempfile
import numpy as np
from unittest.mock import MagicMock


from perceptilabs.lwcore import LightweightCore
from perceptilabs.utils import sanitize_path
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.layers.iooutput.spec import OutputLayerSpec
from perceptilabs.layers.ioinput.spec import InputLayerSpec
from perceptilabs.layers.iooutput.spec import OutputLayerSpec


@pytest.fixture(scope='function')
def graph_spec_binary_classification(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
    checkpoint_path = temp_path_checkpoints
    graph_spec_json = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "2": {
                "Name": "data_labels",
                "Type": "DataData",
                "Properties": {
                    "Type": "DataData",
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": labels_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "5",
                        "dst_name": "one_hot",                        
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [
                    {
                        "src_id": "2",
                        "src_name": "data_labels",
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 50,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Batch_size": 10,                    
                    "Learning_rate": "0.05",
                    "Distributed": False,
                    "Stop_condition": "Epochs"
                },
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            }
        }
    }


    graph_spec = GraphSpec.from_dict(graph_spec_json)
    yield graph_spec

    f1.close()
    f2.close()


@pytest.fixture(scope='function')
def graph_spec_partial(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
    checkpoint_path = temp_path_checkpoints
    graph_spec_json = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 50,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Batch_size": 10,                    
                    "Learning_rate": "0.05",
                    "Distributed": False,
                    "Stop_condition": "Epochs"
                },
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            }
        }
    }


    graph_spec = GraphSpec.from_dict(graph_spec_json)
    yield graph_spec

    f1.close()
    f2.close()

@pytest.fixture(scope='function')
def graph_spec_syntax_error(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
    checkpoint_path = temp_path_checkpoints
    graph_spec_json = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "2": {
                "Name": "data_labels",
                "Type": "DataData",
                "Properties": {
                    "Type": "DataData",
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": labels_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "5",
                        "dst_name": "one_hot",                        
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
                "Code": {"Output": "print('hello')\n!!!"},
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [
                    {
                        "src_id": "2",
                        "src_name": "data_labels",
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 50,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Batch_size": 10,                    
                    "Learning_rate": "0.05",
                    "Distributed": False,
                    "Stop_condition": "Epochs"
                },
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            }
        }
    }


    graph_spec = GraphSpec.from_dict(graph_spec_json)
    yield graph_spec

    f1.close()
    f2.close()
    
@pytest.fixture(scope='function')
def graph_spec_runtime_error(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
    checkpoint_path = temp_path_checkpoints
    graph_spec_json = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "2": {
                "Name": "data_labels",
                "Type": "DataData",
                "Properties": {
                    "Type": "DataData",
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": labels_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "5",
                        "dst_name": "one_hot",                        
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
                "Code": {"Output": "print('hello')\n1/0"},
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [
                    {
                        "src_id": "2",
                        "src_name": "data_labels",
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 50,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Batch_size": 10,                    
                    "Learning_rate": "0.05",
                    "Distributed": False,
                    "Stop_condition": "Epochs"
                },
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            }
        }
    }


    graph_spec = GraphSpec.from_dict(graph_spec_json)
    yield graph_spec

    f1.close()
    f2.close()
    
@pytest.fixture(scope='function')
def graph_spec_runtime_error_training(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
    checkpoint_path = temp_path_checkpoints
    graph_spec_json = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "2": {
                "Name": "data_labels",
                "Type": "DataData",
                "Properties": {
                    "Type": "DataData",
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": labels_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []
                    },
                },
                "backward_connections": [],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "5",
                        "dst_name": "one_hot",                        
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [
                    {
                        "src_id": "2",
                        "src_name": "data_labels",
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 50,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Batch_size": 10,                    
                    "Learning_rate": "0.05",
                    "Distributed": False,
                    "Stop_condition": "Epochs"
                },
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": {"Output": "print('hello')\n1/0"},
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            }
        }
    }


    graph_spec = GraphSpec.from_dict(graph_spec_json)
    yield graph_spec

    f1.close()
    f2.close()
    

@pytest.fixture(scope='function')
def graph_spec_binary_classification_with_strings(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    #f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    #mat = np.random.random((n_samples, 28*28*1))
    #np.save(f1.name, mat)

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    mat = np.random.random((n_samples, 784))
    df = pd.DataFrame.from_records(mat, columns=['col_'+str(x) for x in range(784)])
    
    df['col_0'] = df['col_0'].astype(str)
    df['col_0'].iloc[0] = 'abcd1234' # this cannot be casted to float32
    
    df.to_csv(f1.name, index=False)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
    checkpoint_path = temp_path_checkpoints 
    graph_spec_json = {
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "5",
                        "dst_name": "one_hot",                        
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [
                    {
                        "src_id": "2",
                        "src_name": "data_labels",
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
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
                    "Batch_size": 10,                    
                    "Learning_rate": "0.05",
                    "Distributed": False,
                    "Stop_condition": "Epochs"
                },
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            }
        }
    }

    graph_spec = GraphSpec.from_dict(graph_spec_json)
    yield graph_spec

    f1.close()
    f2.close()
    


@pytest.fixture(scope='function')
def graph_spec_binary_classification_3d(temp_path_checkpoints):
    n_classes = 10
    n_samples = 30

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.random((n_samples, 28, 28, 3))
    np.save(f1.name, mat)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = sanitize_path(f1.name)
    labels_path = sanitize_path(f2.name)

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
    checkpoint_path = temp_path_checkpoints
    
    graph_spec_json = {
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "5",
                        "dst_name": "one_hot",                        
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [2352, 1, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [
                    {
                        "src_id": "2",
                        "src_name": "data_labels",
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
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
                    "Batch_size": 10,                    
                    "Learning_rate": "0.05",
                    "Distributed": False,
                    "Stop_condition": "Epochs"
                },
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": None,
                "checkpoint": {'path': checkpoint_path, 'load_checkpoint':False}
            }
        }
    }

    graph_spec = GraphSpec.from_dict(graph_spec_json)
    yield graph_spec


    f1.close()
    f2.close()



    

def test_out_shapes_ok_basic(graph_spec_binary_classification):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_binary_classification)
 
    assert results['1'].out_shape['output'] == (784,) # Datadata inputs
    assert results['2'].out_shape['output'] == (1,) # Datadata labels
    assert results['3'].out_shape['output'] == (28, 28, 1) # Reshape
    assert results['4'].out_shape['output'] == (10,) # FC
    assert results['5'].out_shape['output'] == (10,) # One hot
    assert results['6'].out_shape['output'] == (1,)


def test_columns_ok_lw(graph_spec_binary_classification):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_binary_classification)

    assert results['1'].columns == [f'col_{x}' for x in range(784)]

    
def test_columns_ok_when_some_columns_are_strings(graph_spec_binary_classification_with_strings):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_binary_classification_with_strings)

    assert "ValueError" in results['1'].strategy_error.message # make sure the layer failed in part    
    assert results['1'].columns == [f'col_{x}' for x in range(len(results['1'].columns))]


def test_variables_are_present(graph_spec_binary_classification):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_binary_classification)


    assert len(results['1'].variables) > 0 # data layer has vars
    assert len(results['4'].variables) > 0 # fc layer has vars   

    
def test_out_shapes_ok_for_3d_samples(graph_spec_binary_classification_3d):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_binary_classification_3d)
 
    assert results['1'].out_shape['output'] == (28, 28, 3) # Datadata inputs
    assert results['2'].out_shape['output'] == (1,) # Datadata labels
    assert results['3'].out_shape['output'] == (2352, 1, 1) # Reshape
    assert results['4'].out_shape['output'] == (10,) # FC
    assert results['5'].out_shape['output'] == (10,) # One hot
    assert results['6'].out_shape['output'] == (1,) # Train normal


def test_out_shapes_ok_partial_graph(graph_spec_partial):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_partial)
 
    assert results['1'].out_shape['output'] == (784,) # Datadata inputs
    assert '2' not in results # Datadata labels
    assert results['3'].out_shape['output'] == (28, 28, 1) # Reshape
    assert results['4'].out_shape['output'] == (10,) # FC
    assert results['5'].out_shape == {} # One hot
    assert results['6'].out_shape['output'] == None # Train normal
    

def test_out_shapes_ok_with_syntax_error(graph_spec_syntax_error):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_syntax_error)
 
    assert results['1'].out_shape['output'] == (784,) # Datadata inputs
    assert results['2'].out_shape['output'] == (1,) # Datadata labels
    assert results['3'].out_shape == {} # Reshape
    assert results['4'].out_shape == {} # FC
    assert results['5'].out_shape['output'] == (10,) # One hot
    assert results['6'].out_shape['output'] == None  # Train normal


def test_errors_ok_with_syntax_error(graph_spec_syntax_error):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_syntax_error)

    assert "SyntaxError" in results['3'].code_error.message


def test_out_shapes_ok_with_runtime_error(graph_spec_runtime_error):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_runtime_error)
 
    assert results['1'].out_shape['output'] == (784,) # Datadata inputs
    assert results['2'].out_shape['output'] == (1,) # Datadata labels
    assert results['3'].out_shape == {} # Reshape
    assert results['4'].out_shape == {} # FC
    assert results['5'].out_shape['output'] == (10,) # One hot
    assert results['6'].out_shape['output'] == None 
    

def test_errors_ok_with_runtime_error(graph_spec_runtime_error):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_runtime_error)

    assert "ZeroDivisionError" in results['3'].instantiation_error.message
    assert results['3'].instantiation_error.line_number == 2

    
def test_errors_detected_in_training_layer(graph_spec_runtime_error_training):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_runtime_error_training)

    assert "ZeroDivisionError" in results['6'].instantiation_error.message        
    assert results['6'].instantiation_error.line_number == 2    

    
def test_load_checkpoints_ok(graph_spec_binary_classification):
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec_binary_classification)

    assert results['1'].trained == False
    assert results['2'].trained == False
    assert results['3'].trained == False
    assert results['4'].trained == False
    assert results['5'].trained == False
    assert results['6'].trained == False

    
def test_calls_cache_get_when_cached_entry_exists(graph_spec_binary_classification):
    cache = MagicMock()
    cache.__contains__.return_value = True
    
    lw_core = LightweightCore(cache=cache)
    results = lw_core.run(graph_spec_binary_classification)

    assert cache.get.call_count > 0

    
def test_calls_cache_put_when_cached_entry_exists(graph_spec_binary_classification):
    cache = MagicMock()
    cache.__contains__.return_value = False
    
    lw_core = LightweightCore(cache=cache)
    results = lw_core.run(graph_spec_binary_classification)

    assert cache.put.call_count > 0

    
@pytest.mark.tf2x    
def test_preview_available_for_output_layer(csv_path):
    layer_spec = OutputLayerSpec(id_='123', feature_name='x1', file_path=csv_path)
    graph_spec = GraphSpec([layer_spec])
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec)
    assert results['123'].sample.get('output') == 1.0
    

@pytest.mark.tf2x    
def test_preview_available_for_input_layer(csv_path):
    layer_spec = InputLayerSpec(id_='123', feature_name='x1', file_path=csv_path)
    graph_spec = GraphSpec([layer_spec])
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec)
    assert results['123'].sample.get('output') == 1.0
    

@pytest.mark.tf2x    
def test_preview_available_for_output_layer(csv_path):
    layer_spec = OutputLayerSpec(id_='123', feature_name='x1', file_path=csv_path)
    graph_spec = GraphSpec([layer_spec])
    lw_core = LightweightCore()
    results = lw_core.run(graph_spec)
    assert results['123'].sample.get('output') == 1.0
    
