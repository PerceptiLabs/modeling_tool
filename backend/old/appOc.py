from coreCommunicator import coreCommunicator
import sys

core=coreCommunicator("OC")

print("Hello Everyone! :D")
print(sys.version_info)
action="StartTraining"

# while True:
    # action=input("Type Input: ")

if action=="StartTraining":
    value= {
        "Hyperparameters": {
        "Epochs": "1",
        "Batch_size": "32",
        "Data_partition": {
            "Training": "10",
            "Validation": "20",
            "Test": "10"
        },
        "Dropout_rate": "0.5",
        "Shuffle_data": True,
        "Save_model_every": "1"
        },
        "Layers": {
        "2": {
            "Name": "Data_1",
            "Type": "DataData",
            "Properties": {
            "Type": "Data",
            "accessProperties": {
                "Category": "Local",
                "Container": "quickstartblobs",
                "BlobName": "testblob",
                "Type": "Data",
                "Path": "./mnist"
            }
            },
            "backward_connections": [],
            "forward_connections": [
            "3"
            ]
        },
        "3": {
            "Name": "Reshape_1",
            "Type": "ProcessReshape",
            "Properties": {
            "Shape": [
                28,
                28,
                1
            ],
            "Permutation": [
                0,
                1,
                2
            ]
            },
            "backward_connections": [
            "2"
            ],
            "forward_connections": [
            "4"
            ]
        },
        "4": {
            "Name": "Convolution_1",
            "Type": "DeepLearningConv",
            "Properties": {
            "Conv_dim": "2D",
            "Patch_size": "3",
            "Stride": "2",
            "Padding": "'SAME'",
            "Feature_maps": "8",
            "Activation_function": "Sigmoid",
            "Dropout": False,
            "PoolBool": False,
            "Pooling": "Max",
            "Pool_area": "2",
            "Pool_padding": "SAME",
            "Pool_stride": "2"
            },
            "backward_connections": [
            "3"
            ],
            "forward_connections": [
            "5"
            ]
        },
        "5": {
            "Name": "FullyConnected_1",
            "Type": "DeepLearningFC",
            "Properties": {
            "Neurons": "10",
            "Activation_function": "Sigmoid",
            "Dropout": False
            },
            "backward_connections": [
            "4"
            ],
            "forward_connections": [
            "10"
            ]
        },
        "10": {
            "Name": "Normal_1",
            "Type": "TrainNormal",
            "Properties": {
            "N_class": "10",
            "Loss": "Cross_entropy",
            "Learning_rate": "0.01",
            "Optimizer": "SGD",
            "Training_iters": "20000"
            },
            "backward_connections": [
            "5",
            "11"
            ],
            "forward_connections": []
        },
        "11": {
            "Name": "OneHot_1",
            "Type": "ProcessOneHot",
            "Properties": {
            "N_class": "10"
            },
            "backward_connections": [
            "12"
            ],
            "forward_connections": [
            "10"
            ]
        },
        "12": {
            "Name": "Data_1",
            "Type": "DataData",
            "Properties": {
            "Type": "Data",
            "accessProperties": {
                "Category": "Local",
                "Container": "quickstartblobs",
                "BlobName": "testblob",
                "Type": "Labels",
                "Path": "./mnist"
            }
            },
            "backward_connections": [],
            "forward_connections": [
            "11"
            ]
        }
        }
    }
    core.startCore(value)
    print("Training Started")
if action=="GetStatus":
    response=core.getStatus()
    print(response)