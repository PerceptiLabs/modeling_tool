import {ipcRenderer} from 'electron'

const namespaced = true;

const state = {
  calcArray: 0,
  openNetwork: 0,
  saveNetwork: 0,
  chartResize: 0,
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
  set_chartResize(state) {
    state.chartResize++
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
  EVENT_logOut({dispatch}, ctx) {
    localStorage.removeItem('userToken');
    dispatch('globalView/SET_userToken', '', {root: true});
    dispatch('mod_workspace/RESET_network', null, {root: true});
    ctx.$router.replace({name: 'login'});
  },
  EVENT_closeApp({dispatch, rootState}) {
    if(rootState.mod_api.statusLocalCore === 'online') {
      dispatch('mod_api/API_stopTraining', null, {root: true})
        .then(()=> { return dispatch('mod_api/API_CLOSE_core', null, {root: true}) })
        .then(()=> ipcRenderer.send('appClose'));
    }
    else {
      ipcRenderer.send('appClose')
    }
  },
  EVENT_chartResize({commit}) {
    commit('set_chartResize')
  },
  EVENT_pressHotKey({commit}, hotKeyName) {
    commit('set_globalPressKey', hotKeyName)
  },
  EVENT_hotKeyDeleteElement({commit, rootGetters, dispatch}) {
    if(rootGetters['mod_workspace/GET_networkIsOpen']) {
      commit('set_globalPressKey', 'del');
      dispatch('mod_workspace/DELETE_element', null, {root: true});
    }
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
