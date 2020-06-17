const objectDetection = {
  "project": {},
  "network": {
    "networkName": "Object Detection",
    "networkID": "",
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
      "1591014032299": {
        "layerId": "1591014032299",
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
                "path": "od_train_7.npy"
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
            "top": 90,
            "left": 70
          },
          "OutputDim": "224x224x3",
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
          "1591014039995"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1591014039995"
        ]
      },
      "1591014039995": {
        "layerId": "1591014039995",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "16",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
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
            "top": 90,
            "left": 190
          },
          "OutputDim": "224x224x16",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014131080"
        ],
        "connectionIn": [
          "1591014032299"
        ],
        "connectionArrow": [
          "1591014131080"
        ]
      },
      "1591014117301": {
        "layerId": "1591014117301",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_1",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "32",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
          "PoolBool": true,
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
            "top": 90,
            "left": 590
          },
          "OutputDim": "56x56x32",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014130303"
        ],
        "connectionIn": [
          "1591014130618"
        ],
        "connectionArrow": [
          "1591014130303"
        ]
      },
      "1591014125557": {
        "layerId": "1591014125557",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_7",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "256",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
          "PoolBool": true,
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
            "top": 90,
            "left": 1320
          },
          "OutputDim": "7x7x256",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591016602609"
        ],
        "connectionIn": [
          "1591014127280"
        ],
        "connectionArrow": [
          "1591016602609"
        ]
      },
      "1591014127280": {
        "layerId": "1591014127280",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_8",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "256",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
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
            "top": 90,
            "left": 1200
          },
          "OutputDim": "14x14x256",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014125557"
        ],
        "connectionIn": [
          "1591014129269"
        ],
        "connectionArrow": [
          "1591014125557"
        ]
      },
      "1591014129269": {
        "layerId": "1591014129269",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_9",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "128",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
          "PoolBool": true,
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
            "top": 90,
            "left": 1080
          },
          "OutputDim": "14x14x128",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014127280"
        ],
        "connectionIn": [
          "1591014129652"
        ],
        "connectionArrow": [
          "1591014127280"
        ]
      },
      "1591014129652": {
        "layerId": "1591014129652",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_10",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "128",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
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
            "top": 90,
            "left": 960
          },
          "OutputDim": "28x28x128",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014129269"
        ],
        "connectionIn": [
          "1591014129966"
        ],
        "connectionArrow": [
          "1591014129269"
        ]
      },
      "1591014129966": {
        "layerId": "1591014129966",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_11",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "64",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
          "PoolBool": true,
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
            "top": 90,
            "left": 840
          },
          "OutputDim": "28x28x64",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014129652"
        ],
        "connectionIn": [
          "1591014130303"
        ],
        "connectionArrow": [
          "1591014129652"
        ]
      },
      "1591014130303": {
        "layerId": "1591014130303",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_12",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "64",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
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
            "top": 90,
            "left": 710
          },
          "OutputDim": "56x56x64",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014129966"
        ],
        "connectionIn": [
          "1591014117301"
        ],
        "connectionArrow": [
          "1591014129966"
        ]
      },
      "1591014130618": {
        "layerId": "1591014130618",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_13",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "32",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
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
            "top": 90,
            "left": 470
          },
          "OutputDim": "112x112x32",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014117301"
        ],
        "connectionIn": [
          "1591014131080"
        ],
        "connectionArrow": [
          "1591014117301"
        ]
      },
      "1591014131080": {
        "layerId": "1591014131080",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_1_14",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "3",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "16",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
          "PoolBool": true,
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
            "top": 90,
            "left": 310
          },
          "OutputDim": "112x112x16",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591014130618"
        ],
        "connectionIn": [
          "1591014039995"
        ],
        "connectionArrow": [
          "1591014130618"
        ]
      },
      "1591015580394": {
        "layerId": "1591015580394",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Detector_1",
        "layerType": "Training",
        "layerSettings": {
          "Labels": "1591015695186",
          "Epochs": "30",
          "grid_size": "7",
          "batch_size": "3",
          "num_box": "2",
          "threshold": "0.8",
          "lambda_coord": "5",
          "lambda_no_obj": "0.7",
          "N_class": "1",
          "Loss": "Quadratic",
          "Class_weights": "1",
          "Learning_rate": "0.001",
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
          "isSelected": false,
          "position": {
            "top": 220,
            "left": 920
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
        "componentName": "TrainDetector",
        "connectionOut": [],
        "connectionIn": [
          "1591015695186",
          "1591016599574"
        ],
        "connectionArrow": []
      },
      "1591015695186": {
        "layerId": "1591015695186",
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
            "Sources": [
              {
                "type": "file",
                "path": "od_labels_7.npy"
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
            "top": 220,
            "left": 770
          },
          "OutputDim": "7x7x8",
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
          "1591015580394"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1591015580394"
        ]
      },
      "1591016599574": {
        "layerId": "1591016599574",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_2",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "1",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "13",
          "Activation_function": "None",
          "Dropout": false,
          "Keep_prob": "1",
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
            "top": 220,
            "left": 1040
          },
          "OutputDim": "7x7x13",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591015580394"
        ],
        "connectionIn": [
          "1591016602609"
        ],
        "connectionArrow": [
          "1591015580394"
        ]
      },
      "1591016602609": {
        "layerId": "1591016602609",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Convolution_3",
        "layerType": "Other",
        "layerSettings": {
          "Conv_dim": "2D",
          "Patch_size": "1",
          "Stride": "1",
          "Padding": "SAME",
          "Feature_maps": "512",
          "Activation_function": "ReLU",
          "Dropout": false,
          "Keep_prob": "1",
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
            "top": 220,
            "left": 1180
          },
          "OutputDim": "7x7x512",
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1591016599574"
        ],
        "connectionIn": [
          "1591014125557"
        ],
        "connectionArrow": [
          "1591016599574"
        ]
      }
    },
    "networkRootFolder": ""
  }
}

export default objectDetection;