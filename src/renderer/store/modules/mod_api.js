import requestApi  from "@/core/api.js";

const net = require('net');
const {spawn} = require('child_process');

const namespaced = true;

const state = {
  statusLocalCore: 'offline' //online
};

const getters = {
  GET_data_CloseServer(state, getters, rootState, rootGetters) {
    return {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      //reciever: 'server',
      action: 'Close',
      value: ''
    };
  },
  GET_data_PauseTraining(state, getters, rootState, rootGetters) {
    return {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'Pause',
      value: ''
    };
  },
  GET_data_StopTraining(state, getters, rootState, rootGetters) {
    return {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'Stop',
      value: ''
    };
  },
  GET_data_SkipValidTraining(state, getters, rootState, rootGetters) {
    return {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'SkipToValidation',
      value: ''
    }
  },
  GET_data_GetStatus(state, getters, rootState, rootGetters) {
    return {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'getStatus', //getIter
      value: ''
    };
  },
};

const mutations = {
  SET_statusLocalCore(state, value) {
    state.statusLocalCore = value
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
    let timer;
    let coreIsStarting = false;
    //checkCore();

    function checkCore() {
      const theData = getters.GET_data_GetStatus;
      const client = new requestApi();
      client.sendMessage(theData)
        .then((data)=> {
          commit('SET_statusLocalCore', 'online')
        })
        .catch((err) =>{
          if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
            console.error(err);
          }
          coreOffline();
          if(!coreIsStarting) {
            startCore();
            waitOnlineCore();
          }
        });
    }
    function startCore() {
      coreIsStarting = true;
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
        //clearInterval(timer);
        coreOffline()
      });
      openServer.on('close', (code) => {
        console.log('close core', code);
        coreOffline()
      });
    }
    function waitOnlineCore() {
      timer = setInterval(()=>{
        let status = state.statusLocalCore;
        if(status === 'offline') {
          checkCore();
        }
        else clearInterval(timer);
      }, 5000);
    }
    function coreOffline() {
      commit('SET_statusLocalCore', 'offline');
    }
  },

  API_getStatus({commit, dispatch, getters}) {
    const theData = getters.GET_data_GetStatus;
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        //commit('SET_serverStatus', data)
      })
      .catch((err) =>{
        if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
          console.error(err);
        }
        commit('SET_statusLocalCore', 'Offline')
      });
  },
  API_startTraining({dispatch, getters, rootGetters}) {
    const net = rootGetters['mod_workspace/GET_currentNetwork'];
    const elementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
    let message = {
      Hyperparameters: net.networkSettings,
      Layers: {}
    };
    console.log('Hyperparameters ', message.Hyperparameters);
    elementList.forEach((el)=> {
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
  API_pauseTraining({commit, getters}) {
    const theData = getters.GET_data_PauseTraining;
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
    //commit('RESET_idTimer')
  },
  API_stopTraining({commit, getters}) {
    const theData = getters.GET_data_StopTraining;
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
    //commit('RESET_idTimer')
  },
  API_skipValidTraining({getters}) {
    const theData = getters.GET_data_SkipValidTraining;
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
  },

  API_CLOSE_core({getters}) {
    const theData = getters.GET_data_CloseServer;
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
