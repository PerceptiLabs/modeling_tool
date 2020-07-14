const reinforcementLearning = {
  "project": {},
  "network": {
    "networkName": "Reinforcement Learning",
    "networkID": "",
    "networkSettings": null,
    "networkMeta": {
      "openStatistics": false,
      "openTest": null,
      "zoom": 1,
      "netMode": "edit",
      "coreStatus": {
        "Status": "Stop",
        "Iterations": 60,
        "Epoch": 0,
        "Progress": 0.0000030000001500000076,
        "CPU": 7.8,
        "GPU": 0,
        "Memory": 78.6
      },
      "chartsRequest": {
        "timerID": 205,
        "waitGlobalEvent": false,
        "doRequest": 347,
        "showCharts": 347
      }
    },
    "networkRootFolder": '',
    "networkElementList": {
      "1591386329458": {
        "layerId": "1591386329458",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Environment_1",
        "layerType": "Data",
        "layerSettings": {
          "Type": "Environment",
          "accessProperties": {
            "EnvType": "Gym",
            "Sources": [],
            "Atari": "Breakout",
            "Category": "Local",
            "Type": "Data"
          }
        },
        "layerCode": null,
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": true,
          "position": {
            "top": 280,
            "left": 260
          },
          "OutputDim": "210x160x3",
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
          "1592387860856"
        ],
        "connectionIn": [],
        "connectionArrow": [
          "1592387860856"
        ]
      },
      "1592387860856": {
        "layerId": "1592387860856",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Grayscale_1",
        "layerType": "Other",
        "layerSettings": {},
        "layerSettingsTabName": "Code",
        "layerCode": {
          "Output": "class ProcessGrayscale_Grayscale_1(Tf1xLayer):\n    def __call__(self, x: tf.Tensor, is_training: tf.Tensor = None) -> tf.Tensor:\n        \"\"\" Takes a tensor as input and changes it to grayscale.\"\"\"\n        channels = x.get_shape().as_list()[-1]\n        if channels % 3 == 0:\n            if channels > 3:\n                splits = tf.split(x, int(channels/3), -1)\n                images = []\n                for split in splits:\n                    images.append(tf.image.rgb_to_grayscale(split))\n                y = tf.squeeze(tf.stack(images, -1), -2)\n            else:\n                y = tf.image.rgb_to_grayscale(x)\n        else:\n            y = x\n        self._variables = {k: v for k, v in locals().items() if can_serialize(v)}    \n        self.y = y\n\n        return y\n\n    @property\n    def variables(self) -> Dict[str, Picklable]:\n        \"\"\"Any variables belonging to this layer that should be rendered in the frontend.\n        \n        Returns:\n            A dictionary with tensor names for keys and picklable for values.\n        \"\"\"\n\n        return self._variables.copy()\n\n    @property\n    def trainable_variables(self) -> Dict[str, tf.Tensor]:\n        \"\"\"Any trainable variables belonging to this layer that should be updated during backpropagation. Their gradients will also be rendered in the frontend.\n        \n        Returns:\n            A dictionary with tensor names for keys and tensors for values.\n        \"\"\"\n        return {}\n\n    def get_sample(self, sess=None) -> np.ndarray:\n        \"\"\"Returns a single data sample\"\"\"\n        if sess is not None:\n            y = sess.run(self.y)\n            return y[0]\n        else:\n            return None\n\n    @property\n    def weights(self) -> Dict[str, tf.Tensor]:\n        \"\"\"Any weight tensors belonging to this layer that should be rendered in the frontend.\n\n        Return:\n            A dictionary with tensor names for keys and tensors for values.\n        \"\"\"        \n        return {}\n\n    @property\n    def biases(self) -> Dict[str, tf.Tensor]:\n        \"\"\"Any weight tensors belonging to this layer that should be rendered in the frontend.\n\n        Return:\n            A dictionary with tensor names for keys and tensors for values.\n        \"\"\"        \n        return {}        \n"
        },
        "layerCodeError": null,
        "layerNone": false,
        "layerMeta": {
          "isInvisible": false,
          "isLock": false,
          "isSelected": false,
          "position": {
            "top": 280,
            "left": 410
          },
          "OutputDim": "210x160x1",
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
          "1592387868143"
        ],
        "connectionIn": [
          "1591386329458"
        ],
        "connectionArrow": [
          "1592387868143"
        ]
      },
      "1592387868143": {
        "layerId": "1592387868143",
        "copyId": null,
        "copyContainerElement": null,
        "layerName": "Fully Connected_1",
        "layerType": "Other",
        "layerSettings": {
          "Neurons": "4",
          "Activation_function": "Sigmoid",
          "Dropout": false,
          "Keep_prob": "1",
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
            "left": 560
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
          "1592387884530"
        ],
        "connectionIn": [
          "1592387860856"
        ],
        "connectionArrow": [
          "1592387884530"
        ]
      },
      "1592387884530": {
        "layerId": "1592387884530",
        "copyId": null,
        "copyContainerElement": null,
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
          "History_length": "10",
          "Batch_size": "32"
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
            "top": 280,
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
        "componentName": "TrainReinforce",
        "connectionOut": [],
        "connectionIn": [
          "1592387868143"
        ],
        "connectionArrow": []
      }
    },
  }
};

export default reinforcementLearning
