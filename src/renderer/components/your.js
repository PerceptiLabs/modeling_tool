let Martin = {
  "reciever": "Network", "action": "Start", "value": {
    "Hyperparameters": {
      "Epochs": "10",
      "Batch_size": "32",
      "Data_partition": {"Training": "70", "Validation": "20", "Test": "10"},
      "Dropout_rate": "0.5",
      "Shuffle_data": true,
      "Save_model_every": "10"
    },
    "Layers": {
      "1": {
        "Name": "Data_1",
        "Type": "Data",
        "Properties": {"Type": "Data", "accessProperties": {"Type": "Data", "Path": "D:\\\\Quantum\\mnist\\"}},
        "backward_connections": [],
        "forward_connections": ["2"]
      },
      "2": {
        "Name": "FC_1",
        "Type": "FC",
        "Properties": {"Neurons": "10", "Activation_function": "Sigmoid", "Dropout": false},
        "backward_connections": ["1"],
        "forward_connections": ["5"]
      },
      "3": {
        "Name": "Data_2",
        "Type": "Data",
        "Properties": {"Type": "Data", "accessProperties": {"Type": "Labels", "Path": "D:\\\\Quantum\\mnist\\"}},
        "backward_connections": [],
        "forward_connections": ["4"]
      },
      "4": {
        "Name": "OneHot_1",
        "Type": "OneHot",
        "Properties": {"N_class": "10"},
        "backward_connections": ["3"],
        "forward_connections": ["5"]
      },
      "5": {
        "Name": "Train_1",
        "Type": "Train",
        "Properties": {
          "N_class": "10",
          "Loss": "Cross_entropy",
          "Learning_rate": "0.01",
          "Training_iters": "20000",
          "Optimizer": "SGD"
        },
        "update_frequency": "1",
        "backward_connections": ["2", "4"],
        "forward_connections": []
      }
    }
  }
}


let Anton = {
  "reciever": "Network", "action": "Start", "value": {
    "Hyperparameters": {
      "isEmpty": false,
      "Epochs": "1",
      "Batch_size": "32",
      "Data_partition": {"Training": "70", "Validation": "20", "Test": "10"},
      "Dropout_rate": "0.5",
      "Shuffle_data": true,
      "Save_model_every": "1"
    }, "Layers": {
      "66050185": {
        "Name": "OneHot_1",
        "Type": "OneHot",
        "Properties": {"N_class": "10"},
        "backward_connections": ["6149184500000001"],
        "forward_connections": ["7069227500000001"]
      },
      "68600085": {
        "Name": "FullyConnected",
        "Type": "FC",
        "Properties": {"Neurons": "10", "Activation_function": "Sigmoid", "Dropout": false},
        "backward_connections": ["62953770000000000"],
        "forward_connections": ["7069227500000001"]
      },
      "6149184500000001": {
        "Name": "Data_1",
        "Type": "Data",
        "Properties": {"Type": "Data", "accessProperties": {"Type": "Data", "Path": "D:\\\\Quantum\\mnist\\"}},
        "backward_connections": [],
        "forward_connections": ["66050185"]
      },
      "62953770000000000": {
        "Name": "Data_1",
        "Type": "Data",
        "Properties": {"Type": "Data", "accessProperties": {"Type": "Data", "Path": "D:\\\\Quantum\\mnist\\"}},
        "backward_connections": [],
        "forward_connections": ["68600085"]
      },
      "7069227500000001": {
        "Name": "Normal",
        "Type": "Train",
        "Properties": {
          "N_class": "10",
          "Loss": "Cross_entropy",
          "Learning_rate": "0.01",
          "Optimizer": "SGD",
          "Training_iters": "20000"
        },
        "backward_connections": ["66050185", "68600085"],
        "forward_connections": []
      }
    }
  }
}
