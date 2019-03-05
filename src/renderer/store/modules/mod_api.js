import requestApi  from "@/core/api.js";
import {pathCore}  from "@/core/constants.js";

//const net = require('net');
const {spawn} = require('child_process');

function prepareNetwork(elementList) {
  let layers = {};
  elementList.forEach((el)=> {
    if(el.componentName === 'DataData') {
      layers[el.layerId] = {
        Name: el.layerName,
        Type: el.componentName,
        Properties: el.layerSettings,
        //Code: el.coreCode,
        backward_connections: el.connectionIn,
        forward_connections: el.connectionOut
      };
    }
    else {
      layers[el.layerId] = {
        Name: el.layerName,
        Type: el.componentName,
        //Properties: el.layerSettings,
        Code: el.layerCode,
        backward_connections: el.connectionIn,
        forward_connections: el.connectionOut
      };
    }
  });
  return layers
}

const namespaced = true;

const state = {
  statusLocalCore: 'offline', //online
  getStatusTimer: null,
};

const getters = {

};

const mutations = {
  SET_statusLocalCore(state, value) {
    state.statusLocalCore = value
  },
  // SET_startWatchGetStatus(state, value) {
  //   state.startWatchGetStatus = value
  // },
  SET_getStatusTimer(state, value) {
    state.getStatusTimer = value
  },
  RESET_getStatusTimer(state) {
    clearInterval(state.getStatusTimer);
  }
};

const actions = {
  API_runServer({state, commit, dispatch, getters, rootGetters}) {
    let timer;
    let coreIsStarting = false;
    var path = rootGetters['globalView/GET_appPath'];
    startCore();

    function startCore() {
      coreIsStarting = true;
      let openServer;
      switch (process.platform) {
        case 'win32':
          openServer = spawn('core/appServer.exe', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          break;
        case 'darwin':
          if(process.env.NODE_ENV === 'production') {
            openServer = spawn(path + 'core/appServer', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          }
          else {
            openServer = spawn('core/appServer', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          }
          break;
        case 'linux':
          if(process.env.NODE_ENV === 'production') {
            openServer = spawn(path + 'core/appServer', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          }
          else {
            openServer = spawn('core/appServer', [], {stdio: ['ignore', 'ignore', 'pipe'] });
          }
          break;
      }
      openServer.on('error', (err) => {
        console.log(err);
        coreOffline()
      });
      openServer.on('close', (code) => {
        coreOffline()
      });
      waitOnlineCore()
    }
    function waitOnlineCore() {
      timer = setInterval(()=>{
        let status = state.statusLocalCore;
        if(status === 'offline') {
          getCoreRequest();
        }
        else clearInterval(timer);
      }, 5000);
    }
    function getCoreRequest() {
      const theData = {
        reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
        action: 'getStatus',
        value: ''
      };
      const client = new requestApi();
      client.sendMessage(theData)
        .then((data)=> {
          commit('SET_statusLocalCore', 'online')
        })
        .catch((err) =>{
         // console.log(err);
        });
    }
    function coreOffline() {
      commit('SET_statusLocalCore', 'offline');
    }
  },

  API_getStatus({rootGetters, dispatch, commit}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: rootGetters['mod_workspace/GET_currentNetwork'].networkMeta.openTest ? 'getTestStatus' :'getStatus',
      value: ''
    };
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        //console.log('API_getStatus ', data);
        dispatch('mod_workspace/SET_statusNetworkCore', data, {root: true})
      })
      .catch((err) =>{
        if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
          console.error(err);
        }
        commit('SET_statusLocalCore', 'offline')
      });
  },

  API_startTraining({dispatch, getters, rootGetters}) {
    const net = rootGetters['mod_workspace/GET_currentNetwork'];
    const elementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
    let message = {
      Hyperparameters: net.networkSettings,
      Layers: prepareNetwork(elementList)
    };

    const theData = {
      reciever: net.networkID,
      action: "Start",
      value: message
    };
    console.log(theData);
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        dispatch('mod_events/EVENT_startDoRequest', true, {root: true})
      })
      .catch((err) =>{
        console.error(err);
      });

  },
  API_pauseTraining({dispatch, rootState, rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'Pause',
      value: ''
    };
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        dispatch('API_getStatus');
        if(rootState.mod_events.chartsRequest.waitGlobalEvent) {
          dispatch('mod_workspace/SET_statusNetworkCoreStatus', 'Paused', {root: true});
          dispatch('mod_events/EVENT_startDoRequest', false, {root: true})
        }
        else {
          dispatch('mod_events/EVENT_startDoRequest', true, {root: true})
        }
      })
      .catch((err) =>{
        console.error(err);
      });
  },
  API_stopTraining({dispatch, rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'Stop',
      value: ''
    };
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        dispatch('mod_workspace/SET_statusNetworkCoreStatus', 'Stop', {root: true});
        dispatch('mod_events/EVENT_startDoRequest', false, {root: true})
        dispatch('API_getStatus');
      })
      .catch((err) =>{
        console.error(err);
      });
  },
  API_skipValidTraining({rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'SkipToValidation',
      value: ''
    };
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
  },

  API_CLOSE_core({getters, dispatch}) {
    const theData = {
      //reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      reciever: 'server',
      action: 'Close',
      value: ''
    };
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
    dispatch('mod_events/EVENT_startDoRequest', false, {root: true})
  },
  API_postTestStart({rootGetters, rootState, dispatch}) {
    console.log('API_postTestStart');
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'startTest',
      value: ''
    };
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {

      })
      .catch((err) =>{
        console.error(err);
      });
  },
  API_postTestPlay({rootGetters, rootState, dispatch}) {
    console.log('API_postTestPlay');
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'playTest',
      value: ''
    };
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        rootState.mod_events.chartsRequest.waitGlobalEvent
          ? dispatch('mod_events/EVENT_startDoRequest', false, {root: true})
          : dispatch('mod_events/EVENT_startDoRequest', true, {root: true})
      })
      .catch((err) =>{
        console.error(err);
      });
  },
  API_postTestMove({rootGetters, rootState, dispatch}, request) {
    console.log('API_postTestMove ', request);
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: request, //nextStep, previousStep
      value: ''
    };
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        dispatch('mod_api/API_getStatus', null, {root: true});
      })
      .catch((err) =>{
        console.error(err);
      });
  },

  API_getBeForEnd({dispatch, getters, rootGetters}) {
    const elementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: "getNetworkData",
      value: prepareNetwork(elementList)
    };
    console.log(theData);
    const client = new requestApi();
    client.sendMessage(theData)
      .then((data)=> {
        console.log(data);
        dispatch('mod_workspace/SET_elementBeForEnd', data, {root: true});
      })
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
