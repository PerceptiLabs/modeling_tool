import pytest
import tempfile
import numpy as np

from perceptilabs.mainInterface import Interface
import perceptilabs.utils as utils
from perceptilabs.issues import IssueHandler

def create_json_network(temp_path_checkpoints):
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
            "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False }
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
            "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False }
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
            "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False }
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
            "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False }
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
            "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False }
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
            "checkpoint": {'path':checkpoint_path, 'load_checkpoint':False }
        }
    }

    return utils.patch_net_connections(json_network)

def create_request(receiver, action, value):
    return {"receiver": receiver, "action":action, "value":value}

def send_request(request):
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwDict=dict()
    issue_handler = IssueHandler()
    main_interface = Interface(cores, dataDict, checkpointDict, lwDict, issue_handler)

    return main_interface.create_response(request)

def test_getGraphOrder(temp_path_checkpoints):
    receiver = 0000
    action = "getGraphOrder"
    value = create_json_network(temp_path_checkpoints)

    request = create_request(receiver, action, value)
    
    response, issue_handler = send_request(request)
    assert len(issue_handler.pop_warnings()) == 0
    assert len(issue_handler.pop_errors()) == 0
    assert (
        response == ['1','3','4','2','5','6'] or
        response == ['2', '5', '1', '3', '4', '6']
    )


@pytest.mark.skip    
def test_start(temp_path_checkpoints):
    receiver = 0000
    action = "Start"
    value = create_json_network(temp_path_checkpoints)


    request = create_request(receiver, action, value)
    
    response, issue_handler = send_request(request)
    
    import pdb; pdb.set_trace()
