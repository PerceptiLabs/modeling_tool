import router         from "@/router";
import {
  filePCRead,
  isWeb,
  isElectron,
  loadPathFolder,
  projectPathModel,
  shouldHideSidebar,
  calculateSidebarScaleCoefficient
} from "@/core/helpers";
import { pathSlash } from "@/core/constants";

let ipcRenderer = null;


if(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1) {
  const electron = require('electron');
  ipcRenderer = electron.ipcRenderer;
}


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
  isEnableCustomHotKey: true
};

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
  set_globalPressKey(state, path) {
    state.globalPressKey[path]++
  },
  set_enableCustomHotKey(state, value) {
    state.isEnableCustomHotKey = value
  },
};

const actions = {
  EVENT_calcArray({commit}) {
    commit('set_calcArray')
  },
  EVENT_loadNetwork({dispatch, rootGetters}, pathProject) {
    const pathFile = projectPathModel(pathProject);
    const localUserInfo = rootGetters['mod_user/GET_LOCAL_userInfo'];
    let localProjectsList = localUserInfo ? localUserInfo.projectsList : [];
    let pathIndex;
    if(localProjectsList.length) {
      pathIndex = localProjectsList.findIndex((proj)=> proj.pathModel === pathFile);
    }

    dispatch('mod_api/API_loadNetwork', pathFile, {root: true})
      .then((net) => {
        //validate model
        try {
          if(!(net.networkName
            && net.networkMeta
            && net.networkElementList)) {
              throw('err');
            }
        } catch(e) {
          dispatch('globalView/GP_infoPopup', 'The model is not valid', {root: true});
          return
        }

        if(pathIndex > -1 && localProjectsList) {
          net.networkID = localProjectsList[pathIndex].id;
        }
        dispatch('mod_workspace/ADD_network', net, {root: true});
      }).catch(err => {
        console.log(err);
        dispatch('globalView/GP_infoPopup', 'Fetching went wrong', {root: true});
        return
      });
  },
  EVENT_openNetwork({dispatch}) {
    const opt = {
      title:"Load Project Folder",
    };
    loadPathFolder(opt)
      .then((pathArr)=> dispatch('EVENT_loadNetwork', pathArr[0]))
      .catch((err)=> {});
  },
  EVENT_saveNetwork({commit}) {
    commit('set_saveNetwork');
  },
  EVENT_saveNetworkAs({commit}) {
    commit('set_saveNetworkAs');
  },
  EVENT_logOut({dispatch}, isSendLogout = true) {
    if(isSendLogout) dispatch('mod_apiCloud/CloudAPI_userLogout', null, {root: true});
    localStorage.removeItem('currentUser');
    dispatch('mod_user/RESET_userToken', null, {root: true});
    dispatch('mod_workspace/RESET_network', null, {root: true});
    dispatch('mod_tutorials/offTutorial', null, {root: true});
    router.replace({name: 'login'});
  },
  EVENT_appClose({dispatch, rootState, rootGetters}, event) {
    if(isWeb()) {
      dispatch('mod_tracker/EVENT_appClose', null, {root: true});
    } else if(isElectron()) {
      if(event) event.preventDefault();
      dispatch('mod_tracker/EVENT_appClose', null, {root: true});
      if(rootGetters['mod_user/GET_userIsLogin']) {
        dispatch('mod_user/SAVE_LOCAL_workspace', null, {root: true});
      }
      if(rootState.mod_api.statusLocalCore === 'online') {
        dispatch('mod_api/API_stopTraining', null, {root: true})
          .then(()=> dispatch('mod_api/API_CLOSE_core', null, {root: true}))
          .then(()=> ipcRenderer.send('app-close', rootState.mod_api.corePid));
      }
      else {
        ipcRenderer.send('app-close')
      }
    }
  },
  EVENT_appMinimize() {
    ipcRenderer.send('app-minimize')
  },
  EVENT_appMaximize() {
    if(isElectron()) {
      ipcRenderer.send('app-maximize')
    }
  },
  EVENT_eventResize({commit}) {
    if(isElectron()) {
      commit('set_eventResize');
    }
  },
  EVENT_pressHotKey({commit}, hotKeyName) {
    commit('set_globalPressKey', hotKeyName)
  },
  EVENT_hotKeyEsc({commit}) {
    commit('set_globalPressKey', 'esc');
  },
  EVENT_hotKeyCut({rootState, rootGetters, dispatch, commit}) {
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
          offsetY: el.layerMeta.position.top * 2,
          offsetX: el.layerMeta.position.left * 2
        };
        arrBuf.push(newEl)
      }
      });
      const currentNetworkElementList = rootGetters['mod_workspace/GET_currentNetworkElementList'];
      dispatch('mod_buffer/SET_clipBoardNetworkList', currentNetworkElementList, {root: true});
      dispatch('mod_buffer/SET_buffer', arrBuf, {root: true});
    }
  },
  EVENT_hotKeyPaste({rootState, rootGetters, dispatch, commit}) {
    dispatch('mod_workspace-history/SET_isEnableHistory', false, {root: true});
    let buffer = rootState.mod_buffer.buffer;
    dispatch('mod_workspace/SET_elementUnselect', null, {root: true});

    if(rootGetters['mod_workspace/GET_enableHotKeyElement'] && buffer) {
      const setChangeToWorkspaceHistory = false;
      buffer.forEach((event) => {
        dispatch('mod_workspace/ADD_element', { event,  setChangeToWorkspaceHistory }, {root: true});
      });
      const netWorkList = rootGetters['mod_workspace/GET_currentNetwork'].networkElementList;
      const clipBoardNetWorkList = rootState.mod_buffer.clipBoardNetworkList;

      for(let elementId in netWorkList) {
        const layerId = netWorkList[elementId].layerId;
        const sourceId = netWorkList[elementId].copyId;
        const isContainerElement = netWorkList[elementId].copyContainerElement;

        if (sourceId && clipBoardNetWorkList[sourceId]) {
          if(isContainerElement) {
            dispatch('mod_workspace/SET_elementMultiSelect', {id: netWorkList[elementId].layerId, setValue: true}, {root: true});
          }
          clipBoardNetWorkList[sourceId].connectionOut.forEach(id => {
            if(!netWorkList[sourceId] && netWorkList[id]) {
              commit('mod_workspace/SET_startArrowID', layerId, {root: true});
              dispatch('mod_workspace/ADD_arrow', netWorkList[id].layerId, {root: true});
            }
            for(let property in netWorkList) {
              if(Number(netWorkList[property].copyId) === Number(id)) {
                commit('mod_workspace/SET_startArrowID', layerId, {root: true});
                dispatch('mod_workspace/ADD_arrow', netWorkList[property].layerId, {root: true});
              }
            }
          })
          clipBoardNetWorkList[sourceId].connectionIn.forEach(id => {
            if(!netWorkList[sourceId] && netWorkList[id]) {
              commit('mod_workspace/SET_startArrowID', netWorkList[id].layerId, {root: true});
              dispatch('mod_workspace/ADD_arrow', layerId, {root: true});
            }
            for(let property in netWorkList) {
              if(Number(netWorkList[property].copyId) === Number(id)) {
                commit('mod_workspace/SET_startArrowID', layerId, {root: true});
                dispatch('mod_workspace/ADD_arrow', netWorkList[property].layerId, {root: true});
              }
            }
          })
        }
        commit('mod_workspace/DELETE_copyProperty', layerId, {root: true});
      }
    }
    dispatch('mod_workspace/ADD_container', null, {root: true});
    dispatch('mod_workspace-history/SET_isEnableHistory', true, {root: true});
  },
  SET_enableCustomHotKey({commit}, val) {
    commit('set_enableCustomHotKey', val)
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
