import { coreRequest }  from "@/core/apiWeb.js";
import { renderingKernel }  from "@/core/apiRenderingKernel.js";
import {deepCopy, parseJWT, isWeb, isEnvDataWizardEnabled, checkpointDirFromProject} from "@/core/helpers.js";
import { createNotebookJson }   from "@/core/helpers/notebook-helper.js";
import { pathSlash, sessionStorageInstanceIdKey }  from "@/core/constants.js";
import { createCoreNetwork } from "@/core/helpers";
import { getModelJson as rygg_getModelJson, doesDirExist as rygg_doesDirExist } from '@/core/apiRygg';
import cloneDeep from 'lodash.clonedeep';
import { v4 as uuidv4  } from 'uuid';


const namespaced = true;
//let pauseAction = 'Pause';

const state = {
  instanceId: null,
  statusLocalCore: 'offline', //online
  headlessState: [],
  coreVersions: null,
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
      if(el.componentName === 'LayerContainer') continue;

      /*prepare checkpoint*/
      const checkpointPath = {
        'load_checkpoint': rootGetters['mod_workspace/GET_currentNetworkModeWeightsState'],
        'path': ''
      };

      if(el.checkpoint.length >= 2) {
        checkpointPath.path = el.checkpoint[1]
        
        if (checkpointPath.path.slice(-1) !== '/') {
          checkpointPath.path += '/';
        } else if (checkpointPath.path.slice(-1) !== '\\') {
          checkpointPath.path += '\\';
        }
  
        checkpointPath.path += 'checkpoint';
      } else {
        checkpointPath.path = network.apiMeta.location + '/checkpoint'
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
    return layers;
  },
  GET_coreNetworkById: (state, getters, rootState, rootGetters) => (id) => {
    const network = rootGetters['mod_workspace/GET_networkByNetworkId'](id);
    let layers = {};
    
    for(let layer in network.networkElementList) {
      const el = network.networkElementList[layer];
      if(el.componentName === 'LayerContainer') continue;

      /*prepare checkpoint*/
      const checkpointPath = {
        'load_checkpoint': rootGetters['mod_workspace/GET_currentNetworkModeWeightsStateById'](id),
        'path': ''
      }; 

      if(el.checkpoint.length >= 2) {
        checkpointPath.path = el.checkpoint[1]
        
        if (checkpointPath.path.slice(-1) !== '/') {
          checkpointPath.path += '/';
        } else if (checkpointPath.path.slice(-1) !== '\\') {
          checkpointPath.path += '\\';
        }
  
        checkpointPath.path += 'checkpoint';
      } else {
        checkpointPath.path = network.apiMeta.location + '/checkpoint'
      }

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
    return layers;

    
  },
  GET_coreNetworkWithCheckpointConfig: (state, getters, rootState, rootGetters) => (loadCheckpoint = false) =>{
    const network = rootGetters['mod_workspace/GET_currentNetwork'];
    let layers = {};
    const rootPath = network.networkRootFolder;
    for(let layer in network.networkElementList) {
      const el = network.networkElementList[layer];
      if(el.componentName === 'LayerContainer') continue;

      /*prepare checkpoint*/
      const checkpointPath = {
        'load_checkpoint': loadCheckpoint,
        'path': ''
      };

      if(el.checkpoint.length >= 2) {
        checkpointPath.path = el.checkpoint[1]
        
        if (checkpointPath.path.slice(-1) !== '/') {
          checkpointPath.path += '/';
        } else if (checkpointPath.path.slice(-1) !== '\\') {
          checkpointPath.path += '\\';
        }
  
        checkpointPath.path += 'checkpoint';
      } else {
        checkpointPath.path = network.apiMeta.location + '/checkpoint'
      }

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
    return layers;
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
  },
  API_setAppInstanceMutation(state, payload) {
    state.instanceId = payload;
  },
  SET_coreVersions(state, value) {
    state.coreVersions = value;
  }
};

const actions = {
  //---------------
  //  CORE
  //---------------
  checkCoreAvailability({commit, dispatch, state}) {
      const theData = {
        action: 'isRunning',
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
  checkCoreVersions({commit, dispatch, state}) {
    const theData = {
      action: 'version',
      value: ''
    };
    return renderingKernel.getVersion()
      .then((versions)=> {
        commit('SET_coreVersions', {
          python: versions.python.split('.').slice(0,2).join('.'),
          tensorflow: versions.tensorflow
        })
      })
      .catch(()=> {
        if(state.statusLocalCore === 'online') {
          commit('SET_statusLocalCore', 'offline');
        }
      });
  },
  API_runServer({state, dispatch, commit, rootGetters}) {
    let timer;
    let coreIsStarting = false;
    var path = rootGetters['globalView/GET_appPath'];
    let userEmail = rootGetters['mod_user/GET_userEmail'];
    startCore();

    function startCore() {
        dispatch('checkCoreAvailability');
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
      }, 5001);
    }
    function getCoreRequest() {
      const theData = {
        action: 'isRunning',
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
        action: 'isRunning',
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

  API_closeCore(context, receiver) {
    const theData = {
      receiver: receiver,
      action: 'closeCore',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> { return })
      .catch((err)=> { console.error(err) });
  },

  API_CLOSE_core() {
    const theData = {
      receiver: 'server',
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
  API_testStart({dispatch, getters, rootGetters}, payload) {
    const { modelIds, checkpoint_paths }  = payload;
    
    let models = {};

    modelIds.forEach(id => {
      const network = rootGetters['mod_workspace/GET_networkByNetworkId'](id);

      models[id] = {};
      models[id].layers = getters.GET_coreNetworkById(id);
      models[id].model_name = network.networkName;
      models[id].data_path = payload.dataPath;
      models[id].checkpoint_directory = checkpoint_paths[id];
    })
    
    const theData = {
      action: 'startTests',
      receiver: 'test_requests',
      value: {
	models: models,
        tests: payload.testTypes,
        userEmail: rootGetters['mod_user/GET_userEmail'],	
        datasetSettings: modelIds.reduce((acc, id) => {
          const network = rootGetters['mod_workspace/GET_networkByNetworkId'](id);
          return { ...acc, [id]: network.networkMeta.datasetSettings };
        }, {})
      }
    }
    dispatch('mod_test/testStart', payload, {root: true});

    return renderingKernel.startSession(theData).catch((err) => {
      console.error(err);
    })
  },
  API_testStop({dispatch}) {
    const theData = {
      receiver: 'test_requests',
      action: 'StopTests'
    }
    dispatch('mod_test/setTestMessage', ['Stopping Tests...'], {root: true});
    return coreRequest(theData).then(() => {
      dispatch('mod_test/testFinish', null, {root: true});
    }).catch((err) => {
      console.error(err);
    })
  },
  API_closeTest({dispatch}) {
    const theData = {
      receiver: 'test_requests',
      action: 'CloseTests'
    }
    dispatch('mod_test/setTestMessage', ['Stopping Tests...'], {root: true});
    return coreRequest(theData).then(() => {
      dispatch('mod_test/testFinish', null, {root: true});
    }).catch((err) => {
      console.error(err);
    })
  },
  API_getTestStatus({dispatch}) {
    const theData = {
      receiver: 'test_requests',
      action: 'getTestStatus',
    }
    return coreRequest(theData).then((data)=> {
      if (data.status === 'Completed') {
        dispatch('API_getTestResults');
      } else if (data.status === 'Error') {
        dispatch('API_closeTest');
        dispatch('globalView/GP_errorPopup', data.update_line_1, {root: true});
      } else {
        dispatch('mod_test/setTestMessage', [data.update_line_1, data.update_line_2], {root: true})
      }
    })
    .catch((err)=> {
      console.error(err);
    });
  },
  API_getTestResults({dispatch}) {
    const theData = {
      receiver: 'test_requests',
      action: 'getTestResults',
    }
    return coreRequest(theData).then((data)=> {
      dispatch('API_closeTest');
      dispatch('mod_test/setTestData', data, {root: true});
      dispatch('mod_test/setTestMessage', null, {root: true});
    })
    .catch((err)=> {
      console.error(err);
    });
  },
  
  API_startTraining({dispatch, getters, rootGetters}, { loadCheckpoint = false } = {}) {
    const network = rootGetters['mod_workspace/GET_currentNetwork'];
    const datasetSettings = rootGetters['mod_workspace/GET_currentNetworkDatasetSettings'];
    const userEmail = rootGetters['mod_user/GET_userEmail'];
    const trainSettings = rootGetters['mod_workspace/GET_modelTrainingSetting'];
    const checkpointDirectory = rootGetters['mod_workspace/GET_currentNetworkCheckpointDirectory'];
    const settingCollection = {}
    if(isEnvDataWizardEnabled()) {
      settingCollection['trainSettings'] = trainSettings
    }
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "Start",
      value: {
        modelId: rootGetters['mod_workspace/GET_currentNetworkId'],
        userEmail: userEmail,
        Layers: getters.GET_coreNetworkWithCheckpointConfig(loadCheckpoint),
        'checkpointDirectory': checkpointDirectory,
        'loadCheckpoint': loadCheckpoint,
        'datasetSettings': datasetSettings,
        ...settingCollection
      }
    };
    // console.log('API_startTraining', theData);
    renderingKernel.startSession(theData)
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'Pause',
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
  API_unpauseTraining({dispatch, rootGetters}) {
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'Unpause',
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
  API_stopTraining({dispatch, rootGetters}, receiver = null) {

    const theData = {
      receiver: receiver || rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'Stop',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {
        dispatch('mod_workspace/SET_statusNetworkCoreStatus', 'Stop', {root: true});
        dispatch('mod_workspace/EVENT_startDoRequest', false, {root: true});
        dispatch('API_getStatus');
        dispatch('mod_tracker/EVENT_trainingCompleted', 'User stopped', {root: true});
      })
      .catch((err)=> {
        console.error(err);
      });
  },

  API_skipValidTraining({rootGetters}) {
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'startTest',
      value: ''
    };
    return coreRequest(theData)
      .then((data)=> { dispatch('mod_tracker/EVENT_testOpenTab', null, {root: true}) })
      .catch((err)=> { console.error(err) });
  },
  API_startTestWithCheckpointJson({rootGetters, dispatch}) {

    const currentNetwork = rootGetters['mod_workspace/GET_currentNetwork'];

    // Can actually remove this since it's not used in the createCoreNetwork call below
    const currentNetworkUsingWeights = rootGetters['mod_workspace/GET_currentNetworkModeWeightsState'];

    return rygg_getModelJson(currentNetwork.apiMeta.location + '/checkpoint/checkpoint_model.json')
      .then(resultCheckpointJson => {
        const coreResultCheckpointJson = createCoreNetwork(resultCheckpointJson, currentNetworkUsingWeights);
        if (!coreResultCheckpointJson) { return; }

        const startTestData = {
          receiver: rootGetters['mod_workspace/GET_currentNetworkId'] + 't',
          action: 'startTest',
          value: coreResultCheckpointJson
        };

        // console.log('API_startTestWithCheckpointJson startTest req', startTestData);
        return coreRequest(startTestData)
        
      })
      .then((startTestResult)=> { 
        // console.log('API_startTestWithCheckpointJson startTest res', startTestResult);
        dispatch('mod_tracker/EVENT_testOpenTab', null, {root: true});

        return Promise.resolve(startTestResult);
      })
    
      .catch((err)=> { console.error(err) });
  },
  
  API_postTestPlay({rootGetters, dispatch}) {
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
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

  API_postTestMove({rootGetters, rootState, dispatch, commit}, request) {
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworIdForKernelRequests'],
      action: request, //nextStep, previousStep
      value: ''
    };

    // console.log('API_postTestMove req', theData);
    dispatch('API_updateResults')
      .then(res => {
        // console.log('API_postTestMove res', res);
        return coreRequest(theData);
      })
      .then(nextStepRes => {
        // console.log('nextStepRes', theData, nextStepRes);
        if (!nextStepRes) { 
          console.log('Session is closed in kernel');
          commit('mod_events/set_componentEvent_test_sessionIsClosed', null, { root: true });
          // this means the session is closed in the kernel
          return dispatch('API_startTestWithCheckpointJson');
        }

        dispatch('mod_workspace/EVENT_onceDoRequest', null, {root: true});
        dispatch('mod_tracker/EVENT_testMove', theData.action, {root: true});
      })
      .catch((err)=> {
        console.error(err);
      });
  },

  API_checkNetworkRunning({rootGetters}, receiver) {
    const theData = {
      receiver: receiver,
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
      receiver: receiver || rootGetters['mod_workspace/GET_currentNetworkId'],
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
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

  //---------------
  //  ELEMENT SETTINGS
  //---------------
  API_getInputDim({dispatch, getters, rootGetters}) {
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "getNetworkInputDim",
      value: getters.GET_coreNetwork
    };

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
    //   receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
    //   action: "getNetworkOutputDim",
    //   value: getters.GET_coreNetwork
    // };
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
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
    const datasetSettings = rootGetters['mod_datasetSettings/getCurrentDatasetSettings'](); 
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getPreviewVariableList',
      value: {
        Id: layerId,
        Network: getters.GET_coreNetwork,
        datasetSettings: datasetSettings
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

     // console.log('getCode - layerId', layerId);
     return renderingKernel.getCode(net, layerId)
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
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
    const datasetSettings = rootGetters['mod_workspace/GET_currentNetworkDatasetSettings']; 
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getPartitionSummary',
      value: {
        Id: layerId,
        Network: net,
        datasetSettings: datasetSettings
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
    const datasetSettings = rootGetters['mod_workspace/GET_currentNetworkDatasetSettings'];
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'getDataMeta',
      value: {
        Id: layerId,
        Network: net,
        datasetSettings: datasetSettings
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
  API_parse({dispatch, getters, rootState, rootGetters}, path) {
    const theData = {
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: "Parse",
      value: path
    };
    return coreRequest(theData)
      .then((data)=> {
        let networkId;

        dispatch('mod_project/createProjectModel', {
          name: data.network.networkName,
          project: rootState.mod_project.currentProject,
          location: `${rootGetters['mod_project/GET_projectPath']}/${data.network.networkName}`,
        }, {root: true})
        .then(apiMeta => {
          networkId = apiMeta.model_id;

          for(let key in data.network.networkElementList) {
            // data.network.networkElementList[key].backward_connections=[]
            // data.network.networkElementList[key].forward_connections=[]
            data.network.networkElementList[key].inputs={"16100284150430":{"name":"input","reference_var_id":null,"reference_layer_id":null,"isDefault":true}}
            data.network.networkElementList[key].outputs={"16100286360500":{"name":"output","reference_var":"output"}}
          }


          data.network.networkMeta={
            chartsRequest: {timerID: null, waitGlobalEvent: false, doRequest: 0, showCharts: 0},
            coreStatus: {Status: "Waiting"},
            netMode: "edit",
            openStatistics: null,
            openTest: null,
            zoom: 1
          }
          return dispatch('mod_workspace/ADD_network', {network: data.network, apiMeta}, {root: true});
        })
        .then(_ => {
          dispatch('mod_workspace/SET_currentModelIndexByNetworkId', networkId, {root: true});
        });

      })
      .catch((err)=> {
        console.error('Parse answer', err);
      });
  },

  async API_exportData({rootGetters, getters, dispatch}, settings) {
    const userEmail = rootGetters['mod_user/GET_userEmail'];      
    const modelId = rootGetters['mod_workspace/GET_currentNetworkId'];
    const datasetSettings = rootGetters['mod_workspace/GET_currentNetworkDatasetSettings'];      

    const isTraining = ['Training', 'Validation', 'Paused'].includes(rootGetters['mod_workspace/GET_networkCoreStatus']);

    async function exportClosure() {
      if (isTraining) {
        const theData = {
	  receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
          action: 'Export',
          value: settings
        };
        return coreRequest(theData);
      } else {
          const network = getters.GET_coreNetwork;
          const checkpointDirectory = rootGetters['mod_workspace/GET_currentNetworkCheckpointDirectory'];       
          return renderingKernel.exportModel(settings, datasetSettings, userEmail, modelId, network, checkpointDirectory)
      }
    };

    const trackerData = {
      result: '',
      network: getters.GET_coreNetwork,
      settings
    };

    exportClosure()
      .then((data) => {
        dispatch('globalView/GP_infoPopup', data, {root: true});
        trackerData.result = 'success';  
      })
      .catch((err) => {
        console.error(err);
        dispatch('globalView/GP_errorPopup', err, {root: true});
        trackerData.result = 'error';
      })	  
      .finally(() => {
        dispatch('mod_tracker/EVENT_modelExport', trackerData, {root: true});
      });
  },
  //---------------
  //  OTHER
  //---------------
  API_getStatus({rootGetters, rootState, dispatch, commit}, payload) {
    const networkId = payload && payload.networkIndex !== undefined 
                        ? rootState.mod_workspace.workspaceContent[payload.networkIndex].networkID
                        : rootGetters['mod_workspace/GET_currentNetworIdForKernelRequests'];
    const theData = {
      receiver: networkId,
      action: rootGetters['mod_workspace/GET_testIsOpen'] ? 'getTestStatus' :'getStatus',
      value: ''
    };

    console.log('API_getStatus req', theData);

    coreRequest(theData)
      .then((data)=> {
        console.log('API_getStatus res', data);
        dispatch('mod_workspace/SET_statusNetworkCoreDynamically', {modelId: networkId, ...data}, {root: true})

        if (data.Status === 'Finished') {
          dispatch('mod_workspace/EVENT_stopRequest', { networkId }, {root: true});
        }
      })
      .catch((err)=> {
        if(!err.toString().match(/Error: connect ECONNREFUSED/)) {
          console.error(err);
        }
        commit('SET_statusLocalCore', 'offline')
      });
  },
  API_getModelStatus({rootGetters, dispatch, commit}, modelId) {
    const theData = {
      receiver: modelId,
      // action: rootGetters['mod_workspace/GET_testIsOpen'] ? 'getTestStatus' :'getStatus',
      // @todo ask about this twho types getTestStatus && getStatus, difference between them.
      action: 'getStatus',
      value: ''
    };
    coreRequest(theData)
      .then((data)=> {
        dispatch('mod_workspace/SET_statusNetworkCoreDynamically', {
          ...data,
          modelId: modelId,
        }, {root: true})

        if (data.Status === 'Finished') {
          dispatch('mod_workspace/EVENT_stopRequest', { networkId: modelId }, {root: true});
        }
      })
      .catch((err)=> {
        if(!err.toString().match(/Error: connect ECONNREFUSED/)) {
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
      receiver: rootGetters['mod_workspace/GET_currentNetworkId'],
      action: 'headless',
      value: value
    };
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error(err);
      });
  },

  API_updateResults({rootGetters, rootState}, payload) {
    const theData = {
      receiver: payload && payload.networkIndex !== undefined 
                  ? rootState.mod_workspace.workspaceContent[payload.networkIndex].networkID
                  : rootGetters['mod_workspace/GET_currentNetworIdForKernelRequests'],
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
      receiver: '',
      action: 'setUser',
      value: userObject.email
    };
    return coreRequest(theData)
      .then((data)=> data)
      .catch((err)=> {
        console.error(err);
      });
  },
  // @param {object} payload | { networkId: variableName } 
  API_getBatchPreviewSample({ getters, dispatch, rootGetters }, payload) {
    if (!payload) { payload = {}; }

    const networkList = getters.GET_coreNetworkElementList;
    const networkId = rootGetters['mod_workspace/GET_currentNetworkId'];
    const userEmail = rootGetters['mod_user/GET_userEmail'];
    let net = cloneDeep(getters.GET_coreNetwork);
    for(let elId in payload) {
      net[elId]['getPreview'] = payload[elId] !== undefined;
    }
    const datasetSettings = rootGetters['mod_workspace/GET_currentNetworkDatasetSettings'];

    // console.log(
    //   'API_getBatchPreviewSample req',
    //   theData
    // );
    
    dispatch('mod_workspace/setChartComponentLoadingState', { descendants: Object.keys(payload), value: true, networkId } , { root: true });

    return renderingKernel.getNetworkData(net, datasetSettings, userEmail)      
      .then(res => {
        // console.group('getNetworkData');
        // console.log(
        //   'API_getBatchPreviewSample res',
        //   theData,
        //   res
        // );
        // console.log('previews', res.previews);
        // console.groupEnd();
        if(res.newNetwork && Object.keys(res.newNetwork).length > 0) {
          for( let ix in res.newNetwork) {
            const currentEl = networkList[ix];
            const saveSettings = {
              'elId': ix,
              'set': res.newNetwork[ix].Properties,
              'code': { Output: res.newNetwork[ix].Code },
              tabName: currentEl.layerSettingsTabName,
              visited: res.newNetwork[ix].visited,
            };
            dispatch('mod_workspace/SET_elementSettings', {settings: deepCopy(saveSettings)}, {root: true});
          }
        }
        if(res.outputDims) {
          dispatch('mod_workspace/SET_elementOutputDim', res.outputDims, {root: true});
          dispatch('mod_workspace-notifications/setNotifications', {
            networkId: rootGetters['mod_workspace/GET_currentNetworkId'],
            kernelResponses: res.outputDims
          }, {root: true});
        } 
        
        if(res.previews && Object.keys(res.previews).length > 0) {
          Object.keys(res.previews).map(previewKey => {
            dispatch('mod_workspace/SET_NetworkChartData', {
              layerId: previewKey,
              payload: res.previews[previewKey],
            }, {root: true});
          })
        }

        if (res.trainedLayers) {
          dispatch('mod_workspace/SET_layerTrainedStatus', {
            networkId,
            trainedLayers: res.trainedLayers,
          }, {root: true});          
        }
      
        return res;

      })
      .catch(e => {
        console.error(e)
        return e;
      }).finally(() => {
        dispatch('mod_workspace/setChartComponentLoadingState', { descendants: Object.keys(payload), value: false, networkId } , { root: true });
        dispatch('mod_events/EVENT_calcArray', null, {root: true});
        dispatch('mod_workspace/SET_networkSnapshot', {}, { root: true });
      });
  },
  API_getBatchPreviewSampleForElementDescendants({ getters, dispatch, rootGetters }, layerId) {
    const networkList = getters.GET_coreNetworkElementList;
    const pivotLayer = networkList[layerId];
    let descendants = getDescendants(pivotLayer, []);
    const userEmail = rootGetters['mod_user/GET_userEmail'];
    const networkId = rootGetters['mod_workspace/GET_currentNetworkId'];
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

    dispatch('mod_workspace/setChartComponentLoadingState', { descendants, value: true, networkId } , { root: true });

    for(let ix in net) {
      let el = net[ix];
      if(descendants.indexOf(ix) !== -1) {
        net[ix]['getPreview'] = true;
      } else {
        net[ix]['getPreview'] = false;
      }
    }
    const datasetSettings = rootGetters['mod_workspace/GET_currentNetworkDatasetSettings'];      
    
    return renderingKernel.getNetworkData(net, datasetSettings, userEmail)
      .then(res => {
        // console.group('API_getBatchPreviewSampleForElementDescendants');
        // console.log(
        //   'API_getBatchPreviewSampleForElementDescendants res',
        //   theData,
        //   res
        // );
        // console.log('previews', res.previews);
        // console.groupEnd();

        if(res.outputDims) {
          dispatch('mod_workspace/SET_elementOutputDim', res.outputDims, {root: true});
          dispatch('mod_workspace-notifications/setNotifications', {
            networkId: rootGetters['mod_workspace/GET_currentNetworkId'],
            kernelResponses: res.outputDims
          }, {root: true});
        } 

        if(res.newNetwork && Object.keys(res.newNetwork).length > 0) {
          for( let ix in res.newNetwork) {
            const currentEl = networkList[ix];
            const saveSettings = {
              'elId': ix,
              'set': res.newNetwork[ix].Properties,
              'code': { Output: res.newNetwork[ix].Code },
              tabName: currentEl.layerSettingsTabName,
              visited: res.newNetwork[ix].visited,
            };
            dispatch('mod_workspace/SET_elementSettings', {settings: deepCopy(saveSettings)}, {root: true});
          }
        }

        if(res.previews && Object.keys(res.previews).length > 0) {
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
      }).finally(() => {
        dispatch('mod_workspace/setChartComponentLoadingState', { descendants, value: false, networkId } , { root: true });
      });
  },
  async API_scanCheckpoint (ctx, { networkId, path }) {
    const isDirExist = await rygg_doesDirExist(path);
    if(!isDirExist) {
       return ({
        networkId,
        hasCheckpoint: false 
      });
    }
    return renderingKernel.hasCheckpoint(checkpointDirFromProject(path))
      .then(res => {
        return ({
          networkId,
          hasCheckpoint: res 
        });
      })
      .catch(e => console.error(e));
  },
  
  API_UploadKernelLogs (ctx, payload) {
    const theData = {
      // receiver: networkId,
      action: 'UploadKernelLogs',
      value: payload
    };
    
    return coreRequest(theData)
  },

  API_setAppInstance({commit}) {
    let instanceKey = sessionStorage.getItem(sessionStorageInstanceIdKey);
    if(instanceKey === null) {
      instanceKey = uuidv4();
      sessionStorage.setItem(sessionStorageInstanceIdKey, instanceKey);
    }
    commit('API_setAppInstanceMutation', instanceKey);
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
