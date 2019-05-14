const basicTemplate1 = {
  "project": {},
  "network": {
    "networkName": "Image Classification",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {},
    "networkElementList": {
      "1557863743895": {
        "layerId": "1557863743895",
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
              "G:\\progects\\test-info\\mnist_split\\mnist_input.npy"
            ],
            "executeTime": 0.07318449020385742
          }
        },
        "layerCode": "",
        "layerMeta": {
          "displayNone": false,
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 88,
            "left": 143
          },
          "OutputDim": "784",
          "InputDim": "[]",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "DataData",
        "connectionOut": [
          "1557863747097"
        ],
        "connectionIn": []
      },
      "1557863744661": {
        "layerId": "1557863744661",
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
              "G:\\progects\\test-info\\mnist_split\\mnist_labels.npy"
            ],
            "executeTime": 0.003995656967163086
          }
        },
        "layerCode": "",
        "layerMeta": {
          "displayNone": false,
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 278,
            "left": 176
          },
          "OutputDim": "1",
          "InputDim": "[]",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "DataData",
        "connectionOut": [
          "1557863812968"
        ],
        "connectionIn": []
      },
      "1557863747097": {
        "layerId": "1557863747097",
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
          "displayNone": false,
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 89,
            "left": 314
          },
          "OutputDim": "28x28x1",
          "InputDim": "[784]",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "ProcessReshape",
        "connectionOut": [
          "1557863815036"
        ],
        "connectionIn": [
          "1557863743895"
        ]
      },
      "1557863812968": {
        "layerId": "1557863812968",
        "layerName": "OneHot_1",
        "layerType": "Other",
        "layerSettings": {
          "N_class": "10"
        },
        "layerCode": "Y=tf.one_hot(tf.cast(X,dtype=tf.int32),10);",
        "layerMeta": {
          "displayNone": false,
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 294,
            "left": 347
          },
          "OutputDim": "10",
          "InputDim": "[1]",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "ProcessOneHot",
        "connectionOut": [
          "1557863819624"
        ],
        "connectionIn": [
          "1557863744661"
        ]
      },
      "1557863815036": {
        "layerId": "1557863815036",
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
        "layerCode": "shape=[3,3,[28, 28, 1][-1],8];\ninitial = tf.truncated_normal(shape, stddev=np.sqrt(2/(3**2 * 8)));\nW = tf.Variable(initial);\ninitial = tf.constant(0.1, shape=[8]);\nb=tf.Variable(initial);\nnode = tf.nn.conv2d(X, W, strides=[1, 2,2, 1], padding='SAME');\nnode=node+b;\nY=tf.sigmoid(node);\n",
        "layerMeta": {
          "displayNone": false,
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 70,
            "left": 470
          },
          "OutputDim": "14x14x8",
          "InputDim": "[28, 28, 1]",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "DeepLearningConv",
        "connectionOut": [
          "1557863815992"
        ],
        "connectionIn": [
          "1557863747097"
        ]
      },
      "1557863815992": {
        "layerId": "1557863815992",
        "layerName": "FullyConnected_1",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "10",
          "Activation_function": "Sigmoid",
          "Dropout": false
        },
        "layerCode": "input_size=1\nfor element in [14, 14, 8]:\n  input_size*=element\nshape=[input_size,10];\ninitial = tf.truncated_normal(shape, stddev=0.1);\nW=tf.Variable(initial);\ninitial = tf.constant(0.1, shape=[10]);\nb=tf.Variable(initial);\nflat_node=tf.cast(tf.reshape(X,[-1,input_size]),dtype=tf.float32);\nnode=tf.matmul(flat_node,W);\nnode=node+b;\nY=tf.sigmoid(node);",
        "layerMeta": {
          "displayNone": false,
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 109,
            "left": 696
          },
          "OutputDim": "10",
          "InputDim": "[14, 14, 8]",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "DeepLearningFC",
        "connectionOut": [
          "1557863819624"
        ],
        "connectionIn": [
          "1557863815036"
        ]
      },
      "1557863819624": {
        "layerId": "1557863819624",
        "layerName": "Normal",
        "layerType": "Training",
        "layerSettings": {
          "Labels": "1557863812968",
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
        "layerCode": "N_class=[[10], [10]][-1][-1];\nflat_logits = tf.reshape(X['1557863815992'], [-1, N_class]);\nflat_labels = tf.reshape(X['1557863812968'], [-1, N_class]);\nloss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=flat_labels, logits=flat_logits));\noptimizer = tf.train.GradientDescentOptimizer(0.01).minimize(loss);\nY=optimizer;\narg_output=tf.argmax(X['1557863815992'],-1);\narg_label=tf.argmax(X['1557863812968'],-1);\ncorrect_prediction = tf.equal(arg_output, arg_label);\naccuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32));",
        "layerMeta": {
          "displayNone": false,
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 285,
            "left": 673
          },
          "OutputDim": "",
          "InputDim": "[[10], [10]]",
          "containerDiff": {
            "top": 0,
            "left": 0
          }
        },
        "componentName": "TrainNormal",
        "connectionOut": [],
        "connectionIn": [
          "1557863812968",
          "1557863815992"
        ]
      }
    }
  }
};

export default basicTemplate1