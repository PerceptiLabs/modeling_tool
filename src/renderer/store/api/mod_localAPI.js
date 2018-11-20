const net = require('net');
// run server core
var exec = require('child_process').execFile;

var runServer = function () {
  //exec('core_local/ServerForJS.exe', function (err, data) { });
  exec('core_local/app-server.exe', function (err, data) {
    console.log('err exe', err);
    console.log('data exe', data);
  });
};
runServer();
var checkData = {
  type: "text/json",
  encoding: "utf-8",
  content: {
    reciever: "Network1",
    action: "getStatus",
    value: null
  }
};

var sendData = {
  type: "text/json",
  encoding: "utf-8",
  content: {
    reciever: "Network1",
    action: "Start",
    value: {
      "Hyperparameters" : {
        "Epochs":"10",
        "Batch_size":"32",
        "Data_partition": { //# Needs to add up to 1
          "Training":"0.7", //# Between 0 and 1
          "Validation":"0.2", //# Between 0 and 1
          "Test":"0.1" //# Between 0 and 1
        },
        "Dropout_rate":"0.5",
        "Shuffle_data": true, //#True,  false
        "Save_model_every":"0"
      },
      "Layers" : {
        "1": {
          "Name":"Data_1",
          "Type":"Data",
          "Properties": {
            "Type":"Data",
            "accessProperties":{
              "Type":"Data"
            }
          },
          "backward_connections":[],
          "forward_connections":["2"]
        },
        "2": {
          "Name":"Reshape_1",
          "Type":"Reshape",
          "Properties": {
            "Shape":"[28,28,1]",
            "Permutation":"[0,1,2]",
          },
          "backward_connections":["1"],
          "forward_connections":["3"]
        },
        "3": {
          "Name":"Grayscale_1",
          "Type":"Grayscale",
          "Properties": {
          },
          "backward_connections":["2"],
          "forward_connections":["4"]
        },
        "4": {
          "Name":"Crop_1",
          "Type":"Crop",
          "Properties": {
            "Offset_height":"y1", //# The new upper left corner
            "Offset_width":"x1", //# The new upper left corner
            "Target_height":"y2", //# The new lower right corner minus the new upper left corner
            "Target_width":"x2", //# The new lower right corner minus the new upper left corner
          },
          "backward_connections":["3"],
          "forward_connections":["5"]
        },
        "5": {
          "Name":"Conv_1",
          "Type":"Conv",
          "Properties": {
            "Conv_dim":"2D", //#Automatic, 1D, 2D, 3D
            "Patch_size":"3",
            "Stride":"2",
            "Padding":"'SAME'", //#'SAME', 'VALID'
            "Feature_maps":"8",
            "Activation_function":"Sigmoid", //#Sigmoid, ReLU, Tanh, None
            "Dropout":  false, //#True,  false
            "PoolBool": false, //#True,  false
          },
          "backward_connections":["4"],
          "forward_connections":["6"]
        },
        "6": {
          "Name":"Deconv_1",
          "Type":"Deconv",
          "Properties": {
            "Deconv_dim":"2D", //#Automatic, 1D, 2D, 3D
            "Stride":"2",
            "Padding":"'SAME'", //#'SAME', 'VALID'
            "Feature_maps":"8",
            "Activation_function":"Sigmoid", //#Sigmoid, ReLU, Tanh, None
            "Dropout": false, //#True,  false
          },
          "backward_connections":["5"],
          "forward_connections":["7"]
        },
        "7": {
          "Name":"FC_1",
          "Type":"FC",
          "Properties": {
            "Neurons":"10",
            "Activation_function":"Sigmoid", //#Sigmoid, ReLU, Tanh, None
            "Dropout": false, //#True,  false
          },
          "backward_connections":["6"],
          "forward_connections":["8","9"]
        },
        "8": {
          "Name":"FC_2",
          "Type":"FC",
          "Properties": {
            "Neurons":"10",
            "Activation_function":"Sigmoid", //#Sigmoid, ReLU, Tanh, None
            "Dropout": false, //#True,  false
          },
          "backward_connections":["7"],
          "forward_connections":["9"]
        },
        "9": {
          "Name":"Merge_1",
          "Type":"Merge",
          "Properties": {
            "Type":"Add", //#Add, Sub, Multi, Div
          },
          "backward_connections":["7","8"],
          "forward_connections":["10"]
        },
        "10": {
          "Name":"Recurrent_1",
          "Type":"Recurrent",
          "Properties": {
            "Neurons":"10",
            "Version":"LSTM", //#LSTM, GRU, RNN
            "Time_steps":"5",
          },
          "backward_connections":["9"],
          "forward_connections":["13"]
        },
        "11": {
          "Name":"Data_2",
          "Type":"Data",
          "Properties": {
            "Type":"Data",
            "accessProperties":{
              "Type":"Labels"
            }
          },
          "backward_connections":[],
          "forward_connections":["12"]
        },
        "12": {
          "Name":"OneHot_1",
          "Type":"OneHot",
          "Properties":{
            'N_class':'10',
          },
          "backward_connections":["11"],
          "forward_connections":["13"]
        },
        "13": {
          "Name":"Train_1",
          "Type":"Train",
          "Properties": {
            'N_class':'10',
            "Loss":"Cross_entropy", //#Cross_entropy, Quadratic, W_cross_entropy, Dice
            "Learning_rate":"0.01",
            "Optimizer":"SGD", //#SGD, Momentum, ADAM, RMSprop
          },
          "update_frequency":"1",
          "backward_connections":["10","12"],
          "forward_connections":[]
        }
      }
    }
  }
};

const namespacedLocal = true;
const stateLocal = {
  symPY: 'Local API'
};
const mutationsLocal = {
  SET_symPY(state, value) {
    state.symPY = value
  }
};
const actionsLocal = {
  PY_func({commit}, num) {
    let a = num.x;
    let b = num.y;
    let socketClient = net.connect({host:'127.0.0.1', port:5000}, () => {
      console.log('connected to server!');
      let d = JSON.stringify(sendData);
      //let c = JSON.stringify(checkData);
      //console.log(d);
      socketClient.write('2+2');
      //socketClient.write(c, 'utf8');
    });

    socketClient.on('end', () => {
      console.log('disconnected from server');
    });

    socketClient.on('data', (data) => {
      console.log(data);
      //console.log('toString', data.toString());
      socketClient.end();
      // let response = data.toString();
      // let startDel = response.indexOf('<Result>') + 8;
      // let stopDel = response.indexOf('</Result>');
      // let result = response.slice(startDel, stopDel);
      // commit('SET_symPY', result)
    });
  }
};

export { namespacedLocal, stateLocal, mutationsLocal, actionsLocal }
