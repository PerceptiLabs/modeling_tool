const basicTemplate1 = {
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
            "left": 330
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
        "componentName": "ProcessReshape",
        "connectionOut": [
          "1564399781738"
        ],
        "connectionIn": [
          "1564399775664"
        ],
        "connectionArrow": [
          "1564399781738"
        ]
      },
      "1564399781738": {
        "layerId": "1564399781738",
        "layerName": "Convolution_1",
        "layerType": "Other",
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
            "left": 470
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
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1564399782856"
        ],
        "connectionIn": [
          "1564399777283"
        ],
        "connectionArrow": [
          "1564399782856"
        ]
      },
      "1564399782856": {
        "layerId": "1564399782856",
        "layerName": "Fully Connected_1",
        "layerType": "Other",
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
            "left": 610
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
        "componentName": "DeepLearningFC",
        "connectionOut": [
          "1564399790363"
        ],
        "connectionIn": [
          "1564399781738"
        ],
        "connectionArrow": [
          "1564399790363"
        ]
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
            "left": 390
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
        "componentName": "ProcessOneHot",
        "connectionOut": [
          "1564399790363"
        ],
        "connectionIn": [
          "1564399786876"
        ],
        "connectionArrow": [
          "1564399790363"
        ]
      },
      "1564399790363": {
        "layerId": "1564399790363",
        "layerName": "Normal_1",
        "layerType": "Training",
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
            "left": 610
          },
          "OutputDim": "",
          "InputDim": "[, ]",
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
        "connectionArrow": []
      }
    }
  }
};

export default basicTemplate1
