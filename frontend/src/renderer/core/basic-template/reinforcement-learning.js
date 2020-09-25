const reinforcementLearning = {
  "project": {},
  "network": {
    "networkName": "Reinforcement Learning",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {
      "openStatistics": false,
      "openTest": null,
      "zoom": 1,
      "netMode": "edit",
      "coreStatus": {
        "Status": "Stop",
        "Iterations": 60,
        "Epoch": 0,
        "Progress": 0.0000030000001500000076,
        "CPU": 7.8,
        "GPU": 0,
        "Memory": 78.6
      },
      "chartsRequest": {
        "timerID": 205,
        "waitGlobalEvent": false,
        "doRequest": 347,
        "showCharts": 347
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
          "Type": "Environment",
          "accessProperties": {
            "EnvType": "Gym",
            "Sources": [],
            "Atari": "Breakout",
            "Category": "Local",
            "Type": "Data"
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
        "layerSettings": {},
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
            "dst_id": "1598979686278",
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
          "Neurons": "4",
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
            "top": 120,
            "left": 520
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
            "reference_var_id": "15989796765100",
            "reference_layer_id": "1598979676510",
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
            "src_id": "1598979676510",
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
          "Update_freq": "4",
          "Gamma": "0.95",
          "Loss": "Quadratic",
          "Eps": "1",
          "Eps_min": "0.1",
          "Eps_decay": "0.2",
          "Learning_rate": "0.01",
          "Optimizer": "SGD",
          "Max_steps": "1000",
          "Episodes": "20000",
          "History_length": "10",
          "Batch_size": "32"
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
            "left": 760
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
      }
    }
  }
};

export default reinforcementLearning
