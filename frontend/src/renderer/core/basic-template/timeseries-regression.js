const timeseriesRegression = {
  "project": {},
  "network": {
    "networkName": "Timeseries Regression",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {},
    "networkRootFolder": '',
    "networkElementList": {
      "1572267778904": {
        "layerId": "1572267778904",
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
            "top": 150,
            "left": 200
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
        "componentName": "DataData",
        "connectionOut": [
          "1572267783219"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1572267783219"
        ]
      },
      "1572267783219": {
        "layerId": "1572267783219",
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
            "top": 150,
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
        "componentName": "DeepLearningFC",
        "connectionOut": [
          "1572267793607"
        ],
        "connectionIn": [
          "1572267778904"
        ],
        "connectionArrow": [
          "1572267793607"
        ]
      },
      "1572267788395": {
        "layerId": "1572267788395",
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
            "top": 320,
            "left": 200
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
        "componentName": "DataData",
        "connectionOut": [
          "1572267793607"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1572267793607"
        ]
      },
      "1572267793607": {
        "layerId": "1572267793607",
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
            "top": 320,
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
        "componentName": "TrainNormal",
        "connectionOut": [],
        "connectionIn": [
          "1572267783219",
          "1572267788395"
        ],
        "connectionArrow": []
      }
    }
  }
};

export default timeseriesRegression
