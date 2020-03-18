//import {ipcRenderer}  from 'electron'
import router         from "@/router";
import {filePCRead, loadPathFolder, projectPathModel} from "@/core/helpers";
import { pathSlash } from "@/core/constants";
import { shouldHideSidebar, calculateSidebarScaleCoefficient } from "../../core/helpers";

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
    let localProjectsList = rootGetters['mod_user/GET_LOCAL_userInfo'].projectsList;
    let pathIndex;
    if(localProjectsList.length) {
      pathIndex = localProjectsList.findIndex((proj)=> proj.pathModel === pathFile);
    }
    return filePCRead(pathFile)
      .then((data) => {
        //validate JSON
        let net = {};
        try { net = JSON.parse(data.toString()); }
        catch(e) {
          dispatch('globalView/GP_infoPopup', 'JSON file is not valid', {root: true});
          return
        }
        //validate model
        try {
          if(!(net.networkName
            && net.networkMeta
            && net.networkElementList)
          ) {
            throw ('err')
          }
        }
        catch(e) {
          dispatch('globalView/GP_infoPopup', 'The model is not valid', {root: true});
          return;
        }
        if(pathIndex > -1 && localProjectsList) {
          net.networkID = localProjectsList[pathIndex].id;
        }
        dispatch('mod_workspace/ADD_network', net, {root: true});
      }
    );
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
    // if(event) event.preventDefault();
    // dispatch('mod_tracker/EVENT_appClose', null, {root: true});
    // if(rootGetters['mod_user/GET_userIsLogin']) {
    //   dispatch('mod_user/SAVE_LOCAL_workspace', null, {root: true});
    // }
    // if(rootState.mod_api.statusLocalCore === 'online') {
    //   dispatch('mod_api/API_stopTraining', null, {root: true})
    //     .then(()=> dispatch('mod_api/API_CLOSE_core', null, {root: true}))
    //     .then(()=> ipcRenderer.send('app-close', rootState.mod_api.corePid));
    // }
    // else {
    //   ipcRenderer.send('app-close')
    // }
  },
  // EVENT_appMinimize() {
  //   ipcRenderer.send('app-minimize')
  // },
  // EVENT_appMaximize() {
  //   ipcRenderer.send('app-maximize')
  // },
  EVENT_eventResize({commit, dispatch, rootState}) {
    //
    calculateSidebarScaleCoefficient();

    // toggle automatically right side on width change
    const sidebarState = rootState.globalView.hideSidebar;

    if(shouldHideSidebar() && sidebarState) {
      dispatch('globalView/hideSidebarAction', false, { root: true});
    } else if (!shouldHideSidebar() && !sidebarState) {
      dispatch('globalView/hideSidebarAction', true, { root: true});
    }

    commit('set_eventResize');

  },
  EVENT_pressHotKey({commit}, hotKeyName) {
    commit('set_globalPressKey', hotKeyName)
  },
  EVENT_hotKeyEsc({commit}) {
    commit('set_globalPressKey', 'esc');
  },
  EVENT_hotKeyCut({rootState, rootGetters, dispatch, commit}) {
    console.log("cut-board");
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
      const workSpace = document.querySelector('.workspace_content');
      workSpace.addEventListener('mousemove',  startCursorListener);

      function startCursorListener (event) {
        const borderline = 15;
        commit('mod_workspace/SET_CopyCursorPosition', {x: event.offsetX, y: event.offsetY}, {root: true});
        commit('mod_workspace/SET_cursorInsideWorkspace', true, {root: true});
        if(event.offsetX <= borderline ||
            event.offsetY <= borderline ||
            event.offsetY >= event.target.clientHeight - borderline ||
            event.offsetX >= event.target.clientWidth - borderline)
        {
          commit('mod_workspace/SET_cursorInsideWorkspace', false, {root: true});
        }
      }
      setTimeout(()=> {
        workSpace.removeEventListener('mousemove',  startCursorListener);
      }, 10000)
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
      const workSpace = document.querySelector('.workspace_content');
      workSpace.addEventListener('mousemove',  startCursorListener);

      function startCursorListener (event) {
        const borderline = 15;
        commit('mod_workspace/SET_CopyCursorPosition', {x: event.offsetX, y: event.offsetY}, {root: true});
        commit('mod_workspace/SET_cursorInsideWorkspace', true, {root: true});
        if(event.offsetX <= borderline ||
            event.offsetY <= borderline ||
            event.offsetY >= event.target.clientHeight - borderline ||
            event.offsetX >= event.target.clientWidth - borderline)
        {
          commit('mod_workspace/SET_cursorInsideWorkspace', false, {root: true});
        }
      }
      setTimeout(()=> {
        workSpace.removeEventListener('mousemove',  startCursorListener);
      }, 10000)
    }
  },
  EVENT_hotKeyPaste({rootState, rootGetters, dispatch, commit}) {
    let buffer = rootState.mod_buffer.buffer;
    dispatch('mod_workspace/SET_elementUnselect', null, {root: true});

    if(rootGetters['mod_workspace/GET_enableHotKeyElement'] && buffer) {
      buffer.forEach((el) => {
        dispatch('mod_workspace/ADD_element', el, {root: true});
      });
  
      const netWorkList = rootGetters['mod_workspace/GET_currentNetwork'].networkElementList;
      const clipBoardNetWorkList = rootState.mod_buffer.clipBoardNetworkList;

      for(let elementId in netWorkList) {
        const layerId = netWorkList[elementId].layerId;
        const sourceId = netWorkList[elementId].copyId;

        if (sourceId && clipBoardNetWorkList[sourceId]) {
          clipBoardNetWorkList[sourceId].connectionOut.forEach(id => {
            for(let property in netWorkList) {
              if(Number(netWorkList[property].copyId) === Number(id)) {
                commit('mod_workspace/SET_startArrowID', layerId, {root: true});
                dispatch('mod_workspace/ADD_arrow', netWorkList[property].layerId, {root: true});
              }
            }
          })
          clipBoardNetWorkList[sourceId].connectionIn.forEach(id => {
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

//      copy all connections
      // for(let key in netWorkList) {
      //   const layerId = netWorkList[key].layerId;
      //   const copyId = netWorkList[key].copyId;
      //   const isContainerElement = netWorkList[key].copyContainerElement;
      //   if(copyId && netWorkList[copyId]) {
      //     if(isContainerElement) {
      //       dispatch('mod_workspace/SET_elementMultiSelect', {id: netWorkList[key].layerId, setValue: true}, {root: true});
      //     }
      //     netWorkList[copyId].connectionOut.forEach(id => {
      //       for(let property in netWorkList) {
      //         if(Number(netWorkList[property].copyId) === Number(id)) {
      //           commit('mod_workspace/SET_startArrowID', layerId, {root: true});
      //           dispatch('mod_workspace/ADD_arrow', netWorkList[property].layerId, {root: true});
      //         }
      //       }
      //     });
      //     netWorkList[copyId].connectionIn.forEach(id => {
      //       for(let property in netWorkList) {
      //         if(Number(netWorkList[property].copyId) === Number(id)) {
      //           commit('mod_workspace/SET_startArrowID', netWorkList[property].layerId, {root: true});
      //           dispatch('mod_workspace/ADD_arrow', layerId, {root: true});
      //         }
      //       }
      //     })
      //   }
      //   commit('mod_workspace/DELETE_copyProperty', layerId, {root: true});
      // }
    }
    dispatch('mod_workspace/ADD_container', null, {root: true});
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
