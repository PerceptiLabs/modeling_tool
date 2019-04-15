import coreRequest  from "@/core/apiCore.js";
import {pathCore}   from "@/core/constants.js";

//const net = require('net');
const {spawn} = require('child_process');

function prepareNetwork(elementList) {
  let layers = {};
  elementList.forEach((el)=> {
    let dataLayers = ['DataData', 'DataEnvironment', 'TrainReinforce'];
    if(dataLayers.includes(el.componentName)) {
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
  //getStatusTimer: null,
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
  // SET_getStatusTimer(state, value) {
  //   state.getStatusTimer = value
  // },
  // RESET_getStatusTimer(state) {
  //   clearInterval(state.getStatusTimer);
  // }
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
        action: 'checkCore',
        value: ''
      };
      coreRequest(theData)
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
    coreRequest(theData)
      .then((data)=> {
        //console.log('API_getStatus answer', data);
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
    //console.log(JSON.parse(JSON.stringify(theData)));
    coreRequest(theData)
      .then((data)=> {
        //console.log('API_startTraining ', data);
        dispatch('mod_workspace/EVENT_startDoRequest', true, {root: true});
        setTimeout(()=>dispatch('mod_workspace/EVENT_chartsRequest', null, {root: true}), 500)
      })
      .catch((err) =>{
        console.error(err);
      });
  },
  API_updateResults({dispatch, rootState, rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'updateResults',
      value: ''
    };
    return coreRequest(theData)
      .then((data)=> {
        return data
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
    coreRequest(theData)
      .then((data)=> {
        dispatch('API_getStatus');
        if(rootGetters['mod_workspace/GET_networkWaitGlobalEvent']) {
          dispatch('mod_workspace/SET_statusNetworkCoreStatus', 'Paused', {root: true});
          dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true})
        }
        else {
          dispatch('mod_workspace/EVENT_startDoRequest', true, {root: true})
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
    coreRequest(theData)
      .then((data)=> {
        dispatch('mod_workspace/SET_statusNetworkCoreStatus', 'Stop', {root: true});
        dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true});
        dispatch('API_getStatus');
        return
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
    coreRequest(theData)
      .then((data)=> {})
      .catch((err) =>{
        console.error(err);
      });
  },
  API_exportData({rootGetters, dispatch}, value) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'Export',
      value: value
    };
    //console.log(theData);
    coreRequest(theData)
      .then((data)=> {
        console.log('API_exportData answer', data);
      })
      .catch((err) =>{
        console.error(err);
      });
    dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true})
  },
  API_CLOSE_core({getters, dispatch, rootState}) {
    const theData = {
      //reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      reciever: 'server',
      action: 'Close',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {
        return
      })
      .catch((err) =>{
        console.error(err);
      });
    if(rootState.mod_workspace.workspaceContent.length)
      dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true})
  },
  API_postTestStart({rootGetters, rootState, dispatch}) {
    //console.log('API_postTestStart');
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'startTest',
      value: ''
    };
    return coreRequest(theData)
      .then((data)=> {
        //console.log('API_postTestStart ', data);
      })
      .catch((err) =>{
        console.error(err);
      });
  },
  API_postTestPlay({rootGetters, rootState, dispatch}) {
    //console.log('API_postTestPlay');
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: 'playTest',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {
        rootGetters['mod_workspace/GET_networkWaitGlobalEvent']
          ? dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true})
          : dispatch('mod_workspace/EVENT_startDoRequest', true, {root: true})
      })
      .catch((err) =>{
        console.error(err);
      });
  },
  API_postTestMove({rootGetters, rootState, dispatch}, request) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: request, //nextStep, previousStep
      value: ''
    };
    dispatch('API_updateResults')
      .then(()=> coreRequest(theData))
      .then(()=> dispatch('mod_workspace/EVENT_onceDoRequest', null, {root: true}))
      .catch((err) =>{
        console.error(err);
      });
  },

  API_getInputDim({dispatch, getters, rootGetters}) {
    const elementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: "getNetworkInputDim",
      value: prepareNetwork(elementList)
    };
    return coreRequest(theData)
      .then((data)=> {
        if(data) return dispatch('mod_workspace/SET_elementInputDim', data, {root: true});
      })
      .catch((err) =>{
        console.error(err);
      });

  },
  API_getOutputDim({dispatch, getters, rootGetters}) {
    const elementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetwork'].networkID,
      action: "getNetworkOutputDim",
      value: prepareNetwork(elementList)
    };
    coreRequest(theData)
      .then((data)=> {
        if(data) dispatch('mod_workspace/SET_elementOutputDim', data, {root: true});
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
