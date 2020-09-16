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
    "networkRootFolder": "",
    "networkElementList": {
        "1598990439670": {
          "layerId": "1598990439670",
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
                  "path": "object_detection_input.npy"
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
          "layerSettingsTabName": "Computer",
          "layerCode": null,
          "layerCodeError": null,
          "layerNone": false,
          "layerMeta": {
            "isInvisible": false,
            "isLock": false,
            "isSelected": false,
            "position": {
              "top": 40,
              "left": 20
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
            "15989904396700": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990485236",
              "dst_var": "input"
            }
          ],
          "backward_connections": [],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990485236": {
          "layerId": "1598990485236",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_1",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 16,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": false,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "top": 40,
              "left": 180
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989904852360": {
              "name": "input",
              "reference_var_id": "15989904396700",
              "reference_layer_id": "1598990439670",
              "isDefault": true
            }
          },
          "outputs": {
            "15989904852360": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990486422",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990439670",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990486422": {
          "layerId": "1598990486422",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_2",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 16,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": true,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "top": 40,
              "left": 360
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989904864220": {
              "name": "input",
              "reference_var_id": "15989904852360",
              "reference_layer_id": "1598990485236",
              "isDefault": true
            }
          },
          "outputs": {
            "15989904864220": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990493118",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990485236",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990493118": {
          "layerId": "1598990493118",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_3",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 32,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": false,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "top": 40,
              "left": 540
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989904931180": {
              "name": "input",
              "reference_var_id": "15989904864220",
              "reference_layer_id": "1598990486422",
              "isDefault": true
            }
          },
          "outputs": {
            "15989904931180": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990497355",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990486422",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990497355": {
          "layerId": "1598990497355",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_4",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 32,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": true,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "top": 40,
              "left": 720
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989904973550": {
              "name": "input",
              "reference_var_id": "15989904931180",
              "reference_layer_id": "1598990493118",
              "isDefault": true
            }
          },
          "outputs": {
            "15989904973550": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990527723",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990493118",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990527723": {
          "layerId": "1598990527723",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_5",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 64,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": false,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "left": 20
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989905277230": {
              "name": "input",
              "reference_var_id": "15989904973550",
              "reference_layer_id": "1598990497355",
              "isDefault": true
            }
          },
          "outputs": {
            "15989905277230": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990531401",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990497355",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990531401": {
          "layerId": "1598990531401",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_6",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 64,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": true,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "left": 220
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989905314010": {
              "name": "input",
              "reference_var_id": "15989905277230",
              "reference_layer_id": "1598990527723",
              "isDefault": true
            }
          },
          "outputs": {
            "15989905314010": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990532554",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990527723",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990532554": {
          "layerId": "1598990532554",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_7",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 128,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": false,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "left": 420
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989905325540": {
              "name": "input",
              "reference_var_id": "15989905314010",
              "reference_layer_id": "1598990531401",
              "isDefault": true
            }
          },
          "outputs": {
            "15989905325540": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990533854",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990531401",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990533854": {
          "layerId": "1598990533854",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_8",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 128,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": true,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "left": 600
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989905338540": {
              "name": "input",
              "reference_var_id": "15989905325540",
              "reference_layer_id": "1598990532554",
              "isDefault": true
            }
          },
          "outputs": {
            "15989905338540": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598995218129",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990532554",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990536189": {
          "layerId": "1598990536189",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_10",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 256,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": true,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "top": 500,
              "left": 20
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989905361890": {
              "name": "input",
              "reference_var_id": "15989952181340",
              "reference_layer_id": "1598995218129",
              "isDefault": true
            }
          },
          "outputs": {
            "15989905361890": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990538091",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598995218129",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990538091": {
          "layerId": "1598990538091",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_11",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 512,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": false,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "top": 500,
              "left": 200
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989905380910": {
              "name": "input",
              "reference_var_id": "15989905361890",
              "reference_layer_id": "1598990536189",
              "isDefault": true
            }
          },
          "outputs": {
            "15989905380910": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990539626",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990536189",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990539626": {
          "layerId": "1598990539626",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_12",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 13,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "None",
            "PoolBool": false,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "top": 500,
              "left": 400
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989905396260": {
              "name": "input",
              "reference_var_id": "15989905380910",
              "reference_layer_id": "1598990538091",
              "isDefault": true
            }
          },
          "outputs": {
            "15989905396260": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990616678",
              "dst_var": "predictions"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990538091",
              "src_var": "output",
              "dst_var": "input"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990616678": {
          "layerId": "1598990616678",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Detector_1",
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
            "Loss": "Quadratic",
            "Labels": "1598990633508",
            "Class_weights": 1,
            "Use_CPU": true,
            "Stop_Target_Accuracy": 0,
            "Stop_condition": "Epochs"
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
              "top": 500,
              "left": 780
            },
            "OutputDim": "0",
            "InputDim": "",
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
          "componentName": "TrainDetector",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": false,
          "inputs": {
            "15989906166780": {
              "name": "predictions",
              "reference_var_id": "15989905396260",
              "reference_layer_id": "1598990539626",
              "isDefault": true
            },
            "15989906166781": {
              "name": "labels",
              "reference_var_id": "15989906335080",
              "reference_layer_id": "1598990633508",
              "isDefault": true
            }
          },
          "outputs": {},
          "forward_connections": [],
          "backward_connections": [
            {
              "src_id": "1598990539626",
              "src_var": "output",
              "dst_var": "predictions"
            },
            {
              "src_id": "1598990633508",
              "src_var": "output",
              "dst_var": "labels"
            }
          ],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598990633508": {
          "layerId": "1598990633508",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Data_2",
          "layerType": "Data",
          "layerSettings": {
            "accessProperties": {
              "Columns": [],
              "Sources": [
                {
                  "type": "file",
                  "path": "object_detection_labels.npy"
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
            "isSelected": false,
            "position": {
              "top": 580,
              "left": 580
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
            "15989906335080": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990616678",
              "dst_var": "labels"
            }
          ],
          "backward_connections": [],
          "previewVariable": "output",
          "previewVariableList": []
        },
        "1598995218129": {
          "layerId": "1598995218129",
          "copyId": null,
          "copyContainerElement": null,
          "layerName": "Convolution_9",
          "layerType": "Other",
          "layerSettings": {
            "Dropout": false,
            "Keep_prob": 1,
            "Batch_norm": false,
            "Conv_dim": "2D",
            "Patch_size": 3,
            "Feature_maps": 256,
            "Stride": 1,
            "Padding": "SAME",
            "Activation_function": "ReLU",
            "PoolBool": false,
            "Pooling": "Max",
            "Pool_area": 2,
            "Pool_padding": "SAME",
            "Pool_stride": 2
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
              "left": 780
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
          "chartData": {},
          "checkpoint": [],
          "endPoints": [],
          "componentName": "DeepLearningConv",
          "connectionOut": [],
          "connectionIn": [],
          "connectionArrow": [],
          "visited": true,
          "inputs": {
            "15989952181340": {
              "name": "input",
              "reference_var_id": "15989905338540",
              "reference_layer_id": "1598990533854",
              "isDefault": true
            }
          },
          "outputs": {
            "15989952181340": {
              "name": "output",
              "reference_var": "output"
            }
          },
          "forward_connections": [
            {
              "src_var": "output",
              "dst_id": "1598990536189",
              "dst_var": "input"
            }
          ],
          "backward_connections": [
            {
              "src_id": "1598990533854",
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

export default objectDetection;