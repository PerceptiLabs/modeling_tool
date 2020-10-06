const reinforcementLearning = {
  "project": {},
  "network": {
    "networkName": "Reinforcement Learning",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {
      "openStatistics": null,
      "openTest": null,
      "zoom": 1,
      "netMode": "edit",
      "coreStatus": {
        "Status": "Waiting",
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
      "1598979671427": {
        "layerId": "1598979671427",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Environment_1",
        "layerType": "Data",
        "layerSettings": {
          "accessProperties": {
            "Atari": "Breakout"
          }
        },
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 119.25,
            "left": 142.5
          },
          "OutputDim": "210x160x3",
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
        "componentName": "DataEnvironment",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": true,
        "inputs": {},
        "outputs": {
          "15989796714270": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598979676510",
            "dst_var": "input"
          }
        ],
        "backward_connections": [],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598979676510": {
        "layerId": "1598979676510",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Grayscale_1",
        "layerType": "Other",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 120,
            "left": 330
          },
          "OutputDim": "210x160x1",
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
        "componentName": "ProcessGrayscale",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": false,
        "inputs": {
          "15989796765100": {
            "name": "input",
            "reference_var_id": "15989796714270",
            "reference_layer_id": "1598979671427",
            "isDefault": true
          }
        },
        "outputs": {
          "15989796765100": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1601035580243",
            "dst_var": "input"
          }
        ],
        "backward_connections": [
          {
            "src_id": "1598979671427",
            "src_var": "output",
            "dst_var": "input"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598979686278": {
        "layerId": "1598979686278",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Dense_1",
        "layerType": "Other",
        "layerSettings": {
          "Dropout": false,
          "Keep_prob": 1,
          "Neurons": 4,
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
            "top": 120,
            "left": 720
          },
          "OutputDim": "4",
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
          "15989796862780": {
            "name": "input",
            "reference_var_id": "16010355802430",
            "reference_layer_id": "1601035580243",
            "isDefault": true
          }
        },
        "outputs": {
          "15989796862780": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598982215514",
            "dst_var": "action"
          }
        ],
        "backward_connections": [
          {
            "src_id": "1601035580243",
            "src_var": "output",
            "dst_var": "input"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598982215514": {
        "layerId": "1598982215514",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Reinforcement Learning_1",
        "layerType": "Training",
        "layerSettings": {
          "ReinforceType": "Q_learning",
          "Learning_rate": 0.01,
          "Distributed": false,
          "Optimizer": "SGD",
          "Episodes": 20000,
          "Batch_size": 32,
          "Max_steps": 1000,
          "History_length": 10,
          "Use_CPU": true
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
            "top": 120,
            "left": 940
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
        "componentName": "TrainReinforce",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": false,
        "inputs": {
          "15989822155140": {
            "name": "action",
            "reference_var_id": "15989796862780",
            "reference_layer_id": "1598979686278",
            "isDefault": true
          }
        },
        "outputs": {},
        "forward_connections": [],
        "backward_connections": [
          {
            "src_id": "1598979686278",
            "src_var": "output",
            "dst_var": "action"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1601035580243": {
        "layerId": "1601035580243",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1",
        "layerType": "Other",
        "layerSettings": {
          "Dropout": false,
          "Keep_prob": 0,
          "Batch_norm": false,
          "Conv_dim": "2D",
          "Patch_size": 3,
          "Feature_maps": 8,
          "Stride": 2,
          "Padding": "SAME",
          "Activation_function": "Sigmoid",
          "PoolBool": false,
          "Pooling": null,
          "Pool_area": null,
          "Pool_padding": "None",
          "Pool_stride": null
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
            "top": 120,
            "left": 520
          },
          "tutorialId": "",
          "OutputDim": "105x80x8",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": false,
        "inputs": {
          "16010355802430": {
            "name": "input",
            "reference_var_id": "15989796765100",
            "reference_layer_id": "1598979676510",
            "isDefault": true
          }
        },
        "outputs": {
          "16010355802430": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598979686278",
            "dst_var": "input"
          }
        ],
        "backward_connections": [
          {
            "src_id": "1598979676510",
            "src_var": "output",
            "dst_var": "input"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      }
    }    
  }
};

export default reinforcementLearning
