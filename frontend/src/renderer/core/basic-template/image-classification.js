const imageClassification = {
  "project": {},
  "network": {
    "networkName": "Image Classification",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {},
    "networkRootFolder": '',
    "networkElementList": {
      "1564399775664": {
        "layerId": "1564399775664",
        "layerName": "Data_1",
        "layerType": "Data",
        "layerSettings": null,
        "layerCode": "",
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 160,
            "left": 200
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DataData",
        "connectionOut": [
          "1564399777283"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1564399777283"
        ]
      },
      "1564399777283": {
        "layerId": "1564399777283",
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
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 160,
            "left": 330
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "ProcessReshape",
        "connectionOut": [
          "1564399781738"
        ],
        "connectionIn": [
          "1564399775664"
        ],
        "connectionArrow": [
          "1564399781738"
        ],
        "layerSettingsTabName": "Settings"
      },
      "1564399781738": {
        "layerId": "1564399781738",
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
          "Batch_norm": false,
          "Keep_prob": "1",
          "PoolBool": false,
          "Pooling": "Max",
          "Pool_area": "2",
          "Pool_padding": "SAME",
          "Pool_stride": "2"
        },
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 160,
            "left": 470
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1564399782856"
        ],
        "connectionIn": [
          "1564399777283"
        ],
        "connectionArrow": [
          "1564399782856"
        ],
        "layerSettingsTabName": "Settings"
      },
      "1564399782856": {
        "layerId": "1564399782856",
        "layerName": "Fully Connected_1",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "10",
          "Activation_function": "Sigmoid",
          "Dropout": false,
          "Keep_prob": "1",
          "Batch_norm": false
        },
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 160,
            "left": 610
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DeepLearningFC",
        "connectionOut": [
          "1564399790363"
        ],
        "connectionIn": [
          "1564399781738"
        ],
        "connectionArrow": [
          "1564399790363"
        ],
        "layerSettingsTabName": "Settings"
      },
      "1564399786876": {
        "layerId": "1564399786876",
        "layerName": "Data_2",
        "layerType": "Data",
        "layerSettings": null,
        "layerCode": "",
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 340,
            "left": 200
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DataData",
        "connectionOut": [
          "1564399788744"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1564399788744"
        ]
      },
      "1564399788744": {
        "layerId": "1564399788744",
        "layerName": "OneHot_1",
        "layerType": "Other",
        "layerSettings": {
          "N_class": "10"
        },
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 340,
            "left": 390
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "ProcessOneHot",
        "connectionOut": [
          "1564399790363"
        ],
        "connectionIn": [
          "1564399786876"
        ],
        "connectionArrow": [
          "1564399790363"
        ],
        "layerSettingsTabName": "Settings"
      },
      "1564399790363": {
        "layerId": "1564399790363",
        "layerName": "Normal_1",
        "layerType": "Training",
        "layerSettings": {
          "Labels": "1564399788744",
          "Epochs": "10",
          "Batch_size": "10",
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
          "Training_iters": "20000",
          "Batch_size": '10'
        },
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 340,
            "left": 610
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "TrainNormal",
        "connectionOut": [],
        "connectionIn": [
          "1564399782856",
          "1564399788744"
        ],
        "connectionArrow": [],
        "layerSettingsTabName": "Settings"
      }
    }
  }
};

export default imageClassification;
