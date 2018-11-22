import requestApi  from "@/core/api.js";
// run server core
var exec = require('child_process').execFile;

var runServer = function () {
  exec('core_local/app-server.exe', function (err, data) {
    console.log('err exe', err);
    console.log('data exe', data);
  });
};
//runServer();
//var clientSocket = new net.Socket();

var sendData =  {
    reciever: "Network1",
    action: "Start",
    value: {
      "Hyperparameters" : {
        "Epochs":"1",
        "Batch_size":"32",
        "Data_partition": {
          "Training":"0.7",
          "Validation":"0.2",
          "Test":"0.1"
        },
        "Dropout_rate":"0.5",
        "Shuffle_data": true,
        "Save_model_every":"10",
        isEmpty: true,
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
          "forward_connections":["2","3"]
        },
        "2": {
          "Name":"FC_1",
          "Type":"FC",
          "Properties": {
            "Neurons":"10",
            "Activation_function":"Sigmoid",
            "Dropout": false,
          },
          "backward_connections":["1"],
          "forward_connections":["4"]
        },
        "3": {
          "Name":"FC_2",
          "Type":"FC",
          "Properties": {
            "Neurons":"10",
            "Activation_function":"Sigmoid",
            "Dropout": false,
          },
          "backward_connections":["1"],
          "forward_connections":["4"]
        },
        "4": {
          "Name":"Merge_1",
          "Type":"Merge",
          "Properties": {
            "Type":"Add",
          },
          "backward_connections":["2","3"],
          "forward_connections":["7"]
        },
        "5": {
          "Name":"Data_2",
          "Type":"Data",
          "Properties": {
            "Type":"Data",
            "accessProperties":{
              "Type":"Labels"
            }
          },
          "backward_connections":[],
          "forward_connections":["6"]
        },
        "6": {
          "Name":"OneHot_1",
          "Type":"OneHot",
          "Properties":{
            'N_class':'10',
          },
          "backward_connections":["5"],
          "forward_connections":["7"]
        },
        "7": {
          "Name":"Train_1",
          "Type":"Train",
          "Properties": {
            'N_class':'10',
            "Loss":"Cross_entropy",
            "Learning_rate":"0.01",
            "Training_iters":"20000",
            "Optimizer":"SGD",
          },
          "update_frequency":"1",
          "backward_connections":["4","6"],
          "forward_connections":[]
        }
      }
    }
};

let data2 = {
  reciever: "Network1",
  action: "Start",
  value: {
    "Hyperparameters": {
      "Epochs": "10",
      "Batch_size": "32",
      "Data_partition": {
        "Training": "0.7",
        "Validation": "0.2",
        "Test": "0.1"
      },
      "Dropout_rate": "0.5",
      "Shuffle_data": true,
      "Save_model_every": "10"
    },
    "Layers": {
      "1": {
        "Name": "Data_1",
        "Type": "Data",
        "Properties": {
          "Type": "Data",
          "accessProperties": {
            "Type": "Data"
          }
        },
        "backward_connections": [],
        "forward_connections": ["2"]
      },
      "2": {
        "Name": "FC_1",
        "Type": "FC",
        "Properties": {
          "Neurons": "10",
          "Activation_function": "Sigmoid",
          "Dropout": false,
        },
        "backward_connections": ["1"],
        "forward_connections": ["3"]
      },
      "3": {
        "Name": "Data_2",
        "Type": "Data",
        "Properties": {
          "Type": "Data",
          "accessProperties": {
            "Type": "Labels"
          }
        },
        "backward_connections": [],
        "forward_connections": ["4"]
      },
      "4": {
        "Name": "OneHot_1",
        "Type": "OneHot",
        "Properties": {
          'N_class': '10',
        },
        "backward_connections": ["3"],
        "forward_connections": ["5"]
      },
      "5": {
        "Name": "Train_1",
        "Type": "Train",
        "Properties": {
          'N_class': '10',
          "Loss": "Cross_entropy",
          "Learning_rate": "0.01",
          "Training_iters": "20000",
          "Optimizer": "SGD",
        },
        "update_frequency": "1",
        "backward_connections": ["2", "4"],
        "forward_connections": []
      },
    }
  }
}

const namespaced = true;

const state = {
  dataAnswer: null,
  serverStatus: null,
};

const mutations = {
  SET_dataAnswer(state, value) {
    state.dataAnswer = value
  },
  SET_serverStatus(state, value) {
    state.serverStatus = value
  }
};


// Actions(value):

// Start(Json Network)
// Stop(None)
// Pause(None)
// SkipToValidation(None)
// Save(path)
// getStatistics({“layerId”:string,”variable”:string,”innervariable”:string})    (Send “”, empty string, if not use field)
// getStatus(None)


const actions = {
  API_getStatus({dispatch, rootGetters}) {
    var theData = {
      reciever: rootGetters['mod_workspace/currentNetwork'].networkName,
      action: "getStatus",
      value: ""
    };
    // var timerId = setTimeout(()=> {
    //   dispatch('API_PUSH_core', theData)
    //   }, 1000);
    // clearTimeout(timerId);
    let answer = requestApi(theData)
  },
  API_startTraining({dispatch, rootGetters}) {
    const net = rootGetters['mod_workspace/currentNetwork'];
    let message = {
      Hyperparameters: net.networkSettings,
      Layers: {}
    };
    net.network.forEach((el)=> {
      let elType = '';

      switch (el.componentName) {
        case 'DataData':
          elType = 'Data';
          break;
        case 'TrainNormal':
          elType = 'Train';
          break;
        case 'ProcessHot':
          elType = 'OneHot';
          break;
        case 'LearnDeepConnect':
          elType = 'FC';
          break;

      }

      message.Layers[el.layerId] = {
        Name: el.layerName,
        Type: elType,
        Properties: el.layerSettings,
        backward_connections: el.connectionIn,
        forward_connections: el.connectionOut
      };
    });
    const theData = {
      reciever: net.networkName,
      action: "Start",
      value: message
    };
    //console.log(theData);
    dispatch('API_PUSH_core', theData)
  },
  API_pauseTraining({dispatch, rootGetters}) {
    var theData = {
      reciever: rootGetters['mod_workspace/currentNetwork'].networkName,
      action: "Pause",
      value: ""
    };
    dispatch('API_PUSH_core', theData)
  },
  API_stopTraining({dispatch, rootGetters}) {
    var theData = {
      reciever: rootGetters['mod_workspace/currentNetwork'].networkName,
      action: "Stop",
      value: ""
    };
    dispatch('API_PUSH_core', theData)
  },
  API_skipValidTraining({dispatch, rootGetters}) {
    var theData = {
      reciever: rootGetters['mod_workspace/currentNetwork'].networkName,
      action: "SkipToValidation",
      value: ""
    };
    dispatch('API_PUSH_core', theData)
  },
  API_getStatistics({dispatch, rootGetters}) {
    // var theData = {
    //   reciever: "Network1",
    //   action: "getStatistics",
    //   value: {
    //     layerId: '2',
    //     variable: 'W',
    //     innervariable: ''
    //   }
    // };
    var theData = {
      reciever: rootGetters['mod_workspace/currentNetwork'].networkName,
      action: "getLayerStatistics",
      value: {
        layerId:"1",
        layerType:"Data",//FC
        view:"" //Output, Weights&Bias
      }
    };
    dispatch('API_PUSH_core', theData)
  },
  API_CLOSE_core({dispatch, rootGetters}) {
    var theData = {
      reciever: rootGetters['mod_workspace/currentNetwork'].networkName,
      action: "Close",
      value: ""
    };
    dispatch('API_PUSH_core', theData)
  },
  API_PUSH_core({commit}, data) {
    const header = {
      "byteorder": 'little',
      "content-type": 'text/json',
      "content-encoding": 'utf-8',
      "content-length": 0,
    };

    let socketClient = net.connect({host:'127.0.0.1', port:5000}, () => {

      let dataJSON = JSON.stringify(data);
      let dataByte = (new TextEncoder('utf-8').encode(dataJSON));
      let dataByteLength = dataByte.length;

      header["content-length"] = dataByteLength;

      let headerJSON = JSON.stringify(header);
      let headerByte = (new TextEncoder('utf-8').encode(headerJSON));
      let headerByteLength = headerByte.length;

      let firstByte = 0;
      let secondByte = headerByteLength;

      if(headerByteLength > 256) {
        firstByte = Math.floor(headerByteLength / 256);
        secondByte = headerByteLength % 256;
      }
      //console.log(dataJSON);
      const message = [
        firstByte, secondByte,
        ...headerByte,
        ...dataByte
      ];

      const buf6 = Buffer.from(message);
      socketClient.write(buf6);
    });

    socketClient.on('end', ()=>{});

    socketClient.on('data', (data) => {
      let dataString = data.toString();
      let clearData = dataString.slice(dataString.indexOf('}{"result": ') + 12, dataString.length-1);
      socketClient.end();
      return clearData
    });
    socketClient.on('error', (err) => {
      console.log('answer error server', err.toString());
      socketClient.end();
    });
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
