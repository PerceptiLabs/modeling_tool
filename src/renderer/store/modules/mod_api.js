// import configApp from '@/core/globalSettings.js'
//
// import { namespacedCloud, stateCloud, mutationsCloud, actionsCloud } from '@/store/api/mod_cloudAPI.js'
// import { namespacedLocal, stateLocal, mutationsLocal, actionsLocal } from '@/store/api/mod_localAPI.js'
//
// const cloudExport = {
//   namespaced: namespacedCloud,
//   state: stateCloud,
//   mutations: mutationsCloud,
//   actions: actionsCloud
// };
// const localExport = {
//   namespaced: namespacedLocal,
//   state: stateLocal,
//   mutations: mutationsLocal,
//   actions: actionsLocal
// };
//
// //export default configApp.version === 'core_cloud' ?  cloudExport : localExport;
// export default configApp.version === 'core_cloud' ?  localExport : localExport;



const net = require('net');
// run server core
var exec = require('child_process').execFile;

var runServer = function () {
  // exec('core_local/ServerForJS.exe', function (err, data) {
  //   console.log('exe server');
  //   console.log('err exe', err);
  //   console.log('data exe', data);
  // });
  // exec('core_local/app-server.exe', function (err, data) {
  //   console.log('err exe', err);
  //   console.log('data exe', data);
  // });
};
//runServer();
//var clientSocket = new net.Socket();
var header = {
  "byteorder": 'little',
  "content-type": 'text/json',
  "content-encoding": 'utf-8',
  "content-length": 0,
}


var checkData = {
  type: "text/json",
  encoding: "utf-8",
  content: {
    reciever: "Network1",
    action: "getStatus",
    value: ""
  }
};

var sendData =  {
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
};

const namespaced = true;

const state = {
  //symPY: 'Local API'
};

const mutations = {
  SET_symPY(state, value) {
    state.symPY = value
  }
};

const actions = {
  API_startServer() {
    clientSocket.connect(5000, '127.0.0.1', function() {
      console.log('connected to server!');
      //clientSocket.write('<?xml version="1.0" encoding="utf-16"?><JsServerRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><CommandName>Add</CommandName><ParamA>10</ParamA><ParamB>2</ParamB></JsServerRequest>');

    });
  },
  API_stopServer() {
    clientSocket.end();
  },
  API_checkStatus() {
    let c = JSON.stringify(checkData);
    clientSocket.write(c, 'utf8');

    clientSocket.on('end', () => {
      console.log('disconnected from server');
    });

    clientSocket.on('data', (data) => {
      console.log(data);
      clientSocket.end();
    });
  },
  API_startTraining() {
    let d = JSON.stringify(sendData);
    clientSocket.write('2+2');

    clientSocket.on('end', () => {
      console.log('disconnected from server');
    });

    clientSocket.on('data', (data) => {
      console.log(data);
      clientSocket.end();
    });
  },
  API_func() {
    let socketClient = net.connect({host:'127.0.0.1', port:5000}, () => {
      console.log('connected to server!');
      //socketClient.write('<?xml version="1.0" encoding="utf-16"?><JsServerRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><CommandName>Add</CommandName><ParamA>10</ParamA><ParamB>2</ParamB></JsServerRequest>');
      let dataJSON = JSON.stringify(sendData);
      let dataBit = (new TextEncoder('utf-8').encode(dataJSON));
      let dataBitLength = (new TextEncoder('utf-8').encode(dataJSON)).length;


      let headerJSON = JSON.stringify(header).length;
      let headerBit = (new TextEncoder('utf-8').encode(headerJSON));
      //console.log(headerBit);
      header["content-length"] = dataBitLength;
      let headerJ = JSON.stringify(header);
      let headerJBit = (new TextEncoder('utf-8').encode(headerJ));
      let headerJBitLen = (new TextEncoder('utf-8').encode(headerJ)).length;

      let massText = '01' + headerJ + dataJSON;

      let firstBit;
      let secondBit;

      if(headerJBitLen > 256) {
        firstBit = Math.floor(headerJBitLen/256);
        secondBit = headerJBitLen % 256;
      }
      else {
        firstBit = 0;
        secondBit = headerJBitLen;
      }

      console.log(headerJBitLen);
      let arrText = [
        firstBit, secondBit,
        ...headerJBit,
        ...dataBit
      ];
      //console.log(arrText);

      const buf6 = Buffer.from(arrText);
      //console.log(buf6);




      socketClient.write(buf6);



      //let headBit = (new TextEncoder('utf-8').encode(head));



      // console.log(dataBit);
      // socketClient.write(head);
      //socketClient.write(c);
      //socketClient.write('c');
    });

    socketClient.on('end', () => {
      console.log('disconnected from server');
    });

    socketClient.on('data', (data) => {
      //console.log(data);
      console.log('answer server', data.toString());
      //socketClient.end();
    });
    socketClient.on('error', (err) => {
      console.log('answer error server', err);
      //console.log('toString', data.toString());
      socketClient.end();
    });
  }
  // API_func() {
  //   clientSocket.connect(5000, '127.0.0.1', function() {
  //     console.log('connected to server!');
  //     //clientSocket.write('<?xml version="1.0" encoding="utf-16"?><JsServerRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><CommandName>Add</CommandName><ParamA>10</ParamA><ParamB>2</ParamB></JsServerRequest>');
  //     clientSocket.write('202');
  //   });
  //
  //   clientSocket.on('end', () => {
  //     console.log('disconnected from server');
  //   });
  //
  //   clientSocket.on('data', (data) => {
  //     //console.log(data);
  //     console.log('toString', data.toString());
  //     //socketClient.end();
  //   });
  //   clientSocket.on('error', (err) => {
  //     console.log(err);
  //     //console.log('toString', data.toString());
  //     clientSocket.end();
  //   });
  // }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
