//import {ipcRenderer}  from 'electron'
import router         from "@/router";
import {filePCRead, loadPathFolder, projectPathModel} from "@/core/helpers";
import { pathSlash } from "@/core/constants";

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
    /*if(event) event.preventDefault();
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
  },
  EVENT_appMinimize() {
    ipcRenderer.send('app-minimize')
  },
  EVENT_appMaximize() {
    ipcRenderer.send('app-maximize')
  },
  EVENT_eventResize({commit}) {
    commit('set_eventResize');

  },*/
  EVENT_pressHotKey({commit}, hotKeyName) {
    commit('set_globalPressKey', hotKeyName)
  },
  EVENT_hotKeyEsc({commit}) {
    commit('set_globalPressKey', 'esc');
  },
  EVENT_hotKeyCopy({rootGetters, dispatch}) {
    if(rootGetters['mod_workspace/GET_enableHotKeyElement']) {
      let arrSelect = rootGetters['mod_workspace/GET_currentSelectedEl'];
      let arrBuf = [];
      arrSelect.forEach((el) => {
        let newEl = {
          target: {
            dataset: {
              layer: el.layerName,
              type: el.layerType,
              component: el.componentName
            },
            clientHeight: el.layerMeta.position.top * 2,
            clientWidth: el.layerMeta.position.left * 2,
          },
          layerSettings: el.layerSettings,
          // connectionOut: el.connectionOut,
          // connectionIn: el.connectionIn,
          // connectionArrow: el.connectionArrow,
          offsetY: el.layerMeta.position.top * 2,
          offsetX: el.layerMeta.position.left * 2
        };
        arrBuf.push(newEl)
      });

      dispatch('mod_buffer/SET_buffer', arrBuf, {root: true});
    }
  },
  EVENT_hotKeyPaste({rootState, rootGetters, dispatch}) {
    let buffer = rootState.mod_buffer.buffer;
    if(rootGetters['mod_workspace/GET_enableHotKeyElement'] && buffer) {
      buffer.forEach((el) => {
        dispatch('mod_workspace/ADD_element', el, {root: true});
      });
      //dispatch('mod_buffer/CLEAR_buffer', null, {root: true});
    }
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
