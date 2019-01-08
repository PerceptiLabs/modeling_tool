import requestApi  from "@/core/api.js";

const net = require('net');
const {spawn} = require('child_process');

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
    //check core
    var timer = setInterval(()=>{
      let status = getters.GET_serverStatus;
      if(status === 'Offline') {
        dispatch('API_getStatus')
      }
      else clearInterval(timer);
    }, 5000);
    //start core
    if(getters.GET_serverStatus === 'Offline') {
      let openServer;
      switch (process.platform) {
        case 'win32':
          openServer = spawn('core_local/appServer.exe', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          break;
        case 'darwin':
          let resPath = process.resourcesPath;
          let path = resPath.slice(0, resPath.indexOf('Resources'));
          if(process.env.NODE_ENV === 'production') {
            openServer = spawn(path + 'core_local/appServer', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          }
          else {
            openServer = spawn('core_local/appServer', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          }
          break;
        case 'linux':
          if(process.env.NODE_ENV === 'production') {
            openServer = spawn('../core_local/appServer', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          }
          else {
            openServer = spawn('core_local/appServer', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          }
          break;
      }
      openServer.on('error', (err) => {
        clearInterval(timer);
        alert('Core dont started :(');
      });
      openServer.on('close', (code) => {
        console.log('close core', code);
        commit('SET_serverStatus', {Status: 'Offline'});
      });

      // openServer.stdout.on('data', (data) => {
      //   console.log(`stdout: ${data}`);
      // });
      // openServer.stderr.on('data', (data) => {
      //   console.log(`stderr: ${data}`);
      // });
    }
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
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });

    // watchStatus();
    // function watchStatus() {
    //   let timer = setInterval(()=>{
    //     let status = getters.GET_serverStatus;
    //     // if(status !== 'Offline' || status !== 'Finished') {
    //     //   //console.log('API_startTraining');
    //     //   dispatch('API_getStatus')
    //     // }
    //     // if(status == 'Offline' || status == 'Finished') {
    //     //   clearInterval(timer);
    //     // }
    //     dispatch('API_getStatus')
    //   }, 1000);
    // }
  },
  API_pauseTraining({commit, dispatch, rootGetters}) {
    const theData = rootGetters['mod_workspace/GET_API_dataPauseTraining'];
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
    //commit('RESET_idTimer')
  },
  API_stopTraining({commit, state, dispatch, rootGetters}) {
    const theData = rootGetters['mod_workspace/GET_API_dataStopTraining'];
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
    //commit('RESET_idTimer')
  },
  API_skipValidTraining({dispatch, rootGetters}) {
    const theData = rootGetters['mod_workspace/GET_API_dataSkipValidTraining'];
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
  },

  API_CLOSE_core({rootGetters}) {
    const theData = rootGetters['mod_workspace/GET_API_dataCloseServer'];
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
