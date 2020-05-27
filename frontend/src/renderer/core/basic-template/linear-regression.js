const linearRegression = {
    "project": {},
    "network": {
      "networkName": "linearRegression",
      "networkID": "",
      "networkMeta": {},
      "networkElementList": {
        "1590611896154": {
          "layerId": "1590611896154",
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
              "Partition_list": [
                [
                  70,
                  20,
                  10
                ]
              ],
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
              "top": 90,
              "left": 400
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
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DataData",
          "connectionOut": [
            "1590611906903"
          ],
          "connectionIn": [],
          "connectionArrow": [
            "1590611906903"
          ]
        },
        "1590611901110": {
          "layerId": "1590611901110",
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
              "Partition_list": [
                [
                  70,
                  20,
                  10
                ]
              ],
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
              "top": 330,
              "left": 400
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
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DataData",
          "connectionOut": [
            "1590611916019"
          ],
          "connectionIn": [],
          "connectionArrow": [
            "1590611916019"
          ]
        },
        "1590611906903": {
          "layerId": "1590611906903",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Fully Connected_1",
          "layerType": "Other",
          "layerSettings": {
            "Neurons": "1",
            "Activation_function": "None",
            "Dropout": false,
            "Keep_prob": "1"
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
              "top": 90,
              "left": 680
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
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningFC",
          "connectionOut": [
            "1590611916019"
          ],
          "connectionIn": [
            "1590611896154"
          ],
          "connectionArrow": [
            "1590611916019"
          ]
        },
        "1590611916019": {
          "layerId": "1590611916019",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Regression_1",
          "layerType": "Training",
          "layerSettings": {
            "Labels": "1590611901110",
            "Epochs": "200",
            "N_class": "1",
            "Loss": "Regression",
            "Class_weights": "1",
            "Learning_rate": "0.00001",
            "Optimizer": "SGD",
            "Beta_1": "0.9",
            "Beta_2": "0.999",
            "Momentum": "0.9",
            "Decay_steps": "100000",
            "Decay_rate": "0.96",
            "batch_size": "10",
            "Training_iters": "20000"
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
              "top": 330,
              "left": 680
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
          "checkpoint": [],
          "endPoints": [],
          "componentName": "TrainRegression",
          "connectionOut": [],
          "connectionIn": [
            "1590611901110",
            "1590611906903"
          ],
          "connectionArrow": []
        }
      },
      "networkRootFolder": "",
    }

  };
  
  export default linearRegression
  