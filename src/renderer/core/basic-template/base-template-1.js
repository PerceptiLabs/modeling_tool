const basicTemplate1 = {
 "project": {},
 "network": {
  "networkName": "New_Network",
  "networkID": "net1548268206058",
  "networkSettings": {
   "Epochs": "1",
   "Batch_size": "32",
   "Data_partition": {
    "Training": "70",
    "Validation": "20",
    "Test": "10"
   },
   "Dropout_rate": "0.5",
   "Shuffle_data": true,
   "Save_model_every": "0"
  },
  "networkMeta": {},
  "networkElementList": [
   {
    "layerId": "49200299999999976",
    "layerName": "Reshape",
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
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 72,
     "left": 419
    },
    "componentName": "ProcessReshape",
    "connectionOut": [
     "8792470000000003"
    ],
    "connectionIn": [
     "6073389999999199"
    ],
    "trainingData": null
   },
   {
    "layerId": "5082220000000007",
    "layerName": "OneHot_1",
    "layerType": "Other",
    "layerSettings": {
     "N_class": "10"
    },
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 301,
     "left": 498
    },
    "componentName": "ProcessOneHot",
    "connectionOut": [
     "9087070000000040"
    ],
    "connectionIn": [
     "630618999999715"
    ],
    "trainingData": null
   },
   {
    "layerId": "8792470000000003",
    "layerName": "Convolution_1",
    "layerType": "Other",
    "layerSettings": {
     "Conv_dim": "2D",
     "Patch_size": "3",
     "Stride": "2",
     "Padding": "'SAME'",
     "Feature_maps": "8",
     "Activation_function": "Sigmoid",
     "Dropout": false,
     "PoolBool": false,
     "Pooling": "Max",
     "Pool_area": "2",
     "Pool_padding": "'SAME'",
     "Pool_stride": "2"
    },
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 72,
     "left": 646
    },
    "componentName": "DeepLearningConv",
    "connectionOut": [
     "8905700000000025"
    ],
    "connectionIn": [
     "49200299999999976"
    ],
    "trainingData": null
   },
   {
    "layerId": "8905700000000025",
    "layerName": "FullyConnected_1",
    "layerType": "Other",
    "layerSettings": {
     "Neurons": "10",
     "Activation_function": "Sigmoid",
     "Dropout": false
    },
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 73,
     "left": 882
    },
    "componentName": "DeepLearningFC",
    "connectionOut": [
     "9087070000000040"
    ],
    "connectionIn": [
     "8792470000000003"
    ],
    "trainingData": null
   },
   {
    "layerId": "9087070000000040",
    "layerName": "Normal",
    "layerType": "Training",
    "layerSettings": {
     "N_class": "1",
     "Loss": "Cross_entropy",
     "Learning_rate": "0.01",
     "Optimizer": "SGD",
     "Training_iters": "20000"
    },
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 303,
     "left": 883
    },
    "componentName": "TrainNormal",
    "connectionOut": [],
    "connectionIn": [
     "8905700000000025",
     "5082220000000007"
    ],
    "trainingData": null
   },
   {
    "layerId": "6073389999999199",
    "layerName": "Data_1",
    "layerType": "Data",
    "layerSettings": {
     "Type": "Data",
     "accessProperties": {
      "Category": "Local",
      "Type": "Data",
      "Path": ""
     }
    },
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 68,
     "left": 178
    },
    "componentName": "DataData",
    "connectionOut": [
     "49200299999999976"
    ],
    "connectionIn": [],
    "trainingData": null
   },
   {
    "layerId": "630618999999715",
    "layerName": "Data_1",
    "layerType": "Data",
    "layerSettings": {
     "Type": "Data",
     "accessProperties": {
      "Category": "Local",
      "Type": "Labels",
      "Path": ""
     }
    },
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 299,
     "left": 186
    },
    "componentName": "DataData",
    "connectionOut": [
     "5082220000000007"
    ],
    "connectionIn": [],
    "trainingData": null
   }
  ]
 }
};

export default basicTemplate1