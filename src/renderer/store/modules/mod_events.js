import {ipcRenderer} from 'electron'

const namespaced = true;

const state = {
  calcArray: 0,
  openNetwork: 0,
  saveNetwork: 0,
  saveNetworkAs: 0,
  eventResize: 0,
  runNetwork: false,
  globalPressKey: {
    del: 0,
  }
};

const mutations = {
  set_calcArray(state) {
    state.calcArray++
  },
  set_openNetwork(state) {
    state.openNetwork++
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
  set_runNetwork(state, value) {
    state.runNetwork = value
  },
  set_globalPressKey(state, path) {
    state.globalPressKey[path]++
  },
};

const actions = {
  EVENT_calcArray({commit}) {
    commit('set_calcArray')
  },
  EVENT_openNetwork({commit}) {
    commit('set_openNetwork');
  },
  EVENT_saveNetwork({commit}) {
    commit('set_saveNetwork');
  },
  EVENT_saveNetworkAs({commit}) {
    commit('set_saveNetworkAs');
  },
  EVENT_logOut({dispatch}, ctx) {
    localStorage.removeItem('userToken');
    localStorage.removeItem('userId');
    localStorage.removeItem('user');
    dispatch('globalView/SET_userToken', '', {root: true});
    dispatch('mod_workspace/RESET_network', null, {root: true});
    ctx.$router.replace({name: 'login'});
  },
  EVENT_closeApp({dispatch, rootState}) {
    if(rootState.mod_api.statusLocalCore === 'online') {
      dispatch('mod_api/API_stopTraining', null, {root: true})
        .then(()=> { return dispatch('mod_api/API_CLOSE_core', null, {root: true}) })
        .then(()=> ipcRenderer.send('app-close'));
    }
    else {
      ipcRenderer.send('app-close')
    }
  },
  EVENT_eventResize({commit}) {
    commit('set_eventResize');

  },
  EVENT_pressHotKey({commit}, hotKeyName) {
    commit('set_globalPressKey', hotKeyName)
  },
  EVENT_hotKeyDeleteElement({commit, rootGetters, dispatch}) {
    commit('set_globalPressKey', 'del');
    if(rootGetters['mod_workspace/GET_networkIsOpen']) {
      dispatch('mod_workspace/DELETE_element', null, {root: true});
    }
  },
  EVENT_hotKeyCopy({rootGetters, dispatch}) {
    if(rootGetters['mod_workspace/GET_networkIsOpen']) {
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
    if(rootGetters['mod_workspace/GET_networkIsOpen'] && buffer) {
      buffer.forEach((el) => {
        dispatch('mod_workspace/ADD_element', el, {root: true});
      });
      dispatch('mod_buffer/CLEAR_buffer', null, {root: true});
    }
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
