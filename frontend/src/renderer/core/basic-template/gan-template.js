const ganTemplate = {
  "project": {},
  "network": {
    "networkName": "GAN Template",
    "networkID": "1587407555677",
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
      "1587407567940": {
        "layerId": "1587407567940",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "GAN_1",
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
            "top": 250,
            "left": 780
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
        "componentName": "TrainGan",
        "connectionOut": [],
        "connectionIn": [
          "1587407689402"
        ],
        "connectionArrow": []
      },
      "1587407596237": {
        "layerId": "1587407596237",
        "copyId": null,
        "copyContainerElement": null,
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
            "top": 110,
            "left": 130
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
          "1587407603884"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1587407603884"
        ]
      },
      "1587407603884": {
        "layerId": "1587407603884",
        "copyId": null,
        "copyContainerElement": null,
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
            "top": 110,
            "left": 220
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
          "1587407608489"
        ],
        "connectionIn": [
          "1587407596237"
        ],
        "connectionArrow": [
          "1587407608489"
        ]
      },
      "1587407608489": {
        "layerId": "1587407608489",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_2",
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
            "top": 110,
            "left": 310
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
          "1587407616987"
        ],
        "connectionIn": [
          "1587407603884"
        ],
        "connectionArrow": [
          "1587407616987"
        ]
      },
      "1587407616987": {
        "layerId": "1587407616987",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_3",
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
            "top": 110,
            "left": 400
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
          "1587407636553"
        ],
        "connectionIn": [
          "1587407608489"
        ],
        "connectionArrow": [
          "1587407636553"
        ]
      },
      "1587407636553": {
        "layerId": "1587407636553",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Merge_1",
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
            "top": 110,
            "left": 500
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
        "componentName": "MathMerge",
        "connectionOut": [
          "1587407673505"
        ],
        "connectionIn": [
          "1587407616987",
          "1587407659152"
        ],
        "connectionArrow": [
          "1587407673505"
        ]
      },
      "1587407659152": {
        "layerId": "1587407659152",
        "copyId": null,
        "copyContainerElement": null,
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
            "top": 250,
            "left": 500
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
          "1587407636553"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1587407636553"
        ]
      },
      "1587407673505": {
        "layerId": "1587407673505",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_4",
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
            "top": 110,
            "left": 600
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
          "1587407677393"
        ],
        "connectionIn": [
          "1587407636553"
        ],
        "connectionArrow": [
          "1587407677393"
        ]
      },
      "1587407677393": {
        "layerId": "1587407677393",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_5",
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
            "top": 110,
            "left": 690
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
          "1587407689402"
        ],
        "connectionIn": [
          "1587407673505"
        ],
        "connectionArrow": [
          "1587407689402"
        ]
      },
      "1587407689402": {
        "layerId": "1587407689402",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_6",
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
            "top": 110,
            "left": 780
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
          "1587407567940"
        ],
        "connectionIn": [
          "1587407677393"
        ],
        "connectionArrow": [
          "1587407567940"
        ]
      }
    },
    "networkRootFolder": ""
  }
}
export default ganTemplate
