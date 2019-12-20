const reinforcementLearning = {
  "project": {},
  "network": {
    "networkName": "Reinforcement Learning",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {},
    "networkRootFolder": '',
    "networkElementList": {
      "1572267706211": {
        "layerId": "1572267706211",
        "layerName": "Environment_1",
        "layerType": "Data",
        "layerSettings": {
          "Type": "Environment",
          "accessProperties": {
            "EnvType": "Gym",
            "Sources": [],
            "Atari": "Breakout",
            "Category": "Local",
            "Type": "Data",
            "History_length": 10
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
            "top": 130,
            "left": 120
          },
          "OutputDim": "10x210x160x3",
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
        "componentName": "DataEnvironment",
        "connectionOut": [
          "1572267710316"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1572267710316"
        ],
        "layerSettingsTabName": "Gym"
      },
      "1572267710316": {
        "layerId": "1572267710316",
        "layerName": "Grayscale_1",
        "layerType": "Other",
        "layerSettings": {},
        "layerCode": {
          "Output": "if X['Y'].get_shape().as_list()[-1] == 3:\n    Y = tf.image.rgb_to_grayscale(X['Y'])\nelse:\n    Y = X['Y']\n"
        },
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 130,
            "left": 270
          },
          "OutputDim": "10x210x160x1",
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
        "componentName": "ProcessGrayscale",
        "connectionOut": [
          "1572267716818"
        ],
        "connectionIn": [
          "1572267706211"
        ],
        "connectionArrow": [
          "1572267716818"
        ],
        "layerSettingsTabName": "Code"
      },
      "1572267716818": {
        "layerId": "1572267716818",
        "layerName": "Fully Connected_1",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "4",
          "Activation_function": "Sigmoid",
          "Dropout": false,
          "Keep_prob": "1"
        },
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 130,
            "left": 420
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
        "checkpoint": [],
        "endPoints": [],
        "componentName": "DeepLearningFC",
        "connectionOut": [
          "1572267721491"
        ],
        "connectionIn": [
          "1572267710316"
        ],
        "connectionArrow": [
          "1572267721491"
        ],
        "layerSettingsTabName": "Settings"
      },
      "1572267721491": {
        "layerId": "1572267721491",
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
        },
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 130,
            "left": 560
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
        "componentName": "TrainReinforce",
        "connectionOut": [],
        "connectionIn": [
          "1572267716818"
        ],
        "connectionArrow": [],
        "layerSettingsTabName": "Settings"
      }
    }
  }
};

export default reinforcementLearning
