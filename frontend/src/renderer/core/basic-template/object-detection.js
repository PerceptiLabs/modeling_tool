const objectDetection = {
  network: {
    networkName: "Object Detection",
    networkID: "",
    networkMeta: {},
    networkElementList: {
      1587026797934: {
        layerId: "1587026797934",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_1",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "16",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 110
          },
          OutputDim: "224x224x16",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587041373168"
        ],
        connectionIn: [
          "1587029450671"
        ],
        connectionArrow: [
          "1587041373168"
        ]
      },
      1587026800466: {
        layerId: "1587026800466",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_2",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "32",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 320
          },
          OutputDim: "112x112x32",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587041390463"
        ],
        connectionIn: [
          "1587041373168"
        ],
        connectionArrow: [
          "1587041390463"
        ]
      },
      1587026803582: {
        layerId: "1587026803582",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_3",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "64",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 530
          },
          OutputDim: "56x56x64",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587041810528"
        ],
        connectionIn: [
          "1587041390463"
        ],
        connectionArrow: [
          "1587041810528"
        ]
      },
      1587026806306: {
        layerId: "1587026806306",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_4",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "128",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 850
          },
          OutputDim: "28x28x128",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587041826029"
        ],
        connectionIn: [
          "1587041888749"
        ],
        connectionArrow: [
          "1587041826029"
        ]
      },
      1587026808521: {
        layerId: "1587026808521",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_5",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "256",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 1190
          },
          OutputDim: "14x14x256",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587041964946"
        ],
        connectionIn: [
          "1587041916437"
        ],
        connectionArrow: [
          "1587041964946"
        ]
      },
      1587027900095: {
        layerId: "1587027900095",
        copyId: null,
        copyContainerElement: null,
        layerName: "Data_2",
        layerType: "Data",
        layerSettings: {
          Type: "Data",
          testInfoIsInput: true,
          accessProperties: {
            Columns: "",
            Dataset_size: "",
            Category: "Local",
            Type: "Data",
            Sources: [
              {
                type: "file",
                path: "/Users/mukund/Desktop/od/yolo/labels_5000.npy"
              }
            ],
            PathFake: [],
            Partition_list: [
              [
                70,
                20,
                10
              ]
            ],
            Batch_size: 10,
            Shuffle_data: true,
            Action_space: ""
          }
        },
        layerSettingsTabName: "Computer",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 190,
            left: 530
          },
          OutputDim: "7x7x8",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DataData",
        connectionOut: [
          "1587031688685"
        ],
        connectionIn: [],
        connectionArrow: [
          "1587031688685"
        ]
      },
      1587029450671: {
        layerId: "1587029450671",
        copyId: null,
        copyContainerElement: null,
        layerName: "Data_1",
        layerType: "Data",
        layerSettings: {
          Type: "Data",
          testInfoIsInput: true,
          accessProperties: {
            Columns: [],
            Dataset_size: "",
            Category: "Local",
            Type: "Data",
            Sources: [
              {
                type: "file",
                path: "/Users/mukund/Desktop/od/yolo/train_5000.npy"
              }
            ],
            PathFake: [],
            Partition_list: [
              [
                70,
                20,
                10
              ]
            ],
            Batch_size: 10,
            Shuffle_data: true,
            Action_space: ""
          }
        },
        layerSettingsTabName: "Computer",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 10
          },
          OutputDim: "224x224x3",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DataData",
        connectionOut: [
          "1587026797934"
        ],
        connectionIn: [],
        connectionArrow: [
          "1587026797934"
        ]
      },
      1587031688685: {
        layerId: "1587031688685",
        copyId: null,
        copyContainerElement: null,
        layerName: "Detector_2",
        layerType: "Training",
        layerSettings: {
          Labels: "1587027900095",
          Epochs: "10",
          grid_size: "7",
          batch_size: "32",
          num_box: "2",
          threshold: "0.8",
          lambda_coord: "5",
          lambda_no_obj: "0.7",
          N_class: "1",
          Loss: "Quadratic",
          Class_weights: "1",
          Learning_rate: "0.0001",
          Optimizer: "ADAM",
          Beta_1: "0.9",
          Beta_2: "0.999",
          Momentum: "0.9",
          Decay_steps: "10000",
          Decay_rate: "0.96",
          Training_iters: "20000"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 190,
            left: 670
          },
          OutputDim: "",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "TrainDetector",
        connectionOut: [],
        connectionIn: [
          "1587027900095",
          "1587042016284"
        ],
        connectionArrow: []
      },
      1587041373168: {
        layerId: "1587041373168",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_1_1",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "16",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: true,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 220
          },
          OutputDim: "112x112x16",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587026800466"
        ],
        connectionIn: [
          "1587026797934"
        ],
        connectionArrow: [
          "1587026800466"
        ]
      },
      1587041390463: {
        layerId: "1587041390463",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_2_1",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "32",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: true,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 430
          },
          OutputDim: "56x56x32",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587026803582"
        ],
        connectionIn: [
          "1587026800466"
        ],
        connectionArrow: [
          "1587026803582"
        ]
      },
      1587041810528: {
        layerId: "1587041810528",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_3_1",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "64",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 630
          },
          OutputDim: "56x56x64",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587041888749"
        ],
        connectionIn: [
          "1587026803582"
        ],
        connectionArrow: [
          "1587041888749"
        ]
      },
      1587041826029: {
        layerId: "1587041826029",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_4_1",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "128",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 970
          },
          OutputDim: "28x28x128",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587041916437"
        ],
        connectionIn: [
          "1587026806306"
        ],
        connectionArrow: [
          "1587041916437"
        ]
      },
      1587041888749: {
        layerId: "1587041888749",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_3_1_1",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "64",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: true,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 740
          },
          OutputDim: "28x28x64",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587026806306"
        ],
        connectionIn: [
          "1587041810528"
        ],
        connectionArrow: [
          "1587026806306"
        ]
      },
      1587041916437: {
        layerId: "1587041916437",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_4_1_1",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "128",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: true,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 60,
            left: 1080
          },
          OutputDim: "14x14x128",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587026808521"
        ],
        connectionIn: [
          "1587041826029"
        ],
        connectionArrow: [
          "1587026808521"
        ]
      },
      1587041963991: {
        layerId: "1587041963991",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_5_1",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "256",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: true,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 190,
            left: 1080
          },
          OutputDim: "7x7x256",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587042012253"
        ],
        connectionIn: [
          "1587041964946"
        ],
        connectionArrow: [
          "1587042012253"
        ]
      },
      1587041964946: {
        layerId: "1587041964946",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_5_2",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "3",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "256",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 190,
            left: 1190
          },
          OutputDim: "14x14x256",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587041963991"
        ],
        connectionIn: [
          "1587026808521"
        ],
        connectionArrow: [
          "1587041963991"
        ]
      },
      1587042012253: {
        layerId: "1587042012253",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_6",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "1",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "512",
          Activation_function: "ReLU",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 190,
            left: 950
          },
          OutputDim: "7x7x512",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587042016284"
        ],
        connectionIn: [
          "1587041963991"
        ],
        connectionArrow: [
          "1587042016284"
        ]
      },
      1587042016284: {
        layerId: "1587042016284",
        copyId: null,
        copyContainerElement: null,
        layerName: "Convolution_7",
        layerType: "Other",
        layerSettings: {
          Conv_dim: "2D",
          Patch_size: "1",
          Stride: "1",
          Padding: "SAME",
          Feature_maps: "13",
          Activation_function: "None",
          Dropout: false,
          Keep_prob: "1",
          PoolBool: false,
          Pooling: "Max",
          Pool_area: "2",
          Pool_padding: "SAME",
          Pool_stride: "2"
        },
        layerSettingsTabName: "Settings",
        layerCode: null,
        layerCodeError: null,
        layerNone: false,
        layerMeta: {
          isInvisible: false,
          isLock: false,
          isSelected: false,
          position: {
            top: 190,
            left: 810
          },
          OutputDim: "7x7x13",
          InputDim: "",
          layerContainerName: "",
          layerBgColor: "",
          containerDiff: {
            top: 0,
            left: 0
          }
        },
        checkpoint: [],
        endPoints: [],
        componentName: "DeepLearningConv",
        connectionOut: [
          "1587031688685"
        ],
        connectionIn: [
          "1587042012253"
        ],
        connectionArrow: [
          "1587031688685"
        ]
      }
    },
    networkRootFolder: ""
  }
}

export default objectDetection;