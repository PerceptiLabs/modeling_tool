import tempfile
import numpy as np

from perceptilabs.mainInterface import Interface

def create_json_network():
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
    json_network = {
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
            "forward_connections": [["5", "one_hot"]],
            "Code": ""
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
            "backward_connections": [["3", "reshape"]],
            "forward_connections": [["6", "training"]],
            "Code": ""
        },
        "5": {
            "Name": "one_hot",
            "Type": "ProcessOneHot",
            "Properties": {
                "N_class": n_classes
            },
            "backward_connections": [["2", "data_labels"]],
            "forward_connections": [["6", "training"]],
            "Code": ""
        },
        "6": {
            "Name": "training",
            "Type": "TrainNormal",
            "Properties": {
                "Labels": "5",
                "Loss": "Quadratic",
                "Epochs": 100,
                "Class_weights": "1",  # TODO: what's this?
                "Optimizer": "SGD",
                "Beta_1": "0.9",
                "Beta_2": "0.999",
                "Momentum": "0.9",
                "Decay_steps": "100000",
                "Decay_rate": "0.96",
                "Learning_rate": "0.5",
                "Distributed": False
            },
            "backward_connections": [["4", "fc"], ["5", "one_hot"]],
            "forward_connections": [],
            "Code": ""
        }

    }

    return json_network

def create_request(reciever, action, value):
    return {"reciever": reciever, "action":action, "value":value}

def send_request(request):
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwDict=dict()

    core_interface = Interface(cores, dataDict, checkpointDict, lwDict, core_mode='v1')

    return core_interface.create_response(request)

def test_getGraphOrder():
    reciever = 0000
    action = "getGraphOrder"
    value = create_json_network()

    request = create_request(reciever, action, value)
    
    response, warnings, errors = send_request(request)
    
    assert warnings.empty()
    assert errors.empty()
    assert response == ['1','2','3','5','4','6']
