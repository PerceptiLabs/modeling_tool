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
        "layerName": "Local_1",
        "layerType": "Data",
        "layerSettings": {
          "accessProperties": {
            "Columns": [],
            "Sources": [
              {
                "type": "file",
                "path": "classification_mnist_input.npy"
              }
            ],
            "Partition_list": [
              [
                70,
                20,
                10
              ]
            ],
            "Shuffle_data": true
          },
          "lazy": false
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
            "top": 30,
            "left": 30
          },
          "OutputDim": "784",
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
        "layerName": "Local_2",
        "layerType": "Data",
        "layerSettings": {
          "accessProperties": {
            "Columns": [],
            "Sources": [
              {
                "type": "file",
                "path": "classification_mnist_labels.npy"
              }
            ],
            "Partition_list": [
              [
                70,
                20,
                10
              ]
            ],
            "Shuffle_data": true
          },
          "lazy": false
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
            "top": 270,
            "left": 30
          },
          "OutputDim": "1",
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
            "top": 30,
            "left": 210
          },
          "OutputDim": "28x28x1",
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
          "Dropout": false,
          "Keep_prob": 1,
          "Batch_norm": false,
          "Conv_type": "Conv",
          "Conv_dim": "2D",
          "Patch_size": 3,
          "Feature_maps": 8,
          "Stride": 2,
          "Padding": "SAME",
          "Activation_function": "Sigmoid",
          "PoolBool": false,
          "Pooling": "Max",
          "Pool_area": 2,
          "Pool_padding": "SAME",
          "Pool_stride": 2
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
            "top": 30,
            "left": 420
          },
          "OutputDim": "14x14x8",
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
          "N_class": 10
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
            "top": 270,
            "left": 300
          },
          "OutputDim": "10",
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
        "layerName": "Dense_1",
        "layerType": "Other",
        "layerSettings": {
          "Dropout": false,
          "Keep_prob": 1,
          "Neurons": 10,
          "Activation_function": "Sigmoid",
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
            "top": 30,
            "left": 630
          },
          "OutputDim": "10",
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
        "visited": false,
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
        "layerName": "Classification_1",
        "layerType": "Training",
        "layerSettings": {
          "Learning_rate": 0.001,
          "Decay_rate": 0.96,
          "Decay_steps": 100000,
          "Momentum": 0.9,
          "Beta_2": 0.999,
          "Beta_1": 0.9,
          "Optimizer": "ADAM",
          "Epochs": 10,
          "Batch_size": 10,
          "Loss": "Quadratic",
          "Labels": "1598915861658",
          "Class_weights": 1,
          "Use_CPU": true,
          "Stop_Target_Accuracy": 0,
          "Stop_condition": "Epochs"
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
            "top": 270,
            "left": 960
          },
          "OutputDim": "1",
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
    }    
  }
};

export default imageClassification;
