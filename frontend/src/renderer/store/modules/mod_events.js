import router         from "@/router";
import {
  projectPathModel,
  eraseCookie,
} from "@/core/helpers";
import { getModelJsonById as rygg_getModelJsonById } from '@/core/apiRygg';
import AuthService from "@/core/auth";

const namespaced = true;

const state = {
  calcArray: 0,
  openNetwork: 0,
  saveNetwork: 0,
  saveNetworkAs: 0,
  eventResize: 0,
  globalPressKey: {
    del: 0,
    esc: 0
  },
  componentEvents: {
    test: {
      nextSampleClick: 0,
      receiveData: 0,
      sessionIsClosed: 0,
    },
    model: {
      resetSettingClick: 0,
      componentDrop: 0,
    }
  },
  isEnableCustomHotKey: true,
  isWorkspaceDragEvent: false,
  isChartFeatureSliderDragEvent: false,
  eventRunStatistic: 0,
};

const getters = {
  getIsWorkspaceDragEvent(state) {
    return state.isWorkspaceDragEvent;
  },
  getIsChartFeatureSliderDragEvent(state) {
    return state.isChartFeatureSliderDragEvent;
  }
}

const mutations = {
  set_calcArray(state) {
    state.calcArray++
  },
  set_saveNetwork(state) {
    state.saveNetwork++
  },
  set_saveNetworkAs(state) {
    state.saveNetworkAs++
  },
  set_eventResize(state) {
    state.eventResize++
  },
  set_eventComponentDrop(state) {
    state.componentEvents.model.componentDrop++;
  },
  set_globalPressKey(state, path) {
    state.globalPressKey[path]++
  },
  set_componentEvent_test_nextSampleClick(state) {
    state.componentEvents.test.nextSampleClick++;
  },
  set_componentEvent_test_receiveData(state) {
    state.componentEvents.test.receiveData++;
  },
  set_enableCustomHotKey(state, value) {
    state.isEnableCustomHotKey = value
  },
  set_componentEvent_model_resetSettingClick(state) {
    state.componentEvents.model.resetSettingClick++;
  },
  set_isWorkspaceDragEvent(state, value) {
    state.isWorkspaceDragEvent = value;
  },
  set_isChartFeatureSliderDragEvent(state, value) {
    state.isChartFeatureSliderDragEvent = value;
  },
  set_eventRunStatistic(state) {
    state.eventRunStatistic++;
  },
};
const actions = {
  EVENT_calcArray({commit}) {
    commit('set_calcArray')
  },
  EVENT_loadNetwork({dispatch, rootGetters, rootState}, pathProject) {
    const pathFile = projectPathModel(pathProject);
    let pathIndex;

    // TODO: if this dead code is resurrected, then the model id will be needed
    let model_id = 0;
    rygg_getModelJsonById(model_id)
      .then(async (model) => {

        //validate model
        let isTrained = false;
        let currentNetworkId = rootGetters['mod_workspace/GET_currentNetworkId'];
        
        const projectModels = await dispatch('mod_project/getProjectModels', null, { root: true});
        const projectModelsPaths = projectModels.map(model => model.location);

        // checking and break if model location already exist in current project
        if(projectModelsPaths.indexOf(model.apiMeta.location) !== -1 && !(currentNetworkId === model.networkID)) {
          dispatch('globalView/GP_errorPopup', `The chosen model is already in the project`, {root: true});
          return;
        }
        
        for (const idx in model.networkElementList) {
          model.networkElementList[idx].checkpoint = [];
          model.networkElementList[idx].checkpoint.push(null);
          model.networkElementList[idx].checkpoint.push(pathProject);
        }
        // Loaded model are the same with current model
        if(currentNetworkId === model.networkID) {
          dispatch('mod_workspace/ReplaceNetworkElementList', model.networkElementList, {root: true});
          dispatch('EVENT_calcArray', null); // for arrow update
        } else {
          
          if(model.hasOwnProperty('apiMeta')) {
            delete model.apiMeta;
          }
          delete model.networkID;
          
          model.networkMeta.coreStatus = { Status: 'Waiting' };
  
          try {
            if(!(model.networkName
              && model.networkMeta
              && model.networkElementList)) {
                throw('err');
              }
  
              for(let id in model.networkElementList) {
                let element = model.networkElementList[id];
                if (element.checkpoint.length > 0) {
                  isTrained = true;
                  break;
                }
              }
  
          } catch(e) {
            dispatch('globalView/GP_infoPopup', 'The model does not exist or the Kernel is not online.', {root: true});
            return
          }
  
          if(pathIndex > -1 && localProjectsList) {
            model.networkID = localProjectsList[pathIndex].id;
            model.networkRootFolder = localProjectsList[pathIndex].pathProject;
          } else {
            model.networkRootFolder = pathProject;
          }
          
          // Now only loading the normal model
          createProjectAndAddNetworkFn(model, rootState.mod_project.currentProject);
        }

        if (model.networkMeta) {
          model.networkMeta.openStatistics = null;
          model.networkMeta.openTest = null;
        }

        dispatch('mod_project/getProjects', null , {root: true});
      }).catch(err => {
        console.log(err);
        dispatch('globalView/GP_infoPopup', 'Fetching failed', {root: true});
        return;
      });

    function createProjectAndAddNetworkFn (mod, projectId) {
      let networkId;

      dispatch('mod_project/createProjectModel', {
        name: mod.networkName,
        project: projectId,
        location: pathFile.substring(0, pathFile.lastIndexOf('/')),
      }, {root: true})
      .then(apiMeta => {
        networkId = apiMeta.model_id;
        return dispatch('mod_workspace/ADD_network', {network: mod, apiMeta}, {root: true});
      })
      .then(_ => {
        dispatch('mod_workspace/SET_currentModelIndexByNetworkId', networkId, {root: true});
      });
    }
  },
  EVENT_saveNetwork({commit}) {
    commit('set_saveNetwork');
  },
  EVENT_saveNetworkAs({commit}) {
    commit('set_saveNetworkAs');
  },
  EVENT_logOut({commit, dispatch}, isSendLogout = true) {
    if(isSendLogout) {
      if(AuthService.isReachable()) { // has internet connection and keycloak instance are available
        AuthService.logout();
        eraseCookie('loggedInUser')
      } else {
        eraseCookie('loggedInUser');
        window.location.reload();
      }
    }

    commit('mod_project/removeProjectIdInLocalStorage');
    localStorage.removeItem('currentUser');
    dispatch('mod_workspace/RESET_network', null, {root: true});
    dispatch('mod_workspace-changes/clearNetworkChanges', null, {root: true});

    router.replace({name: 'projects'})
      .catch(e => {/*console.error('Error during logout', e)*/});
  },
  EVENT_eventResize({commit}) {
    commit('set_eventResize');
  },
  EVENT_pressHotKey({commit}, hotKeyName) {
    commit('set_globalPressKey', hotKeyName)
  },
  EVENT_hotKeyEsc({commit}) {
    commit('set_globalPressKey', 'esc');
  },
  EVENT_hotKeyCut({rootState, rootGetters, dispatch, commit}) {
    if(rootState['mod_workspace-code-editor'].isInFocus) {
      return 0;
    }
    commit('mod_workspace/CLEAR_CopyElementsPosition', null, {root: true});
    dispatch('mod_workspace/copyOrCutNetworkSnapshotAction', null, { root: true }); // copy the snapshot of network elements for paste functionality
    if(rootGetters['mod_workspace/GET_enableHotKeyElement']) {
      let arrSelect = rootGetters['mod_workspace/GET_currentSelectedEl'];
      let arrBuf = [];
      arrSelect.forEach((el) => {
      commit('mod_workspace/SET_CopyElementsPosition', {left: el.layerMeta.position.left, top: el.layerMeta.position.top}, {root: true});
      if(el.componentName === 'LayerContainer') {
        for(let id in el.containerLayersList) {
          const element = el.containerLayersList[id];
          let newContainerEl = {
            target: {
              dataset: {
                layer: element.layerName,
                type: element.layerType,
                component: element.componentName,
                copyId: element.layerId,
                copyContainerElement: true
              },
              clientHeight: element.layerMeta.position.top * 2,
              clientWidth: element.layerMeta.position.left * 2,
            },
            layerSettings: element.layerSettings,
            offsetY: element.layerMeta.position.top * 2,
            offsetX: element.layerMeta.position.left * 2
          };
          arrBuf.push(newContainerEl)
        }
      }
      else {
        let newEl = {
          target: {
            dataset: {
              layer: el.layerName,
              type: el.layerType,
              component: el.componentName,
              copyId: el.layerId
            },
            clientHeight: el.layerMeta.position.top * 2,
            clientWidth: el.layerMeta.position.left * 2,
          },
          layerSettings: el.layerSettings,
          layerSettingsTabName: el.layerSettingsTabName,
          layerCode: el.layerCode,
          offsetY: el.layerMeta.position.top * 2,
          offsetX: el.layerMeta.position.left * 2
        };
        arrBuf.push(newEl)
      }
      });
      const currentNetworkElementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
      dispatch('mod_buffer/SET_clipBoardNetworkList', currentNetworkElementList, {root: true});
      dispatch('mod_buffer/SET_buffer', arrBuf, {root: true});
      dispatch('mod_workspace/DELETE_element', null, {root: true});
    }    
  },
  EVENT_hotKeyCopy({rootState, rootGetters, dispatch, commit}) {
    if(rootState['mod_workspace-code-editor'].isInFocus) { return; }
    dispatch('mod_workspace/copyOrCutNetworkSnapshotAction', null, { root: true }); // copy the snapshot of network elements for paste functionality
    commit('mod_workspace/CLEAR_CopyElementsPosition', null, {root: true});
    if(rootGetters['mod_workspace/GET_enableHotKeyElement']) {
      let arrSelect = rootGetters['mod_workspace/GET_currentSelectedEl'];
      let arrBuf = [];
      arrSelect.forEach((el) => {
      commit('mod_workspace/SET_CopyElementsPosition', {left: el.layerMeta.position.left, top: el.layerMeta.position.top}, {root: true});
      if(el.componentName === 'LayerContainer') {
        for(let id in el.containerLayersList) {
          const element = el.containerLayersList[id];
          let newContainerEl = {
            target: {
              dataset: {
                layer: element.layerName,
                type: element.layerType,
                component: element.componentName,
                copyId: element.layerId,
                copyContainerElement: true
              },
              clientHeight: element.layerMeta.position.top,
              clientWidth: element.layerMeta.position.left,
            },
            layerSettings: element.layerSettings,
            offsetY: element.layerMeta.position.top,
            offsetX: element.layerMeta.position.left
          };
          arrBuf.push(newContainerEl)
        }
      }
      else {
        let newEl = {
          target: {
            dataset: {
              layer: el.layerName,
              type: el.layerType,
              component: el.componentName,
              copyId: el.layerId
            },
            clientHeight: el.layerMeta.position.top,
            clientWidth: el.layerMeta.position.left,
          },
          layerSettings: el.layerSettings,
          layerSettingsTabName: el.layerSettingsTabName,
          layerCode: el.layerCode,
          offsetY: el.layerMeta.position.top,
          offsetX: el.layerMeta.position.left,
          isSettingsLocked: el.isSettingsLocked || false,
        };
        arrBuf.push(newEl)
      }
      });
      const currentNetworkElementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
      dispatch('mod_buffer/SET_clipBoardNetworkList', currentNetworkElementList, {root: true});
      dispatch('mod_buffer/SET_buffer', arrBuf, {root: true});
    }
  },
  EVENT_hotKeyPaste({rootState, rootGetters, dispatch, commit}, triggeredByHotKey) {
    if(rootState['mod_workspace-code-editor'].isInFocus) {
      return 0;
    }
    dispatch('mod_workspace-history/SET_isEnableHistory', false, {root: true});
    let buffer = rootState.mod_buffer.buffer;
    dispatch('mod_workspace/SET_elementUnselect', null, {root: true});

    if(!rootGetters['mod_workspace/GET_enableHotKeyElement'] || 
      !buffer || 
      buffer.length === 0) { return };

    const oldElementIds = Object.keys(rootGetters['mod_workspace/GET_currentNetwork'].networkElementList);

    const addElementPromises = buffer.map(b => {
      dispatch('mod_workspace/ADD_element', { 
        event: b,  
        setChangeToWorkspaceHistory: false,
        triggeredByHotKey
      }, {root: true})
    })
    Promise.all(addElementPromises)
      .then(result => {

      const networkList = rootGetters['mod_workspace/GET_currentNetwork'].networkElementList;
      const clipBoardNetworkList = rootState.mod_buffer.clipBoardNetworkList;
      const copyOrCutNetworkSnapshot = rootGetters['mod_workspace/GET_copyOrCutNetworkSnapshot'];

      // make a mapping of the old element ids to the new so we don't have to loop through 
      const newElementIds = Object.keys(networkList).filter(nId => !oldElementIds.includes(nId));
      const oldToNewElementIdMapping = {};
      for(let elementId of newElementIds) {
        oldToNewElementIdMapping[networkList[elementId].copyId] = elementId;
      }

      for(let elementId of newElementIds) {
        const sourceId = networkList[elementId].copyId;
        const isContainerElement = networkList[elementId].copyContainerElement;
        
        if (!sourceId || !clipBoardNetworkList[sourceId]) { continue; }

        if(isContainerElement) {
          dispatch('mod_workspace/SET_elementMultiSelect', {id: networkList[elementId].layerId, setValue: true}, {root: true});
        }
        
        if (!copyOrCutNetworkSnapshot[sourceId].inputs) { continue; }

        for (const inputItem of Object.entries(copyOrCutNetworkSnapshot[sourceId].inputs)) {
          
          const oldDestName = inputItem[1].name;
          const oldSourceLayerId = inputItem[1].reference_layer_id;
          const oldSourceVarId = inputItem[1].reference_var_id;
          
          // if no connection
          if (!oldSourceLayerId || !oldSourceVarId) { continue; }

          // true when the connections are not part of what's being copied
          if (!networkList[oldToNewElementIdMapping[oldSourceLayerId]]) { continue; }

          // TODO: can perhaps match oldSourceLayerId to the buffer...
          // continue if not included

          // getting information on where the arrow starts
          const newElementInputs = networkList[oldToNewElementIdMapping[sourceId]].inputs;
          let newDestVarId = '';
          for(const i of Object.entries(newElementInputs)) {
            if (i[1].name === oldDestName) {
              newDestVarId = i[0];
            }
          }

          // getting information on where the arrow ends
          const oldElementOutputs = copyOrCutNetworkSnapshot[oldSourceLayerId].outputs;            
          let oldSourceVarName = '';
          for(const i of Object.entries(oldElementOutputs)) {
            if (i[0] === oldSourceVarId) {
              oldSourceVarName = i[1].name;
            }
          }

          const newElementOutputs = networkList[oldToNewElementIdMapping[oldSourceLayerId]].outputs;  
          let newSourceVarId = '';
          for(const i of Object.entries(newElementOutputs)) {
            if (i[1].name === oldSourceVarName) {
              newSourceVarId = i[0];
            }
          }

          commit('mod_workspace/SET_startArrowID', {
            outputDotId: newSourceVarId,
            outputLayerId: oldToNewElementIdMapping[oldSourceLayerId],
            layerId: oldToNewElementIdMapping[oldSourceLayerId],
          }, {root: true});

          dispatch('mod_workspace/ADD_arrow', {
            inputDotId: newDestVarId,
            inputLayerId: elementId,
            layerId: elementId,
          }, {root: true})
          // .then(() => {
          //   this.$store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', this.dataEl.layerId);
          // });
        }
      }

      // removes the copyId
      for(let elementId of newElementIds) {
        commit('mod_workspace/DELETE_copyProperty', elementId, {root: true});
      }
    })
    .then(() => {
      dispatch('mod_workspace-history/SET_isEnableHistory', true, {root: true});
      dispatch('mod_workspace-history/PUSH_newSnapshot', null, {root: true});
    });

  },
  SET_enableCustomHotKey({commit}, val) {
    commit('set_enableCustomHotKey', val)
  },
  EVENT_componentEvent_model_resetSettingClick({commit}) {
    commit('set_componentEvent_model_resetSettingClick');
  },
  EVENT_set_eventRunStatistic({commit}) {
    commit("set_eventRunStatistic");
  }
};

export default {
  getters,
  namespaced,
  state,
  mutations,
  actions
}
