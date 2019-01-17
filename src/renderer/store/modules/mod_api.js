import requestApi  from "@/core/api.js";

const net = require('net');
const {spawn} = require('child_process');

const namespaced = true;

const state = {
  statusLocalCore: 'offline', //online
  getStatusTimer: null,
  startWatchGetStatus: false
};

const getters = {
  GET_data_CloseServer(state, getters, rootState, rootGetters) {
    return {
      //reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      reciever: 'server',
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
  SET_startWatchGetStatus(state, value) {
    state.startWatchGetStatus = value
  },
  SET_getStatusTimer(state, value) {
    state.getStatusTimer = value
  },
  RESET_getStatusTimer(state) {
    clearInterval(state.getStatusTimer);
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
    checkCore();
    function checkCore() {
      const theData = getters.GET_data_GetStatus;
      const client = new requestApi();
      client.sendMessage(theData)
        .then((data)=> {
          commit('SET_statusLocalCore', 'online')
        })
        .catch((err) =>{
          if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
            console.log('core offline');
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

  API_getStatus({getters, dispatch, commit}) {
    console.log('API_getStatus');
    const theData = getters.GET_data_GetStatus;
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        dispatch('mod_workspace/SET_statusNetworkCore', data, {root: true})
      })
      .catch((err) =>{
        if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
          console.error(err);
        }
        commit('SET_statusLocalCore', 'offline')
      });
  },

  API_startWatchGetStatus({commit, dispatch}, message) {
    commit('SET_startWatchGetStatus', message);
    message ? startWatch() : stopWatch();

    function startWatch() {
      let timer = setInterval(()=>{
        dispatch('API_getStatus')
      }, 1000);
      commit('SET_getStatusTimer', timer);
    }
    function stopWatch() {
      commit('RESET_getStatusTimer');
    }
  },

  API_startTraining({dispatch, getters, rootGetters}) {
    console.log('API_startTraining');
    const net = rootGetters['mod_workspace/GET_currentNetwork'];
    const elementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
    let message = {
      Hyperparameters: net.networkSettings,
      Layers: {}
    };
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
    dispatch('API_startWatchGetStatus', true)
  },
  API_pauseTraining({dispatch, commit, getters}) {
    const theData = getters.GET_data_PauseTraining;
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });

    state.startWatchGetStatus
      ? dispatch('API_startWatchGetStatus', false)
      : dispatch('API_startWatchGetStatus', true)

  },
  API_stopTraining({dispatch, commit, getters}) {
    console.log('API_stopTraining');
    const theData = getters.GET_data_StopTraining;
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
    dispatch('API_startWatchGetStatus', false);
    dispatch('API_getStatus');
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
