const imageClassification = {
  "project": {},
  "network": {
    "networkName": "Image Classification",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {
      "openStatistics": null,
      "openTest": null,
      "zoom": 1,
      "netMode": "edit",
      "coreStatus": {
        "Status": "Waiting"
      },
      "chartsRequest": {
        "timerID": null,
        "waitGlobalEvent": false,
        "doRequest": 0,
        "showCharts": 0
      }
    },
    "networkRootFolder": "",
    "networkElementList": {
      "1598915799200": {
        "layerId": "1598915799200",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Data_1",
        "layerType": "Data",
        "layerSettings": {
          "Type": "Data",
          "testInfoIsInput": true,
          "accessProperties": {
            "Columns": [],
            "Dataset_size": "",
            "Category": "Local",
            "Type": "Data",
            "Sources": [],
            "PathFake": [],
            "Partition_list": [],
            "Shuffle_data": true,
            "Action_space": ""
          }
        },
        "layerSettingsTabName": "Computer",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 20,
            "left": 20
          },
          "OutputDim": "",
          "InputDim": "[]",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "chartData": {},
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DataData",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": true,
        "inputs": {},
        "outputs": {
          "15989157992000": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598915836465",
            "dst_var": "input"
          }
        ],
        "backward_connections": [],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598915800150": {
        "layerId": "1598915800150",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Data_2",
        "layerType": "Data",
        "layerSettings": {
          "Type": "Data",
          "testInfoIsInput": true,
          "accessProperties": {
            "Columns": [],
            "Dataset_size": "",
            "Category": "Local",
            "Type": "Data",
            "Sources": [],
            "PathFake": [],
            "Partition_list": [],
            "Shuffle_data": true,
            "Action_space": ""
          }
        },
        "layerSettingsTabName": "Computer",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 280,
            "left": 20
          },
          "OutputDim": "",
          "InputDim": "[]",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "chartData": {},
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DataData",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": true,
        "inputs": {},
        "outputs": {
          "15989158001500": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598915861658",
            "dst_var": "input"
          }
        ],
        "backward_connections": [],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598915836465": {
        "layerId": "1598915836465",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Reshape_1",
        "layerType": "Other",
        "layerSettings": {
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
        "layerSettingsTabName": "Settings",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 20,
            "left": 220
          },
          "OutputDim": "",
          "InputDim": "[784]",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "chartData": {},
        "checkpoint": [],
        "endPoints": [],
        "componentName": "ProcessReshape",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": false,
        "inputs": {
          "15989158364650": {
            "name": "input",
            "reference_var_id": "15989157992000",
            "reference_layer_id": "1598915799200",
            "isDefault": true
          }
        },
        "outputs": {
          "15989158364650": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598915844680",
            "dst_var": "input"
          }
        ],
        "backward_connections": [
          {
            "src_id": "1598915799200",
            "src_var": "output",
            "dst_var": "input"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598915844680": {
        "layerId": "1598915844680",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "2",
          "Padding": "SAME",
          "Feature_maps": "8",
          "Activation_function": "Sigmoid",
          "Dropout": false,
          "Keep_prob": "1",
          "Batch_norm": false,
          "PoolBool": false,
          "Pooling": "Max",
          "Pool_area": "2",
          "Pool_padding": "SAME",
          "Pool_stride": "2"
        },
        "layerSettingsTabName": "Settings",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 20,
            "left": 420
          },
          "OutputDim": "",
          "InputDim": "[28, 28, 1]",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "chartData": {},
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DeepLearningConv",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": false,
        "inputs": {
          "15989158446800": {
            "name": "input",
            "reference_var_id": "15989158364650",
            "reference_layer_id": "1598915836465",
            "isDefault": true
          }
        },
        "outputs": {
          "15989158446800": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598970577549",
            "dst_var": "input"
          }
        ],
        "backward_connections": [
          {
            "src_id": "1598915836465",
            "src_var": "output",
            "dst_var": "input"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598915861658": {
        "layerId": "1598915861658",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "OneHot_1",
        "layerType": "Other",
        "layerSettings": {
          "N_class": "10"
        },
        "layerSettingsTabName": "Settings",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 280,
            "left": 280
          },
          "OutputDim": "",
          "InputDim": "",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "chartData": {},
        "checkpoint": [],
        "endPoints": [],
        "componentName": "ProcessOneHot",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": false,
        "inputs": {
          "15989158616580": {
            "name": "input",
            "reference_var_id": "15989158001500",
            "reference_layer_id": "1598915800150",
            "isDefault": true
          }
        },
        "outputs": {
          "15989158616580": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598982397425",
            "dst_var": "labels"
          }
        ],
        "backward_connections": [
          {
            "src_id": "1598915800150",
            "src_var": "output",
            "dst_var": "input"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598970577549": {
        "layerId": "1598970577549",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_1",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "10",
          "Activation_function": "Sigmoid",
          "Dropout": false,
          "Keep_prob": "1",
          "Batch_norm": false
        },
        "layerSettingsTabName": "Settings",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 20,
            "left": 640
          },
          "OutputDim": "",
          "InputDim": "",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "chartData": {},
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DeepLearningFC",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": true,
        "inputs": {
          "15989705775490": {
            "name": "input",
            "reference_var_id": "15989158446800",
            "reference_layer_id": "1598915844680",
            "isDefault": true
          }
        },
        "outputs": {
          "15989705775490": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598982397425",
            "dst_var": "predictions"
          }
        ],
        "backward_connections": [
          {
            "src_id": "1598915844680",
            "src_var": "output",
            "dst_var": "input"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598982397425": {
        "layerId": "1598982397425",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Normal_1",
        "layerType": "Training",
        "layerSettings": {
          "Labels": "",
          "Epochs": "10",
          "N_class": "1",
          "Loss": "Quadratic",
          "Stop_condition": "Epochs",
          "Stop_Target_Accuracy": "0",
          "Class_weights": "1",
          "Learning_rate": "0.001",
          "Optimizer": "ADAM",
          "Beta_1": "0.9",
          "Beta_2": "0.999",
          "Momentum": "0.9",
          "Decay_steps": "100000",
          "Decay_rate": "0.96",
          "Training_iters": "20000",
          "Batch_size": "10"
        },
        "layerSettingsTabName": "Settings",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 259,
            "left": 954
          },
          "OutputDim": "",
          "InputDim": "",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "chartData": {},
        "checkpoint": [],
        "endPoints": [],
        "componentName": "TrainNormal",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": false,
        "inputs": {
          "15989823974250": {
            "name": "predictions",
            "reference_var_id": "15989705775490",
            "reference_layer_id": "1598970577549",
            "isDefault": true
          },
          "15989823974251": {
            "name": "labels",
            "reference_var_id": "15989158616580",
            "reference_layer_id": "1598915861658",
            "isDefault": true
          }
        },
        "outputs": {},
        "forward_connections": [],
        "backward_connections": [
          {
            "src_id": "1598970577549",
            "src_var": "output",
            "dst_var": "predictions"
          },
          {
            "src_id": "1598915861658",
            "src_var": "output",
            "dst_var": "labels"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      }
    },
    
  }
};

export default imageClassification;
