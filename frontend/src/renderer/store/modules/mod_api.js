import {coreRequest, openWS}  from "@/core/apiWeb.js";
//import coreRequest    from "@/core/apiCore.js";
import { deepCopy }   from "@/core/helpers.js";
import { pathSlash }  from "@/core/constants.js";

const {spawn} = require('child_process');

const namespaced = true;
//let pauseAction = 'Pause';

const state = {
  statusLocalCore: 'offline', //online
  corePid: 0
};

const getters = {
  GET_coreNetwork(state, getters, rootState, rootGetters) {
    const network = rootGetters['mod_workspace/GET_currentNetwork'];
    let layers = {};
    const rootPath = network.networkRootFolder;
    for(let layer in network.networkElementList) {
      const dataLayers = ['DataData', 'DataEnvironment', 'TrainReinforce'];
      const el = network.networkElementList[layer];
      let checkpointPath = deepCopy(el.checkpoint);
      if(el.componentName === 'LayerContainer') continue;
      /*prepare checkpoint*/
      if(rootPath && el.checkpoint.length) {
        const filePath = el.checkpoint[1].slice(0, el.checkpoint[1].length);
        checkpointPath[1] = rootPath + pathSlash + filePath;
      }

      const namesConnectionOut = [];
      const namesConnectionIn = [];

      el.connectionOut.forEach(id => {
        const name =  network.networkElementList[id].layerName;
        namesConnectionOut.push([id, name])
      });

      el.connectionIn.forEach(id => {
        const name =  network.networkElementList[id].layerName;
        namesConnectionIn.push([id, name])
      });

      /*prepare elements*/
      if(dataLayers.includes(el.componentName)) {
        layers[el.layerId] = {
          Name: el.layerName,
          Type: el.componentName,
          Properties: el.layerSettings,
          checkpoint: checkpointPath,
          endPoints: el.endPoints,
          //Code: el.coreCode,
          backward_connections: namesConnectionIn,
          forward_connections: namesConnectionOut
        };
      }
      else {
        layers[el.layerId] = {
          Name: el.layerName,
          Type: el.componentName,
          checkpoint: checkpointPath,
          endPoints: el.endPoints,
          Properties: el.layerSettings,
          Code: el.layerCode,
          backward_connections: namesConnectionIn,
          forward_connections: namesConnectionOut
        };
      }
    }
    return layers
  }
};

const mutations = {
  SET_statusLocalCore(state, value) {
    state.statusLocalCore = value
  },
  set_corePid(state, value) {
    state.corePid = value
  },
};

const actions = {
  //---------------
  //  CORE
  //---------------
  API_runServer({state, commit, rootGetters}) {
    let timer;
    let coreIsStarting = false;
    var path = rootGetters['globalView/GET_appPath'];
    startCore();

    function startCore() {
      // coreIsStarting = true;
      // let openServer;
      // let platformPath = '';
      // switch (process.platform) {
      //   case 'win32':
      //     platformPath = 'core/appServer.exe';
      //     break;
      //   case 'darwin':
      //   case 'linux':
      //     process.env.NODE_ENV === 'production'
      //       ? platformPath = path + 'core/appServer'
      //       : platformPath = 'core/appServer';
      //     break;
      // }
      // openServer = spawn(platformPath, [], {stdio: ['ignore', 'ignore', 'pipe']});
      // commit('set_corePid', openServer.pid);
      // openServer.on('error', (err)=>  { coreOffline() });
      // openServer.on('close', (code)=> { coreOffline() });
      waitOnlineCore()
    }
    function waitOnlineCore() {
      timer = setInterval(()=> {
        let status = state.statusLocalCore;
        if(status === 'offline') getCoreRequest();
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
          //console.log('checkCore', data);
          commit('SET_statusLocalCore', 'online')
        })
        .catch((err)=> {  });
    }
    function coreOffline() {
      commit('SET_statusLocalCore', 'offline');
    }
  },

  API_closeSession(context, reciever) {
    const theData = {
      reciever: reciever,
      action: 'closeSession',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> { return })
      .catch((err)=> { console.error(err) });
  },
  
  API_CLOSE_core() {
    const theData = {
      reciever: 'server',
      action: 'Close',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> { return })
      .catch((err)=> { console.error(err) });
  },


  //---------------
  //  NETWORK TRAINING
  //---------------
  API_startTraining({dispatch, getters, rootGetters}) {
    //const net = rootGetters['mod_workspace/GET_currentNetwork'];
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "Start",
      value: {
        Layers: getters.GET_coreNetwork
      }
    };
    //console.log('API_startTraining', theData);
    coreRequest(theData)
      .then((data)=> {
        dispatch('mod_workspace/EVENT_startDoRequest', true, {root: true});
        dispatch('mod_tracker/EVENT_trainingStart', theData.value, {root: true});
        setTimeout(()=> dispatch('mod_workspace/EVENT_chartsRequest', null, {root: true}), 500)
      })
      .catch((err)=> {
        console.error(err);
      });
  },

  API_pauseTraining({dispatch, rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: rootGetters['mod_workspace/GET_networkCoreStatus'] === 'Paused' ? 'Unpause' : 'Pause', // Pause and Unpause
      value: ''
    };

    coreRequest(theData)
      .then((data)=> {
        if(rootGetters['mod_workspace/GET_networkWaitGlobalEvent']) {
          dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true});
          dispatch('API_getStatus');
          }
        else {
          dispatch('mod_workspace/EVENT_startDoRequest', true, {root: true});
        }
      })
      .catch((err)=> {
        console.error(err);
      });
  },
  API_stopTraining({dispatch, rootGetters}, reciever = null) {

    const theData = {
      reciever: reciever || rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'Stop',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {
        dispatch('mod_workspace/SET_statusNetworkCoreStatus', 'Stop', {root: true});
        dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true});
        dispatch('API_getStatus');
        dispatch('mod_tracker/EVENT_trainingStop', null, {root: true});
      })
      .catch((err)=> {
        console.error(err);
      });
  },

  API_skipValidTraining({rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'SkipToValidation',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {})
      .catch((err)=> {
        console.error(err);
      });
  },

  API_getResultInfo({rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getEndResults',
    };
    //console.log('API_getResultInfo', theData);
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error(err);
      });
  },

  //---------------
  //  NETWORK TESTING
  //---------------
  API_postTestStart({rootGetters, dispatch}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'startTest',
      value: ''
    };
    return coreRequest(theData)
      .then((data)=> { dispatch('mod_tracker/EVENT_testOpenTab', null, {root: true}) })
      .catch((err)=> { console.error(err) });
  },

  API_postTestPlay({rootGetters, dispatch}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'playTest',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {
        if(rootGetters['mod_workspace/GET_networkWaitGlobalEvent']) {
          dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true});
          dispatch('mod_tracker/EVENT_testStop', null, {root: true});
        }
        else {
          dispatch('mod_workspace/EVENT_startDoRequest', true, {root: true});
          dispatch('mod_tracker/EVENT_testPlay', null, {root: true});
        }
      })
      .catch((err)=> {
        console.error(err);
      });
  },

  API_postTestMove({rootGetters, rootState, dispatch}, request) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: request, //nextStep, previousStep
      value: ''
    };
    dispatch('API_updateResults')
      .then(()=> coreRequest(theData))
      .then(()=> {
        dispatch('mod_workspace/EVENT_onceDoRequest', null, {root: true});
        dispatch('mod_tracker/EVENT_testMove', theData.action, {root: true});
      })
      .catch((err)=> {
        console.error(err);
      });
  },


  //---------------
  //  NETWORK SAVE
  //---------------

  API_checkNetworkRunning({rootGetters}, receiver) {
    const theData = {
      reciever: receiver,
      action: "isRunning",
      value: ""
    };
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error('isRunning answer', err);
      });
  },

  API_checkTrainedNetwork({rootGetters}, receiver = null) {
    const theData = {
      reciever: receiver || rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "isTrained"
    };
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error('isTrained answer', err);
      });
  },

  API_saveTrainedNetwork({dispatch, getters, rootGetters}, {Location, frontendNetwork}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "SaveTrained",
      value:  {Location, frontendNetwork}
    };
    //console.log('SaveTrained', theData);
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error('SaveTrained answer', err);
      });
  },


  //---------------
  //  ELEMENT SETTINGS
  //---------------
  API_getInputDim({dispatch, getters, rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "getNetworkInputDim",
      value: getters.GET_coreNetwork
    };
    //console.log('getNetworkInputDim request', theData);
    return coreRequest(theData)
      .then((data)=> {
        //console.log('getNetworkInputDim answer', data);
        if(data) return dispatch('mod_workspace/SET_elementInputDim', data, {root: true});
      })
      .catch((err)=> {
        console.error(err);
      });

  },

  API_getOutputDim({dispatch, getters, rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "getNetworkOutputDim",
      value: getters.GET_coreNetwork
    };
    //console.log('API_getOutputDim');
    return coreRequest(theData)
      .then((data)=> {
        //console.log('API_getOutputDim answer', data);
        if(data) dispatch('mod_workspace/SET_elementOutputDim', data, {root: true});
        return true;
      })
      .catch((err)=> {
        console.error(err);
      });
  },

  API_getPreviewSample({dispatch, getters, rootGetters}, {layerId, varData}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "getPreviewSample",
      value: {
        Id: layerId,
        Network: getters.GET_coreNetwork,
        Variable: varData
      }
    };
    //console.log('getPreviewSample', theData);
    return coreRequest(theData)
      .then((data)=> {
        //console.log('getPreviewSample answer', data);
        return data
      })
      .catch((err)=> {
        console.error(err);
      });
  },

  API_getPreviewVariableList({dispatch, getters, rootGetters}, layerId) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getPreviewVariableList',
      value: {
        Id: layerId,
        Network: getters.GET_coreNetwork
      }
    };
    //console.log('getPreviewVariableList', theData);
    return coreRequest(theData)
      .then((data)=> {
        //console.log('getPreviewVariableList answer', data);
        return data
      })
      .catch((err)=> {
        console.error(err);
      });
  },

  API_getCode({dispatch, getters, rootGetters}, {layerId, settings}) {
    const net = getters.GET_coreNetwork;
    if(settings) net[layerId].Properties = settings;

    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getCode',
      value: {
        Id: layerId,
        Network: net
      }
    };

    console.log('getCode', theData);
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error(err);
      });
  },

  API_getPartitionSummary({getters, rootGetters},  {layerId, settings}) {
    const net = getters.GET_coreNetwork;
    if(settings) net[layerId].Properties = settings;

    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getPartitionSummary',
      value: {
        Id: layerId,
        Network: net
      }
    };
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error(err);
      });
  },

  API_getDataMeta({getters, rootGetters}, {layerId, settings}) {
    const net = getters.GET_coreNetwork;
    if(settings) net[layerId].Properties = settings;

    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getDataMeta',
      value: {
        Id: layerId,
        Network: net
      }
    };
    //console.log('API_getDataMeta', theData);
    return coreRequest(theData)
      .then((data)=> {
        //console.log('API_getDataMeta ans', data);
        return data
      })
      .catch((err)=> {
        console.error(err);
      });
  },
  //---------------
  //  IMPORT/EXPORT
  //---------------
  API_parse({dispatch, getters, rootGetters}, path) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "Parse",
      value: path
    };
    return coreRequest(theData)
      .then((data)=> {
        dispatch('mod_workspace/ADD_network', data.network, {root: true});
      })
      .catch((err)=> {
        console.error('Parse answer', err);
      });
  },

  API_exportData({rootGetters, getters, dispatch}, settings) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'Export',
      value: {
        ...settings,
        frontendNetwork: rootGetters['mod_workspace/GET_currentNetwork'].networkName
      }
    };
    const trackerData = {
      result: '',
      network: getters.GET_coreNetwork,
      settings
    };
    coreRequest(theData)
      .then((data)=> {
        dispatch('globalView/GP_infoPopup', data, {root: true});
        trackerData.result = 'success';
      })
      .catch((err)=> {
        console.error(err);
        dispatch('globalView/GP_errorPopup', err, {root: true});
        trackerData.result = 'error';
      })
      .finally(()=> {
        dispatch('mod_tracker/EVENT_modelExport', trackerData, {root: true});
      })
  },
  //---------------
  //  OTHER
  //---------------
  API_getStatus({rootGetters, dispatch, commit}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: rootGetters['mod_workspace/GET_testIsOpen'] ? 'getTestStatus' :'getStatus',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {
        //console.log('API_getStatus answer', data);
        dispatch('mod_workspace/SET_statusNetworkCore', data, {root: true})
      })
      .catch((err)=> {
        if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
          console.error(err);
        }
        commit('SET_statusLocalCore', 'offline')
      });
  },

  API_setHeadless({dispatch, rootState, rootGetters}, value) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'headless',
      value: value
    };
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error(err);
      });
  },

  API_updateResults({rootGetters}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'updateResults',
      value: ''
    };
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
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