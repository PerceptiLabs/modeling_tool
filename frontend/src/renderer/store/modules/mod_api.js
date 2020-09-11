import {coreRequest as coreRequestWeb, openWS}  from "@/core/apiWeb.js";
import coreRequestElectron from "@/core/apiCore.js";
import { deepCopy, parseJWT, isWeb, stringifyNetworkObjects }   from "@/core/helpers.js";
import { createNotebookJson }   from "@/core/helpers/notebook-helper.js";
import { pathSlash }  from "@/core/constants.js";
import {isElectron} from "@/core/helpers";
import { PROJECT_DEFAULT_FOLDER } from "../../core/constants";
import cloneDeep from 'lodash.clonedeep';
let coreRequest = null;
let ipcRenderer = null;
let spawn = null;


if(!(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1)) {
  coreRequest = coreRequestWeb;
} else {
const electron =  require('electron');
  spawn = require('child_process').spawn;
  ipcRenderer = electron.ipcRenderer;
  coreRequest = coreRequestElectron
};


const namespaced = true;
//let pauseAction = 'Pause';

const state = {
  statusLocalCore: 'offline', //online
  corePid: 0,
  headlessState: [],
};

const getters = {
  GET_coreNetworkElementList(state, getters, rootState, rootGetters) {
    return rootGetters['mod_workspace/GET_currentNetworkElementList'];
  },
  GET_coreNetwork(state, getters, rootState, rootGetters) {
    const network = rootGetters['mod_workspace/GET_currentNetwork'];
    let layers = {};
    const rootPath = network.networkRootFolder;
    for(let layer in network.networkElementList) {
      const el = network.networkElementList[layer];
      let checkpointPath = deepCopy(el.checkpoint);
      if(el.componentName === 'LayerContainer') continue;
      /*prepare checkpoint*/
      if(rootPath && el.checkpoint.length) {
        const filePath = el.checkpoint[1].slice(0, el.checkpoint[1].length);
        checkpointPath[1] = rootPath + pathSlash + filePath;
      }

      // const namesConnectionOut = [];
      // const namesConnectionIn = [];

      // el.connectionOut.forEach(id => {
      //   const name =  network.networkElementList[id].layerName;
      //   namesConnectionOut.push([id, name])
      // });

      // el.connectionIn.forEach(id => {
      //   const name =  network.networkElementList[id].layerName;
      //   namesConnectionIn.push([id, name])
      // });

      /*prepare elements*/
      layers[el.layerId] = {
        Name: el.layerName,
        Type: el.componentName,
        checkpoint: checkpointPath,
        endPoints: el.endPoints,
        Properties: el.layerSettings,
        Code: el.layerCode,
        backward_connections: el.backward_connections,
        forward_connections: el.forward_connections,
        visited: el.visited,
        previewVariable: el.previewVariable
      };

    }
    return layers
  },
  get_headlessState: (state) => (networkId) => {
    const headlessState = state.headlessState.find(hs => hs.id === networkId);
    
    if (!headlessState) { return; }

    return headlessState.isHeadless;
  },
  // maybe another flag for within or not alayerId
  GET_descendentsIds: (state, getters) => (pivotLayer, withPivot = true) => { 
    const networkList = getters.GET_coreNetworkElementList;
    let listIds = getDescendants(pivotLayer, []);
    if(withPivot) {
      listIds.push(pivotLayer.layerId);
    }
    return listIds;
    function getDescendants(networkElement, dataIds){
      if(networkElement.forward_connections.length === 0) {
        return dataIds;
      }
      for(let index in networkElement.forward_connections) {
        const layerId = networkElement.forward_connections[index].dst_id;
        dataIds.push(layerId);
        getDescendants(networkList[layerId], dataIds);
      }
      return dataIds;
    }
  },
};

const mutations = {
  SET_statusLocalCore(state, value) {
    state.statusLocalCore = value
  },
  set_corePid(state, value) {
    state.corePid = value
  },
  set_headlessState(state, { id, value }) {
    const headlessState = state.headlessState.find(hs => hs.id === id);

    if (!headlessState) {
      state.headlessState.push({
        id: id,
        isHeadless: value
      });
    } else {
      headlessState.isHeadless = value;
    }
  }
};

const actions = {
  SET_corePid({commit}, id) {
    commit('set_corePid', id);
    ipcRenderer.send('save-corePid', id)
  },
  //---------------
  //  CORE
  //---------------
  checkCoreAvailability({commit, dispatch, state}) {
      const theData = {
        action: 'checkCore',
        value: ''
      };
      return coreRequest(theData)
        .then(()=> {
          // set user when core switch from offline to online
          if(state.statusLocalCore === 'offline') {
            dispatch('API_setUserInCore');
            commit('SET_statusLocalCore', 'online');
          }
        })
        .catch(()=> {
          if(state.statusLocalCore === 'online') {
            commit('SET_statusLocalCore', 'offline');
          }
        });
  },
  coreStatusWatcher({dispatch}) {  
    setInterval(() => {
    dispatch('checkCoreAvailability')
  }, 2000)
  },
  API_runServer({state, dispatch, commit, rootGetters}) {
    let timer;
    let coreIsStarting = false;
    var path = rootGetters['globalView/GET_appPath'];
    let userEmail = rootGetters['mod_user/GET_userEmail'];
    startCore();

    function startCore() {
      if(isElectron()) {
        coreIsStarting = true;
        let openServer;
        let platformPath = '';
        switch (process.platform) {
          case 'win32':
            platformPath = 'core/appServer.exe';
            break;
          case 'darwin':
          case 'linux':
            process.env.NODE_ENV === 'production'
              ? platformPath = path + 'core/appServer'
              : platformPath = 'core/appServer';
            break;
        }
        console.log('PID: ', process.pid);
        openServer = spawn(platformPath, ['-f', process.pid, '-u', userEmail], {stdio: ['ignore', 'ignore', 'pipe']});
        dispatch('SET_corePid', openServer.pid);
        openServer.on('error', (err)=>  {
          console.log('core error', err)
          coreOffline()
        });
        openServer.on('close', (code)=> {
          console.log('core close', code)
          coreOffline()
        });
        waitOnlineCore()
      }
      if(isWeb()) {
        dispatch('checkCoreAvailability');
        dispatch("coreStatusWatcher");
      }
      
    }
    function waitOnlineCore() {
      timer = setInterval(()=> {
        let status = state.statusLocalCore;
        if(status === 'offline') {
          if(isWeb()) {
            dispatch('checkCoreAvailability');
          } else {
            getCoreRequest();
          }
        }
        else {
          clearInterval(timer);
        }
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
        .catch((err)=> { if(isWeb()) {coreOffline()}  });
    }
    function coreOffline() {
      commit('SET_statusLocalCore', 'offline');
    }
    function getCoreRequest() {
      const theData = {
        action: 'checkCore',
        value: ''
      };
      coreRequest(theData)
        .then((data)=> {
          //console.log('checkCore', data);
          commit('SET_statusLocalCore', 'online');
          if(isWeb()) {
            dispatch('API_setUserInCore');
          }
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
  //  NETWORK SETTING UPDATING
  //---------------
  // API_updateNetworkSetting({getters, dispatch}, layerId) {
  //   const theData = {
  //     action: 'getSettingsRecommendation',
  //     value: {
  //       Id: layerId,
  //       Network: getters.GET_coreNetwork,
  //     }
  //   };


  //   coreRequest(theData)
  //     .then((data)=> {
  //       console.warn(data);
  //       if (data) {
  //         for (var el in data) {
  //           const saveSettings = {
  //             'elId': el,
  //             'set': data[el].Properties,
  //             'code': data[el].Code
  //           };
            
  //           dispatch('mod_workspace/SET_elementSettings', deepCopy(saveSettings), {root: true});      
  //         }
  //       }
  //     })
  //     .catch((err)=> {
  //       console.log("Calling getSettingsRecommendation", err)
  //     })
  // },
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
    if(isWeb()) {
      dispatch('globalView/ShowCoreNotFoundPopup', null, { root: true });
    }
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
    if(isWeb()) {
      dispatch('globalView/ShowCoreNotFoundPopup', null, { root: true });
    }
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
  // NETWORK LOAD
  //---------------
  
  API_loadNetwork({rootGetters}, path) {
    const theData = {
      reciever: "",
      action: "getJsonModel",
      value: path
    }

    return coreRequest(theData)
      .then((data) => data)
      .catch((err) => {
        console.error('loading network error: ', err);
      });
  },

  API_getRootFolder() {
    const theData = {
      reciever: '',
      action: 'getRootFolder',
      value: ''
    }

    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error(err);
      })
  },

  //---------------
  //  NETWORK SAVE
  //---------------
  API_loadNetwork(ctx, path) {
    const theData = {
      reciever: "",
      action: "getJsonModel",
      value: path
    }

    return coreRequest(theData)
      .then((data) => data)
      .catch((err) => {
        console.error('loading network error: ', err);
      });
  },
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

  API_saveTrainedNetwork({dispatch, getters, rootGetters}, {Location, frontendNetwork, networkName}) {
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "SaveTrained",
      value:  {Location, frontendNetwork, networkName}
    };
    //console.log('SaveTrained', theData);
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error('SaveTrained answer', err);
        return Promise.reject();
      });
  },
  API_saveModel({dispatch, getters, rootGetters}, {model}) {
    // location shoul be getted from default location of project
    // /model_${model.apiMeta.model_id}
    const save_path = `${model.apiMeta.location}`;
    
    const theData = {
      action: "saveJsonModel",
      value:  {
        reciever: model,
        path: save_path,
        json: stringifyNetworkObjects(model),
      }
    };
    return coreRequest(theData)
      .then((data)=> {
        return data;
      })
      .catch((err)=> {
        console.error('SaveModel', err);
      });
  },
  API_getModel(ctx, path) {
    const theData = {
      action: 'getJsonModel',
      value: path
    }
    return coreRequest(theData)
      .then(res=> {
        return res;
      }).catch(e => {
        console.log(e);
      })
  },

  API_saveJsonModel({rootGetters}, {path}) {
    const networkJson = cloneDeep(rootGetters['mod_workspace/GET_currentNetwork']);
    const healthNetworkElementList = {};
    Object.keys(networkJson.networkElementList).map(key => {
      const el = networkJson.networkElementList[key];
      healthNetworkElementList[key] = {
        ...el,
        chartData: {}
      }
    })

    const healthNetworkJson = {
      ...networkJson,
      networkElementList: healthNetworkElementList
    }
    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'saveJsonModel',
      value:  {
        json: stringifyNetworkObjects(healthNetworkJson),
        path
      }
    };
    
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error('saveJsonModel answer', err);
        return Promise.reject();
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

    if(isWeb()) {
      dispatch('globalView/ShowCoreNotFoundPopup', null, { root: true });
    }
    return coreRequest(theData)
      .then((data)=> {
        if(data) return dispatch('mod_workspace/SET_elementInputDim', data, {root: true});
      })
      .catch((err)=> {
        console.error(err);
      });

  },

  API_getOutputDim({dispatch, getters, rootGetters}) {
    // const theData = {
    //   reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
    //   action: "getNetworkOutputDim",
    //   value: getters.GET_coreNetwork
    // };
    // if(isWeb()) {
    //   dispatch('globalView/ShowCoreNotFoundPopup', null, { root: true });
    // }
    // //console.log('API_getOutputDim');
    // // @todo -- this request are not longer used instead is used  ->>>> mod_api/API_getBatchPreviewSample
    // return coreRequest(theData)
    //   .then((data)=> {
    //     //console.log('API_getOutputDim answer', data);
    //     if(data){
    //       dispatch('mod_workspace/SET_elementOutputDim', data, {root: true});
    //       dispatch('mod_workspace-notifications/setNotifications', {
    //         networkId:rootGetters['mod_workspace/GET_currentNetworkId'],
    //         kernelResponses: data
    //       }, {root: true});
    //     }
    //     return true;
    //   })
    //   .catch((err)=> {
    //     console.error(err);
    //   });
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
    // console.log('getPreviewSample', theData);
    return coreRequest(theData)
      .then((data)=> {
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
    // console.log('getPreviewVariableList Request', theData);
    return coreRequest(theData)
      .then((data)=> {
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

    // console.log('getCode', theData);
    // console.log('getCode - payload', theData);
    // console.log('getCode - layerId', layerId);
    if(isWeb()) {
      dispatch('globalView/ShowCoreNotFoundPopup', null, { root: true });
    }
    return coreRequest(theData)
      .then((data)=> {
        // console.log('getCode - response', data);
        // console.log('getCode - layerId', layerId);
        return data
      })
      .catch((err)=> {
        console.log('API_getCode error');
        console.error(err);
      });
  },

  API_getGraphOrder({ rootGetters }, jsonNetwork) {

    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getGraphOrder',
      value: jsonNetwork
    };

    return coreRequest(theData)
      .then((data)=> {
        // console.log('API_getGraphOrder data', data);
        return data;
      })
      .catch((err)=> {
        // console.log('API_getGraphOrder error');
        console.error(err);
      });
  },

  API_getGraphOrder({ rootGetters }, jsonNetwork) {

    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getGraphOrder',
      value: jsonNetwork
    };

    return coreRequest(theData)
      .then((data)=> {
        // console.log('API_getGraphOrder data', data);
        return data;
      })
      .catch((err)=> {
        // console.log('API_getGraphOrder error');
        console.error(err);
      });
  },

  API_getNotebookImports({ rootGetters }, jsonNetwork) {

    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getNotebookImports',
      value: jsonNetwork
    };

    return coreRequest(theData)
      .then((data)=> {
        // console.log('API_getNotebookImports data', data);
        return data;
      })
      .catch((err)=> {
        // console.log('API_getNotebookImports error');
        console.error(err);
      });
  },

  API_getNotebookRunscript({ rootGetters }, jsonNetwork) {

    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getNotebookRunscript',
      value: jsonNetwork
    };

    return coreRequest(theData)
      .then((data)=> {
        // console.log('API_getNotebookRunscript data', data);
        return data;
      })
      .catch((err)=> {
        // console.log('API_getNotebookRunscript error');
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

  async API_exportData({rootGetters, getters, dispatch}, settings) {

    const theData = {
      reciever: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'Export',
      value: await makePayload.call(this, settings)
    };

    if(isWeb()) {
      dispatch('globalView/ShowCoreNotFoundPopup', null, { root: true });
    }
    const trackerData = {
      result: '',
      network: getters.GET_coreNetwork,
      settings
    };
    coreRequest(theData)
      .then((data)=> {
        const thePath = data.substring(data.indexOf('/'));
        const { apiMeta } = rootGetters['mod_workspace/GET_currentNetwork'];
        dispatch('mod_workspace/SET_model_saved_version_location', thePath, {root: true});
        dispatch('mod_project/updateModel', {
          ...apiMeta,
          saved_version_location: thePath
        }, {root: true});
        
        dispatch('globalView/GP_infoPopup', data, {root: true});
        trackerData.result = 'success';
      })
      .catch((err)=> {
        console.error(err);
        if(settings.Type !== 'ipynb') {
          dispatch('globalView/GP_errorPopup', 'Kernel is not connected', {root: true});
        }
        // dispatch('globalView/GP_errorPopup', err, {root: true});
        trackerData.result = 'error';
      })
      .finally(()=> {
        dispatch('mod_tracker/EVENT_modelExport', trackerData, {root: true});
      })

    async function makePayload(settings = null) {
      if (!settings || settings.Type === 'TFModel') {
        return ({
          ...settings,
          frontendNetwork: rootGetters['mod_workspace/GET_currentNetwork'].networkName
        });
      }
  
      if (settings.Type === 'ipynb') {
        // current 'this' is the Vuex store object
        try {
          const payload = await createNotebookJson(this);
          return ({
            ...settings,
            frontendNetwork: settings.name,
            NotebookJson: payload
          });
        } 
        catch(err) {
          dispatch('globalView/GP_errorPopup', 'Kernel is not connected', {root: true});
        }
      }
    }
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
        dispatch('mod_workspace/SET_statusNetworkCore', {...rootGetters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus, ...data}, {root: true})
      })
      .catch((err)=> {
        if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
          console.error(err);
        }
        commit('SET_statusLocalCore', 'offline')
      });
  },
  API_getModelStatus({rootGetters, dispatch, commit}, modelId) {
    const theData = {
      reciever: modelId,
      // action: rootGetters['mod_workspace/GET_testIsOpen'] ? 'getTestStatus' :'getStatus',
      // @todo ask about this twho types getTestStatus && getStatus, difference between them.
      action: 'getStatus',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {
        dispatch('mod_workspace/SET_statusNetworkCoreDinamically', {
          ...data,
          modelId: modelId,
        }, {root: true})
      })
      .catch((err)=> {
        if(err.toString() !== "Error: connect ECONNREFUSED 127.0.0.1:5000") {
          console.error(err);
        }
        commit('SET_statusLocalCore', 'offline')
      });
  },

  API_setHeadless({commit, getters, rootGetters}, value) {
    // Checking headless state and only sending if:
    // - different or
    // - never sent before
    
    // This is because the Kernel can current not handle a request
    // that sets the same state (i.e. true -> true).

    const networkHeadlessState = getters.get_headlessState(rootGetters['mod_workspace/GET_currentNetworkId']);
    
    commit('set_headlessState', {
      id: rootGetters['mod_workspace/GET_currentNetworkId'],
      value: value
    });

    // if the value is the same, don't send it
    if (networkHeadlessState === value) {
      return Promise.resolve();
    }

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

  API_setUserInCore({}) {
    const haveNotToken = (token) => ((token === 'undefined') || (token === null));
    let userToken = sessionStorage.getItem('currentUser');
    if (haveNotToken(userToken)) {
      userToken = localStorage.getItem('currentUser');
    }
    if (haveNotToken(userToken)) { return; }
    const userObject = parseJWT(userToken);

    const theData = {
      reciever: '',
      action: 'setUser',
      value: userObject.email
    };
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error(err);
      });
  },
  API_createFolder(ctx, {folder_path}) {
    if (!folder_path) { return; }

    const theData = {
      receiver: '',
      action: 'createFolder',
      value: {
        "folder_path": folder_path
      },
    }
    
    return coreRequest(theData)
      .then(res => {
        return res;
      })
      .catch(err => {
        console.error(err);
      });
  },
  API_isDirExist (ctx, path) {
    const theData = {
      receiver: '',
      action: 'isDirExist',
      value: {
        path
      }
    };
    return coreRequest(theData)
      .then(res => res)
      .catch(e => console.error(e));
  },
  API_resolveDir (ctx, path) {
    // resolves ~ for windows
    // expands to the full path for POSIX
    const theData = {
      receiver: '',
      action: 'resolveDir',
      value: {
        path
      }
    };
    return coreRequest(theData)
      .then(res => res)
      .catch(e => console.error(e));
  },
  API_isFileExist (ctx, path) {
    const theData = {
      receiver: '',
      action: 'isFileExist',
      value: {
        path
      }
    };
    return coreRequest(theData)
      .then(res => res)
      .catch(e => console.error(e));
  },
  // @param {object} payload | { networkId: variableName } 
  API_getBatchPreviewSample({ getters, dispatch, rootGetters }, payload) {
    const networkList = getters.GET_coreNetworkElementList;
    let net = cloneDeep(getters.GET_coreNetwork);
    for(let elId in payload) {
      net[elId]['getPreview'] = payload[elId] !== undefined;
    }
    const theData = {
      receiver: '',
      action: 'getNetworkData',
      value: {
        Network:  net,
      }
    };

    return coreRequest(theData)
      .then(res => {
        // console.log(
        //   theData,
        //   res
        // );
        if(Object.keys(res.newNetwork).length > 0) {
          for( let ix in res.newNetwork) {
            const currentEl = networkList[ix];
            const saveSettings = {
              'elId': ix,
              'set': res.newNetwork[ix].Properties,
              'code': res.newNetwork[ix].Code,
              tabName: currentEl.layerSettingsTabName,
              visited: res.newNetwork[ix].visited,
            };
            dispatch('mod_workspace/SET_elementSettings', deepCopy(saveSettings), {root: true});
          }
        }
        if(res.outputDims) {
          dispatch('mod_workspace/SET_elementOutputDim', res.outputDims, {root: true});
          dispatch('mod_workspace-notifications/setNotifications', {
            networkId: rootGetters['mod_workspace/GET_currentNetworkId'],
            kernelResponses: res.outputDims
          }, {root: true});
        } 
        
        if(Object.keys(res.previews).length > 0) {
          Object.keys(res.previews).map(previewKey => {
            dispatch('mod_workspace/SET_NetworkChartData', {
              layerId: previewKey,
              payload: res.previews[previewKey],
            }, {root: true});
          })
        }
      
        return res;

      })
      .catch(e => {
        console.error(e)
      });
  },
  API_getBatchPreviewSampleForElementDescendants({ getters, dispatch, rootGetters }, layerId) {
    const networkList = getters.GET_coreNetworkElementList;
    const pivotLayer = networkList[layerId];
    let descendants = getDescendants(pivotLayer, []);
    let net = cloneDeep(getters.GET_coreNetwork);
    
    function getDescendants(networkElement, dataIds){
      if(networkElement.forward_connections.length === 0) {
        return dataIds;
      }
      for(let index in networkElement.forward_connections) {
        const layerId = networkElement.forward_connections[index].dst_id;
        dataIds.push(layerId);
        getDescendants(networkList[layerId], dataIds);
      }
      return dataIds;
    }

    descendants.push(layerId); 

    for(let ix in net) {
      let el = net[ix];
      if(descendants.indexOf(ix) !== -1) {
        net[ix]['getPreview'] = true;
      } else {
        net[ix]['getPreview'] = false;
      }
    }
    
    const theData = {
      receiver: '',
      action: 'getNetworkData',
      value: {
        Network:  net,
      }
    };
    return coreRequest(theData)
      .then(res => {
        
        if(res.outputDims) {
          dispatch('mod_workspace/SET_elementOutputDim', res.outputDims, {root: true});
          dispatch('mod_workspace-notifications/setNotifications', {
            networkId: rootGetters['mod_workspace/GET_currentNetworkId'],
            kernelResponses: res.outputDims
          }, {root: true});
        } 

        if(Object.keys(res.newNetwork).length > 0) {
          for( let ix in res.newNetwork) {
            const currentEl = networkList[ix];
            const saveSettings = {
              'elId': ix,
              'set': res.newNetwork[ix].Properties,
              'code': res.newNetwork[ix].Code,
		tabName: currentEl.layerSettingsTabName,
              visited: res.newNetwork[ix].visited,		
            };
            
            dispatch('mod_workspace/SET_elementSettings', deepCopy(saveSettings), {root: true});
          }
        }

        if(Object.keys(res.previews).length > 0) {
          Object.keys(res.previews).map(previewKey => {
            dispatch('mod_workspace/SET_NetworkChartData', {
              layerId: previewKey,
              payload: res.previews[previewKey],
            }, {root: true});
          })
        }
        return res;
      })
      .catch(e => {
        console.error(e)
      });
  },
  API_getFolderContent (ctx, path) {
    // resolves ~ for windows
    // expands to the full path for POSIX
    const theData = {
      receiver: '',
      action: 'getFolderContent',
      value: path
    };

    return coreRequest(theData)
      .then(res => res)
      .catch(e => console.error(e));
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
