const basicTemplate1 = {
  "project": {},
  "network": {
    "networkName": "New_Network",
    "networkID": "net1551878609730",
    "networkSettings": null,
    "networkMeta": {},
    "networkElementList": [
      {
        "layerId": "4918449999997392",
        "layerName": "Data_1",
        "layerType": "Data",
        "layerSettings": "",
        "layerCode": "",
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "top": 59,
          "left": 118,
          "OutputDim": "",
          "InputDim": ""
        },
        "componentName": "DataData",
        "connectionOut": [
          "55294099999940950"
        ],
        "connectionIn": [],
        "trainingData": null
      },
      {
        "layerId": "506581999999471",
        "layerName": "Data_1",
        "layerType": "Data",
        "layerSettings": "",
        "layerCode": "",
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "top": 234,
          "left": 121,
          "OutputDim": "",
          "InputDim": ""
        },
        "componentName": "DataData",
        "connectionOut": [
          "57608199999900536"
        ],
        "connectionIn": [],
        "trainingData": null
      },
      {
        "layerId": "55294099999940950",
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
        "layerCode": "Y=tf.reshape(X, [-1]+[layer_output for layer_output in [28,28,1]]);\nY=tf.transpose(Y,perm=[0]+[i+1 for i in [0,1,2]]);",
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "top": 58,
          "left": 321,
          "OutputDim": "",
          "InputDim": ""
        },
        "componentName": "ProcessReshape",
        "connectionOut": [
          "6940039999992587"
        ],
        "connectionIn": [
          "4918449999997392"
        ],
        "trainingData": null
      },
      {
        "layerId": "57608199999900536",
        "layerName": "OneHot_1",
        "layerType": "Other",
        "layerSettings": {
          "N_class": "10"
        },
        "layerCode": "Y=tf.one_hot(tf.cast(X,dtype=tf.int32),10);",
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "top": 236,
          "left": 375,
          "OutputDim": "",
          "InputDim": ""
        },
        "componentName": "ProcessOneHot",
        "connectionOut": [
          "789022999999579"
        ],
        "connectionIn": [
          "506581999999471"
        ],
        "trainingData": null
      },
      {
        "layerId": "6940039999992587",
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
        "layerCode": "shape=[3,3,X.get_shape()[-1].value,8];\ninitial = tf.truncated_normal(shape, stddev=np.sqrt(2/(3**2 * 8)));\nW = tf.Variable(initial);\ninitial = tf.constant(0.1, shape=[8]);\nb=tf.Variable(initial);\nnode = tf.nn.conv2d(X, W, strides=[1, 2,2, 1], padding='SAME');\nnode=node+b;\nY=tf.sigmoid(node);\n",
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "top": 58,
          "left": 500,
          "OutputDim": "",
          "InputDim": ""
        },
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "7177849999989849"
        ],
        "connectionIn": [
          "55294099999940950"
        ],
        "trainingData": null
      },
      {
        "layerId": "7177849999989849",
        "layerName": "FullyConnected_1",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "10",
          "Activation_function": "Sigmoid",
          "Dropout": false
        },
        "layerCode": "input_size=1\nfor element in X.get_shape().as_list()[1:]:\n  input_size*=element\nshape=[input_size,10];\ninitial = tf.truncated_normal(shape, stddev=0.1);\nW=tf.Variable(initial);\ninitial = tf.constant(0.1, shape=[10]);\nb=tf.Variable(initial);\nflat_node=tf.cast(tf.reshape(X,[-1,input_size]),dtype=tf.float32);\nnode=tf.matmul(flat_node,W);\nnode=node+b;\nY=tf.sigmoid(node);",
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "top": 59,
          "left": 668,
          "OutputDim": "",
          "InputDim": ""
        },
        "componentName": "DeepLearningFC",
        "connectionOut": [
          "789022999999579"
        ],
        "connectionIn": [
          "6940039999992587"
        ],
        "trainingData": null
      },
      {
        "layerId": "789022999999579",
        "layerName": "Normal",
        "layerType": "Training",
        "layerSettings": {
          "Labels": "57608199999900536",
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
        "layerCode": "N_class=list(X.values())[-1].get_shape().as_list()[-1];\nflat_logits = tf.reshape(X['7177849999989849'], [-1, N_class]);\nflat_labels = tf.reshape(X['57608199999900536'], [-1, N_class]);\nloss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=flat_labels, logits=flat_logits));\noptimizer = tf.train.GradientDescentOptimizer(0.01).minimize(loss);\nY=optimizer;\narg_output=tf.argmax(X['7177849999989849'],-1);\narg_label=tf.argmax(X['57608199999900536'],-1);\ncorrect_prediction = tf.equal(arg_output, arg_label);\naccuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32));",
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "top": 237,
          "left": 666,
          "OutputDim": "",
          "InputDim": ""
        },
        "componentName": "TrainNormal",
        "connectionOut": [],
        "connectionIn": [
          "7177849999989849",
          "57608199999900536"
        ],
        "trainingData": null
      }
    ]
  }
};

export default basicTemplate1