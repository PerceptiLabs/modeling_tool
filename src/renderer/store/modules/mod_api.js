import requestApi  from "@/core/api.js";

const net = require('net');
const exec = require('child_process').spawn;

const namespaced = true;

const state = {
  serverStatus: {
    Status: 'Offline' //Created, Training, Validation, Paused, Finished
  },
};

const getters = {
  GET_serverStatus(state) {
    return state.serverStatus.Status;
  }
};

const mutations = {
  SET_serverStatus(state, value) {
    state.serverStatus = value
  },
  RESET_idTimer(state, value) {
    clearInterval(state.idTimer);
    state.idTimer = value
  }
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
  API_runServer({state, commit, dispatch, getters}) {
    dispatch('API_getStatus');
    setTimeout(()=>{
      if(getters.GET_serverStatus === 'Offline') {
        let openServer = exec('core_local/app-server/appServer.exe', [], {stdio: ['ignore', 'ignore', 'pipe'] });
        openServer.on('close', (code) => {
          console.error(code);
          commit('SET_serverStatus', {Status: 'Offline'});
        });

        // openServer.stdout.on('data', (data) => {
        //   console.log(`stdout: ${data}`);
        // });
        // openServer.stderr.on('data', (data) => {
        //   console.log(`stderr: ${data}`);
        // });
      }
    }, 1000);
    let timer = setInterval(()=>{
      let status = getters.GET_serverStatus;
      if(status === 'Offline') {
        //console.log('API_runServer');
        dispatch('API_getStatus')
      }
      else clearInterval(timer);
    }, 5000);
  },

  API_getStatus({commit, dispatch, rootGetters}) {
    const dataGetStatus = rootGetters['mod_workspace/GET_API_dataGetStatus'];
    const client = new requestApi();
    client.sendMessage(dataGetStatus)
      .then((data)=> {
        commit('SET_serverStatus', data)
      })
      .catch((err) =>{
        if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
          console.error(err);
        }
        commit('SET_serverStatus', {Status: 'Offline'})
      });
  },
  API_startTraining({dispatch, getters, rootGetters}) {
    const net = rootGetters['mod_workspace/GET_currentNetwork'];
    let message = {
      Hyperparameters: net.networkSettings,
      Layers: {}
    };
    net.network.forEach((el)=> {
      let elType = '';

      // switch (el.componentName) {
      //   case 'DataData':
      //     elType = 'Data';
      //     break;
      //   case 'TrainNormal':
      //     elType = 'Train';
      //     break;
      //   case 'ProcessHot':
      //     elType = 'OneHot';
      //     break;
      //   case 'LearnDeepConnect':
      //     elType = 'FC';
      //     break;
      // }

      message.Layers[el.layerId] = {
        Name: el.layerName,
        Type: el.componentName,
        Properties: el.layerSettings,
        backward_connections: el.connectionIn,
        forward_connections: el.connectionOut
      };
    });
    const theData = {
      reciever: net.networkID,
      action: "Start",
      value: message
    };
    console.log(theData);

    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {

      })
      .catch((err) =>{
        if(err.toString() === "Error: connect ECONNREFUSED 127.0.0.1:5000") {
          commit('SET_serverStatus', {Status: 'Offline'})
        }
        else console.error(err);
      });

    watchStatus();
    function watchStatus() {
      let timer = setInterval(()=>{
        let status = getters.GET_serverStatus;
        // if(status !== 'Offline' || status !== 'Finished') {
        //   //console.log('API_startTraining');
        //   dispatch('API_getStatus')
        // }
        // if(status == 'Offline' || status == 'Finished') {
        //   clearInterval(timer);
        // }
        dispatch('API_getStatus')
      }, 1000);
    }
  },
  API_pauseTraining({commit, dispatch, rootGetters}) {
    // var theData = {
    //   reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkName,
    //   action: "Pause",
    //   value: ""
    // };
    const theData = rootGetters['mod_workspace/GET_API_dataPauseTraining'];
    dispatch('API_PUSH_core', theData);
    commit('RESET_idTimer')
  },
  API_stopTraining({commit, state, dispatch, rootGetters}) {
    // var theData = {
    //   reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkName,
    //   action: "Stop",
    //   value: ""
    // };
    const theData = rootGetters['mod_workspace/GET_API_dataStopTraining'];
    dispatch('API_PUSH_core', theData);
    commit('RESET_idTimer')
  },
  API_skipValidTraining({dispatch, rootGetters}) {
    // var theData = {
    //   reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkName,
    //   action: "SkipToValidation",
    //   value: ""
    // };
    const theData = rootGetters['mod_workspace/GET_API_dataSkipValidTraining'];
    dispatch('API_PUSH_core', theData)
  },
  // API_getStatistics({dispatch, rootGetters}) {
  //   // var theData = {
  //   //   reciever: "Network1",
  //   //   action: "getStatistics",
  //   //   value: {
  //   //     layerId: '2',
  //   //     variable: 'W',
  //   //     innervariable: ''
  //   //   }
  //   // };
  //   var theData = {
  //     reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkName,
  //     action: "getLayerStatistics",//getStatistics
  //     value: {
  //       layerId:"2",
  //       layerType:"FC",//FC //Data ///Train //OneHot
  //       view:"Output" //Output, Weights&Bias // Predicition  Accuracy
  //     }
  //     // value: {
  //     //   layerId: '4',
  //     //   variable:"Y",
  //     //   innervariable:"" //last arrey
  //     // }
  //   };
  //   dispatch('API_PUSH_core', theData)
  // },
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
