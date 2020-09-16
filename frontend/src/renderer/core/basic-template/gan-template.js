const ganTemplate = {
  "project": {},
  "network": {
    "networkName": "GAN Template",
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
    "networkRootFolder": "",
    "networkElementList": {
        "1598914253772": {
          "layerId": "1598914253772",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Data_1",
          "layerType": "Data",
          "layerSettings": {
            "accessProperties": {
              "Columns": [],
              "Sources": [
                {
                  "type": "file",
                  "path": "gan_mnist.npy"
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
            "isSelected": true,
            "position": {
              "top": 420,
              "left": 20
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
            "15989142537730": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598914264624",
              "dst_var": "input"
            }
          ],
          "backward_connections": [],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598914264624": {
          "layerId": "1598914264624",
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
              "top": 420,
              "left": 200
            },
            "OutputDim": "28x28x1",
            "InputDim": "[]",
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
          "componentName": "ProcessReshape",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": false,
          "inputs": {
            "15989142646240": {
              "name": "input",
              "reference_var_id": "15989142537730",
              "reference_layer_id": "1598914253772",
              "isDefault": true
            }
          },
          "outputs": {
            "15989142646240": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598914364500",
              "dst_var": "input2"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598914253772",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598914273257": {
          "layerId": "1598914273257",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Random_1",
          "layerType": "Data",
          "layerSettings": {
            "shape": "(100,)",
            "distribution": "Normal",
            "mean": 0.1,
            "stddev": 0.5,
            "min": 0.1,
            "max": 3.4,
            "Training_Seed": 1111,
            "Testing_Seed": 1234,
            "Validation_Seed": 5678
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
              "top": 20,
              "left": 20
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DataRandom",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {},
          "outputs": {
            "15989142732570": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598914325207",
              "dst_var": "input"
            }
          ],
          "backward_connections": [],
          "previewVariable": "output",
          "previewVariableList": [
            "output"
          ]
        },
        "1598914325207": {
          "layerId": "1598914325207",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Fully Connected_1",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Neurons": 128,
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
              "top": 20,
              "left": 180
            },
            "OutputDim": "128",
            "InputDim": "[100]",
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
            "15989143252070": {
              "name": "input",
              "reference_var_id": "15989142732570",
              "reference_layer_id": "1598914273257",
              "isDefault": true
            }
          },
          "outputs": {
            "15989143252070": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598914328961",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598914273257",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598914328961": {
          "layerId": "1598914328961",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Fully Connected_2",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Neurons": 784,
            "Activation_function": "Sigmoid",
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
              "top": 20,
              "left": 340
            },
            "OutputDim": "784",
            "InputDim": "[128]",
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
            "15989143289610": {
              "name": "input",
              "reference_var_id": "15989143252070",
              "reference_layer_id": "1598914325207",
              "isDefault": true
            }
          },
          "outputs": {
            "15989143289610": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598914357526",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598914325207",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598914357526": {
          "layerId": "1598914357526",
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
              "top": 20,
              "left": 520
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "ProcessReshape",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": false,
          "inputs": {
            "15989143575270": {
              "name": "input",
              "reference_var_id": "15989143289610",
              "reference_layer_id": "1598914328961",
              "isDefault": true
            }
          },
          "outputs": {
            "15989143575270": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598914364500",
              "dst_var": "input1"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598914328961",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598914364500": {
          "layerId": "1598914364500",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Switch_1",
          "layerType": "Other",
          "layerSettings": {
            "selected_layer_id": "1598914357526",
            "selected_var_name": "input1"
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
              "top": 280,
              "left": 700
            },
            "OutputDim": "28x28x1",
            "InputDim": "[[28, 28, 1], []]",
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
          "componentName": "MathSwitch",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": false,
          "inputs": {
            "15989143645000": {
              "name": "input1",
              "reference_var_id": "15989143575270",
              "reference_layer_id": "1598914357526",
              "isDefault": true
            },
            "15989143645001": {
              "name": "input2",
              "reference_var_id": "15989142646240",
              "reference_layer_id": "1598914264624",
              "isDefault": true
            }
          },
          "outputs": {
            "15989143645000": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598914700401",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598914357526",
              "src_var": "output",
              "dst_var": "input1"
            },
            {
              "src_id": "1598914264624",
              "src_var": "output",
              "dst_var": "input2"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598914700401": {
          "layerId": "1598914700401",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Fully Connected_3",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Neurons": 128,
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
              "top": 280,
              "left": 920
            },
            "OutputDim": "128",
            "InputDim": "[]",
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
            "15989147004010": {
              "name": "input",
              "reference_var_id": "15989143645000",
              "reference_layer_id": "1598914364500",
              "isDefault": true
            }
          },
          "outputs": {
            "15989147004010": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598914702587",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598914364500",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598914702587": {
          "layerId": "1598914702587",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Fully Connected_4",
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
              "top": 280,
              "left": 1140
            },
            "OutputDim": "1",
            "InputDim": "[]",
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
            "15989147025870": {
              "name": "input",
              "reference_var_id": "15989147004010",
              "reference_layer_id": "1598914700401",
              "isDefault": true
            }
          },
          "outputs": {
            "15989147025870": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990049723",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598914700401",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990049723": {
          "layerId": "1598990049723",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "GAN_1",
          "layerType": "Training",
          "layerSettings": {
            "Learning_rate": 0.001,
            "Decay_rate": 0.96,
            "Decay_steps": 100000,
            "Momentum": 0.9,
            "Beta_2": 0.999,
            "Beta_1": 0.9,
            "Optimizer": "ADAM",
            "Epochs": 10,
            "batch_size": 3,
            "Use_CPU": true,
            "switch_layer": "Switch_1",
            "Stop_condition": "Epochs",
            "Stop_Target_Accuracy": 0,
            "real_data_layer": "Data_1"
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
              "top": 280,
              "left": 1340
            },
            "OutputDim": "1",
            "InputDim": "[]",
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
          "componentName": "TrainGan",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": false,
          "inputs": {
            "15989900497240": {
              "name": "input",
              "reference_var_id": "15989147025870",
              "reference_layer_id": "1598914702587",
              "isDefault": true
            }
          },
          "outputs": {},
          "forward_connections": [],
          "backward_connections": [
            {
              "src_id": "1598914702587",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        }
      }
  }
}
export default ganTemplate
