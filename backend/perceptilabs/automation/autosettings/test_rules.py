import pytest
import tempfile
import numpy as np

from perceptilabs.lwcore import LightweightCore
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.automation.autosettings import SettingsEngine
import perceptilabs.automation.autosettings.rules as rules


@pytest.fixture
def graph_spec(temp_path_checkpoints):
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
    
    checkpoint_path = temp_path_checkpoints
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
                "Code": None,
                "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False },
                "endPoints": []               
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
                "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False },
                "endPoints": [],                
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [12, 1, 3],
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
                        "dst_id": "3.1",
                        "dst_name": "conv1",
                        "dst_var": "input"
                    }
                ],                
                "Code": None,
                "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False },
                "endPoints": [],                
            },
            "3.1": {
                "Name": "conv1",
                "Type": "DeepLearningConv",
                "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False },
                "endPoints": [],
                "Properties": {
                    "Conv_dim": "2D",
                    "Patch_size": "3",
                    "Stride": "2",
                    "Padding": "SAME",
                    "Feature_maps": "8",
                    "Activation_function": "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False,
                    "PoolBool": False,
                    "Pooling": "Max",
                    "Pool_area": "2",
                    "Pool_padding": "SAME",
                    "Pool_stride": "2"
                },
                "Code": None,
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
                        "dst_id": "3.2",
                        "dst_name": "conv2",
                        "dst_var": "input"
                    }
                ]
            },

            "3.2": {
                "Name": "conv2",
                "Type": "DeepLearningConv",
                "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False },
                "endPoints": [],
                "Properties": {
                    "Conv_dim": "2D",
                    "Patch_size": "3",
                    "Stride": "2",
                    "Padding": "SAME",
                    "Feature_maps": "8000",
                    "Activation_function": "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False,                    
                    "PoolBool": False,
                    "Pooling": "Max",
                    "Pool_area": "2",
                    "Pool_padding": "SAME",
                    "Pool_stride": "2"
                },
                "Code": None,
                "backward_connections": [
                    {
                        "src_id": "3.1",
                        "src_name": "conv1",
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
                ]
            },            
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": 123,
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Batch_norm": False,                    
                    "Keep_prob": "1"
                },
                "backward_connections": [
                    {
                        "src_id": "3.2",
                        "src_name": "conv2",
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
                "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False },
                "endPoints": [],                
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
                "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False },
                "endPoints": [],                                
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
                    "Batch_size": 10,                                        
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
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
                "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False },
                "endPoints": [],                                
            }
        }
    }
    
    graph_spec = GraphSpec.from_dict(json_network)    
    yield graph_spec

    
@pytest.fixture(scope='module')
def lw_core():
    yield LightweightCore()
    

@pytest.mark.pre_datawizard
def test_output_shape_from_labels(graph_spec, lw_core):
    rule = rules.DeepLearningFcOutputShapeFromLabels
    engine = SettingsEngine([rule], lw_core=lw_core)
    recommended_net = engine.run(graph_spec)

    assert graph_spec['4'].n_neurons != 10    
    assert recommended_net['4'].n_neurons == 10


    
    
