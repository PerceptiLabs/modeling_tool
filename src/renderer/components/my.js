let asc = {
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
        "Name": "One Hot",
        "Type": "OneHot",
        "Properties": {"N_class": "10"},
        "backward_connections": ["6149184500000001"],
        "forward_connections": ["7069227500000001"]
      },
      "68600085": {
        "Name": "Fully Connected",
        "Type": "FC",
        "Properties": {"Neurons": "10", "Activation_function": "Sigmoid", "Dropout": false},
        "backward_connections": ["62953770000000000"],
        "forward_connections": ["7069227500000001"]
      },
      "6149184500000001": {
        "Name": "Data",
        "Type": "Data",
        "Properties": {"Type": "Data", "accessProperties": {"Type": "Data", "Path": "D:\\\\Quantum\\mnist\\"}},
        "backward_connections": [],
        "forward_connections": ["66050185"]
      },
      "62953770000000000": {
        "Name": "Data",
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
