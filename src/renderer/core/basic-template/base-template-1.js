const basicTemplate1 = {
  "project": {},
  "network": {
    "networkName": "Image Classification",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {},
    "networkElementList": {
      "1558084944100": {
        "layerId": "1558084944100",
        "layerName": "Data_1",
        "layerType": "Data",
        "layerSettings": "",
        "layerCode": "",
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 130,
            "left": 290
          },
          "OutputDim": "",
          "InputDim": "",
          "layerBgColor": '',
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "DataData",
        "connectionOut": [
          "1558084947036"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1558084947036"
        ]
      },
      "1558084944754": {
        "layerId": "1558084944754",
        "layerName": "Data_1",
        "layerType": "Data",
        "layerSettings": "",
        "layerCode": "",
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 350,
            "left": 290
          },
          "OutputDim": "",
          "InputDim": "",
          "layerBgColor": '',
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "DataData",
        "connectionOut": [
          "1558084948353"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1558084948353"
        ]
      },
      "1558084947036": {
        "layerId": "1558084947036",
        "layerName": "Reshape",
        "layerType": "Other",
        "layerSettings": "",
        "layerCode": "",
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 130,
            "left": 490
          },
          "OutputDim": "",
          "InputDim": "",
          "layerBgColor": '',
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "ProcessReshape",
        "connectionOut": [
          "1558084952391"
        ],
        "connectionIn": [
          "1558084944100"
        ],
        "connectionArrow": [
          "1558084952391"
        ]
      },
      "1558084948353": {
        "layerId": "1558084948353",
        "layerName": "OneHot_1",
        "layerType": "Other",
        "layerSettings": "",
        "layerCode": "",
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 350,
            "left": 580
          },
          "OutputDim": "",
          "InputDim": "",
          "layerBgColor": '',
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "ProcessOneHot",
        "connectionOut": [
          "1558084956146"
        ],
        "connectionIn": [
          "1558084944754"
        ],
        "connectionArrow": [
          "1558084956146"
        ]
      },
      "1558084952391": {
        "layerId": "1558084952391",
        "layerName": "Convolution_1",
        "layerType": "Other",
        "layerSettings": "",
        "layerCode": "",
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 130,
            "left": 680
          },
          "OutputDim": "",
          "InputDim": "",
          "layerBgColor": '',
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1558084953513"
        ],
        "connectionIn": [
          "1558084947036"
        ],
        "connectionArrow": [
          "1558084953513"
        ]
      },
      "1558084953513": {
        "layerId": "1558084953513",
        "layerName": "FullyConnected_1",
        "layerType": "Other",
        "layerSettings": "",
        "layerCode": "",
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 130,
            "left": 870
          },
          "OutputDim": "",
          "InputDim": "",
          "layerBgColor": '',
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "DeepLearningFC",
        "connectionOut": [
          "1558084956146"
        ],
        "connectionIn": [
          "1558084952391"
        ],
        "connectionArrow": [
          "1558084956146"
        ]
      },
      "1558084956146": {
        "layerId": "1558084956146",
        "layerName": "Normal",
        "layerType": "Training",
        "layerSettings": "",
        "layerCode": "",
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 350,
            "left": 870
          },
          "OutputDim": "",
          "InputDim": "",
          "layerBgColor": '',
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "TrainNormal",
        "connectionOut": [],
        "connectionIn": [
          "1558084953513",
          "1558084948353"
        ],
        "connectionArrow": []
      }
    }
  }
};

export default basicTemplate1