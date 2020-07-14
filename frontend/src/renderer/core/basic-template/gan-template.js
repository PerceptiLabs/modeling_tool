const ganTemplate = {
  "project": {},
  "network": {
    "networkName": "GAN Template",
    "networkID": "",
    "networkRootFolder": "",
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
    "networkElementList": {
      "1590427362547": {
        "layerId": "1590427362547",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Random_1",
        "layerType": "Data",
        "layerSettings": {
          "mean": "0.1",
          "stddev": "0.5",
          "min": "0.1",
          "max": "3.4",
          "distribution": "Normal",
          "shape": "(100)",
          "accessProperties": {
            "Action_space": "",
            "Dataset_size": "",
            "Columns": []
          }
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
            "top": 190,
            "left": 110
          },
          "OutputDim": "100",
          "InputDim": "[]",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DataRandom",
        "connectionOut": [
          "1590427376455"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1590427376455"
        ]
      },
      "1590427376455": {
        "layerId": "1590427376455",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_1",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "128",
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
            "top": 190,
            "left": 220
          },
          "OutputDim": "128",
          "InputDim": "[128]",
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
          "1590427378853"
        ],
        "connectionIn": [
          "1590427362547"
        ],
        "connectionArrow": [
          "1590427378853"
        ]
      },
      "1590427378853": {
        "layerId": "1590427378853",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_2",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "784",
          "Activation_function": "Sigmoid",
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
            "top": 190,
            "left": 340
          },
          "OutputDim": "784",
          "InputDim": "[256]",
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
          "1590427416106"
        ],
        "connectionIn": [
          "1590427376455"
        ],
        "connectionArrow": [
          "1590427416106"
        ]
      },
      "1590427381875": {
        "layerId": "1590427381875",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_3",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "128",
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
            "top": 190,
            "left": 710
          },
          "OutputDim": "128",
          "InputDim": "[28, 28, 1]",
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
          "1590427385141"
        ],
        "connectionIn": [
          "1590427392420"
        ],
        "connectionArrow": [
          "1590427385141"
        ]
      },
      "1590427385141": {
        "layerId": "1590427385141",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_4",
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
            "top": 190,
            "left": 850
          },
          "OutputDim": "1",
          "InputDim": "[256]",
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
          "1590428875155"
        ],
        "connectionIn": [
          "1590427381875"
        ],
        "connectionArrow": [
          "1590428875155"
        ]
      },
      "1590427392420": {
        "layerId": "1590427392420",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Switch_1",
        "layerType": "Other",
        "layerSettings": {
          "selected_layer": "Reshape_1"
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
            "top": 190,
            "left": 590
          },
          "OutputDim": "28x28x1",
          "InputDim": "[[28, 28, 1], [28, 28, 1]]",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "checkpoint": [],
        "endPoints": [],
        "componentName": "MathSwitch",
        "connectionOut": [
          "1590427381875"
        ],
        "connectionIn": [
          "1590427520850",
          "1590427416106"
        ],
        "connectionArrow": [
          "1590427381875"
        ]
      },
      "1590427416106": {
        "layerId": "1590427416106",
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
            "top": 190,
            "left": 460
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "ProcessReshape",
        "connectionOut": [
          "1590427392420"
        ],
        "connectionIn": [
          "1590427378853"
        ],
        "connectionArrow": [
          "1590427392420"
        ]
      },
      "1590427520850": {
        "layerId": "1590427520850",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Reshape_2",
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
            "top": 310,
            "left": 590
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "ProcessReshape",
        "connectionOut": [
          "1590427392420"
        ],
        "connectionIn": [
          "1590428953412"
        ],
        "connectionArrow": [
          "1590427392420"
        ]
      },
      "1590428875155": {
        "layerId": "1590428875155",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "GAN_1",
        "layerType": "Training",
        "layerSettings": {
          "switch_layer": "Switch_1",
          "real_data_layer": "Data_1",
          "Epochs": "100",
          "N_class": "1",
          "Loss": "Quadratic",
          "Class_weights": "1",
          "Learning_rate": "0.001",
          "batch_size": "100",
          "Optimizer": "ADAM",
          "Beta_1": "0.9",
          "Beta_2": "0.999",
          "Momentum": "0.9",
          "Decay_steps": "100000",
          "Decay_rate": "0.96",
          "Training_iters": "20000"
        },
        "layerSettingsTabName": "Settings",
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": true,
          "position": {
            "top": 190,
            "left": 990
          },
          "OutputDim": "",
          "InputDim": "[1]",
          "layerContainerName": "",
          "layerBgColor": "",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "checkpoint": [],
        "endPoints": [],
        "componentName": "TrainGan",
        "connectionOut": [],
        "connectionIn": [
          "1590427385141"
        ],
        "connectionArrow": []
      },
      "1590428953412": {
        "layerId": "1590428953412",
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
            "Sources": [
              {
                "type": "file",
                "path": "mnist_gan.npy"
              }
            ],
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
            "top": 460,
            "left": 590
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DataData",
        "connectionOut": [
          "1590427520850"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1590427520850"
        ]
      }
    }    
  }
}
export default ganTemplate
