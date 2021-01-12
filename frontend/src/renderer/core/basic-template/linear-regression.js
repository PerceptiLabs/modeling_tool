const linearRegression = {
  "project": {},
  "network": {
    "networkName": "Linear Regression",
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
      "1598990332625": {
        "layerId": "1598990332625",
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
                "path": "linreg_input.npy"
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
            "left": 90
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
        "componentName": "DataData",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": true,
        "inputs": {},
        "outputs": {
          "15989903326260": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1598990349372",
            "dst_var": "input"
          }
        ],
        "backward_connections": [],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598990333926": {
        "layerId": "1598990333926",
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
                "path": "linreg_labels.npy"
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
            "top": 480,
            "left": 90
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
        "componentName": "DataData",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": true,
        "inputs": {},
        "outputs": {
          "15989903339270": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1599778043214",
            "dst_var": "labels"
          }
        ],
        "backward_connections": [],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1598990349372": {
        "layerId": "1598990349372",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Dense_1",
        "layerType": "Other",
        "layerSettings": {
          "Dropout": false,
          "Keep_prob": 1,
          "Neurons": 1,
          "Activation_function": "None",
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
            "left": 390
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
        "componentName": "DeepLearningFC",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": true,
        "inputs": {
          "15989903493720": {
            "name": "input",
            "reference_var_id": "15989903326260",
            "reference_layer_id": "1598990332625",
            "isDefault": true
          }
        },
        "outputs": {
          "15989903493730": {
            "name": "output",
            "reference_var": "output"
          }
        },
        "forward_connections": [
          {
            "src_var": "output",
            "dst_id": "1599778043214",
            "dst_var": "predictions"
          }
        ],
        "backward_connections": [
          {
            "src_id": "1598990332625",
            "src_var": "output",
            "dst_var": "input"
          }
        ],
        "previewVariable": "output",
        "previewVariableList": []
      },
      "1599778043214": {
        "layerId": "1599778043214",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Regression_1",
        "layerType": "Training",
        "layerSettings": {
          "Learning_rate": 0.00001,
          "Decay_rate": 0.96,
          "Decay_steps": 100000,
          "Momentum": 0.9,
          "Batch_size": 8,
          "Beta_2": 0.999,
          "Beta_1": 0.9,
          "Optimizer": "SGD",
          "Epochs": 400,
          "Batch_size": 8,
          "Labels": "1598990333926",
          "Class_weights": 1,
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
            "top": 300,
            "left": 750
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
        "componentName": "TrainRegression",
        "connectionOut": [],
        "connectionIn": [],
        "connectionArrow": [],
        "visited": true,
        "inputs": {
          "15997780432140": {
            "name": "predictions",
            "reference_var_id": "15989903493730",
            "reference_layer_id": "1598990349372",
            "isDefault": true
          },
          "15997780432141": {
            "name": "labels",
            "reference_var_id": "15989903339270",
            "reference_layer_id": "1598990333926",
            "isDefault": true
          }
        },
        "outputs": {},
        "forward_connections": [],
        "backward_connections": [
          {
            "src_id": "1598990349372",
            "src_var": "output",
            "dst_var": "predictions"
          },
          {
            "src_id": "1598990333926",
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

export default linearRegression
