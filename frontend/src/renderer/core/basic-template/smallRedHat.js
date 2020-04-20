const smallRedHat = {
 "project": {},
 "network": {
  "networkName": "Red Hat",
  "networkID": "net1555685806314",
  "networkSettings": null,
  "networkMeta": {},
  "networkElementList": [
   {
    "layerId": "11919900000008056",
    "layerName": "Data_1",
    "layerType": "Data",
    "layerSettings": {
     "Type": "Data",
     "accessProperties": {
      "Columns": [],
      "Dataset_size": 10,
      "Category": "Local",
      "Type": "Data",
      "Path": [
       "./RedHats"
      ],
      "executeTime": 2.8844106197357178
     }
    },
    "layerCode": "",
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 57,
     "left": 106,
     "OutputDim": "320x640x3",
     "InputDim": "[]"
    },
    "componentName": "DataData",
    "connectionOut": [
     "3656919999999809"
    ],
    "connectionIn": [],
    "trainingData": null
   },
   {
    "layerId": "13568599999998696",
    "layerName": "Data_1",
    "layerType": "Data",
    "layerSettings": {
     "Type": "Data",
     "accessProperties": {
      "Columns": [],
      "Dataset_size": 1,
      "Category": "Local",
      "Type": "Data",
      "Path": [
       "./RedHats.npy"
      ],
      "executeTime": 0.0019516944885253906
     }
    },
    "layerCode": "",
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 188,
     "left": 100,
     "OutputDim": "1",
     "InputDim": "[]"
    },
    "componentName": "DataData",
    "connectionOut": [
     "3405869999999413"
    ],
    "connectionIn": [],
    "trainingData": null
   },
   {
    "layerId": "3405869999999413",
    "layerName": "OneHot_1",
    "layerType": "Other",
    "layerSettings": {
     "N_class": "2"
    },
    "layerCode": "Y=tf.one_hot(tf.cast(X,dtype=tf.int32),2);",
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 228,
     "left": 226,
     "OutputDim": "2",
     "InputDim": "[1]"
    },
    "componentName": "ProcessOneHot",
    "connectionOut": [
     "4051840000000084"
    ],
    "connectionIn": [
     "13568599999998696"
    ],
    "trainingData": null
   },
   {
    "layerId": "3656919999999809",
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
    "layerCode": "shape=[3,3,[320, 640, 3][-1],8];\ninitial = tf.truncated_normal(shape, stddev=np.sqrt(2/(3**2 * 8)));\nW = tf.Variable(initial);\ninitial = tf.constant(0.1, shape=[8]);\nb=tf.Variable(initial);\nnode = tf.nn.conv2d(X, W, strides=[1, 2,2, 1], padding='SAME');\nnode=node+b;\nY=tf.sigmoid(node);\n",
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 78,
     "left": 264,
     "OutputDim": "160x320x8",
     "InputDim": "[320, 640, 3]"
    },
    "componentName": "DeepLearningConv",
    "connectionOut": [
     "378411000000051"
    ],
    "connectionIn": [
     "11919900000008056"
    ],
    "trainingData": null
   },
   {
    "layerId": "378411000000051",
    "layerName": "FullyConnected_1",
    "layerType": "Other",
    "layerSettings": {
     "Neurons": "2",
     "Activation_function": "Sigmoid",
     "Dropout": false
    },
    "layerCode": "input_size=1\nfor element in [160, 320, 8]:\n  input_size*=element\nshape=[input_size,2];\ninitial = tf.truncated_normal(shape, stddev=0.1);\nW=tf.Variable(initial);\ninitial = tf.constant(0.1, shape=[2]);\nb=tf.Variable(initial);\nflat_node=tf.cast(tf.reshape(X,[-1,input_size]),dtype=tf.float32);\nnode=tf.matmul(flat_node,W);\nnode=node+b;\nY=tf.sigmoid(node);",
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 89,
     "left": 412,
     "OutputDim": "2",
     "InputDim": "[160, 320, 8]"
    },
    "componentName": "DeepLearningFC",
    "connectionOut": [
     "4051840000000084"
    ],
    "connectionIn": [
     "3656919999999809"
    ],
    "trainingData": null
   },
   {
    "layerId": "4051840000000084",
    "layerName": "Normal",
    "layerType": "Training",
    "layerSettings": {
     "Labels": "",
     "N_class": "1",
     "Loss": "Cross_entropy",
     "Class_weights": 1,
     "Learning_rate": "0.01",
     "Optimizer": "SGD",
     "Beta_1": "0.1",
     "Beta_2": "0.1",
     "Momentum": "0.1",
     "Decay": "0.1",
     "Training_iters": "20000"
    },
    "layerCode": "N_class=[[2], [2]][-1][-1];\nflat_logits = tf.reshape(X['378411000000051'], [-1, N_class]);\nflat_labels = tf.reshape(X['3405869999999413'], [-1, N_class]);\nloss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=flat_labels, logits=flat_logits));\noptimizer = tf.train.GradientDescentOptimizer(0.01).minimize(loss);\nY=optimizer;\narg_output=tf.argmax(X['378411000000051'],-1);\narg_label=tf.argmax(X['3405869999999413'],-1);\ncorrect_prediction = tf.equal(arg_output, arg_label);\naccuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32));",
    "layerMeta": {
     "isInvisible": false,
     "isLock": false,
     "isSelected": false,
     "top": 233,
     "left": 398,
     "OutputDim": "",
     "InputDim": "[[2], [2]]"
    },
    "componentName": "TrainNormal",
    "connectionOut": [],
    "connectionIn": [
     "378411000000051",
     "3405869999999413"
    ],
    "trainingData": null
   }
  ]
 }
}

export default smallRedHat
