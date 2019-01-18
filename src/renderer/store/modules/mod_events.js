//import requestApi  from "@/core/api.js";
import {ipcRenderer} from 'electron'

const namespaced = true;

const state = {
  calcArray: 0,
  openNetwork: 0,
  saveNetwork: 0
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

  EVENT_closeCore({dispatch}) {
    dispatch('mod_api/API_CLOSE_core', null, {root: true});
    ipcRenderer.send('appClose');
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
