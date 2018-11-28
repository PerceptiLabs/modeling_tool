import requestApi  from "@/core/api.js";

const net = require('net');
const exec = require('child_process').execFile;

function runServer() {
  exec('core_local/app-server.exe', (err, data)=> {
    console.log('err exe', err);
    console.log('data exe', data);
  });
}
//runServer();

//var clientSocket = new net.Socket();


let data2 = {
  reciever: "Network",
  action: "Start",
  value: {
    "Hyperparameters": {
      "Epochs": "20",
      "Batch_size": "32",
      "Data_partition": {
        "Training": "70",
        "Validation": "20",
        "Test": "20"
      },
      "Dropout_rate": "0.5",
      "Shuffle_data": true,
      "Save_model_every": "20"
    },
    "Layers": {
      "1": {
        "Name": "Data_1",
        "Type": "Data",
        "Properties": {
          "Type": "Data",
          "accessProperties": {
            "Type": "Data",
            "Path": "D:\\\\Quantum\\mnist\\"
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
        "forward_connections": ["5"]
      },
      "3": {
        "Name": "Data_2",
        "Type": "Data",
        "Properties": {
          "Type": "Data",
          "accessProperties": {
            "Type": "Labels",
            "Path": "D:\\\\Quantum\\mnist\\"
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
  idTimer: null
};

const mutations = {
  SET_dataAnswer(state, value) {
    state.dataAnswer = value
  },
  SET_serverStatus(state, value) {
    state.serverStatus = value
  },
  SET_idTimer(state, value) {
    state.serverStatus = value
  },
  RESET_idTimer(state, value) {
    clearInterval(state.idTimer);
    state.idTimer = value
  }
};

const getters = {

};
// Actions(value):

// Start(Json Network)
// Stop(None)
// Pause(None)
// SkipToValidation(None)
// Save(path)
// Close(None)
// getStatistics({“layerId”:string,”variable”:string,”innervariable”:string})    (Send “”, empty string, if not use field)
// getLayerStatistics({“layerId”:string,”variable”:string,”innervariable”:string})    (Send “”, empty string, if not use field)
// getStatus(None)


const actions = {
  API_runServer({state, commit, dispatch}) {
    let timer;
    // setTimeout(()=>{
    //   timer = setInterval(()=>{
    //     dispatch('API_getStatus')
    //   }, 3000)
    // }, 10000);
    commit('SET_idTimer', timer)
  },
  API_getStatus({commit, dispatch, rootGetters}) {
    const dataGetStatus = rootGetters['mod_workspace/GET_API_dataGetStatus'];
    const client = new requestApi();

    client.sendMessage(dataGetStatus)
      .then((data)=> {
        let jsnData = JSON.parse(data);
        //console.log('status', jsnData);
        commit('SET_serverStatus', jsnData)
      })
      .catch((err) =>{
        console.error(err);
        commit('RESET_idTimer')
      });
  },
  API_startTraining({dispatch, rootGetters}) {
    const net = rootGetters['mod_workspace/GET_currentNetwork'];
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
    console.log(theData);
    //dispatch('API_PUSH_core', theData)
    dispatch('API_PUSH_core', data2)
  },
  API_pauseTraining({commit, dispatch, rootGetters}) {
    var theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkName,
      action: "Pause",
      value: ""
    };
    dispatch('API_PUSH_core', theData)
    commit('RESET_idTimer')
  },
  API_stopTraining({commit, state, dispatch, rootGetters}) {
    var theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkName,
      action: "Stop",
      value: ""
    };

    dispatch('API_PUSH_core', theData);
    commit('RESET_idTimer')
  },
  API_skipValidTraining({dispatch, rootGetters}) {
    var theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkName,
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
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkName,
      action: "getLayerStatistics",//getStatistics
      value: {
        layerId:"2",
        layerType:"FC",//FC //Data ///Train //OneHot
        view:"Output" //Output, Weights&Bias // Predicition  Accuracy
      }
      // value: {
      //   layerId: '4',
      //   variable:"Y",
      //   innervariable:"" //last arrey
      // }
    };
    dispatch('API_PUSH_core', theData)
  },
  API_CLOSE_core({commit, dispatch, rootGetters}) {
    const theData = rootGetters['mod_workspace/GET_API_dataCloseServer'];
    dispatch('API_PUSH_core', theData);
    commit('RESET_idTimer')
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
      console.log(dataJSON);
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
      console.log(clearData);
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
  getters,
  mutations,
  actions
}
