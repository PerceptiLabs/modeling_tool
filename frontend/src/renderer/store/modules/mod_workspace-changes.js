import Vue from 'vue';
import { isLocalStorageAvailable }  from "@/core/helpers.js";

const namespaced = true;

const state = {
  networkChanges: {},
};

const getters = {
  get_hasUnsavedChanges: (state) => (networkId) => {
    if (state.networkChanges && state.networkChanges[networkId]) {
      return true;
    }
    return false;
  },
  get_networksWithChanges(state) {
    const keys = Object.keys(state.networkChanges);

    return keys.filter(k => state.networkChanges[k]);
  },
};

const mutations = {
  get_workspaceChangesInLocalStorage(state) {
    if (!isLocalStorageAvailable()) { return; }
  
    const changes = localStorage.getItem('_network.changes') || '{}';
    const parsedChanges = JSON.parse(changes);

    for ([key, value] of Object.entries(parsedChanges)) {
      Vue.set(state.networkChanges, key, value);
    }
  },
  set_workspaceChangesInLocalStorage(state) {
    if (!isLocalStorageAvailable()) { return; }
  
    const changes = JSON.parse(JSON.stringify(state.networkChanges));

    for ([key,value] of Object.entries(changes)) {
      if (value === false) {
        delete changes[key];
      }
    }

    localStorage.setItem('_network.changes', JSON.stringify(changes));
  },
  set_hasUnsavedChanges(state, {networkId, value}) {
    if (!networkId) { return; }

    Vue.set(state.networkChanges, networkId, value);
  },
  clear_networkChanges() {
    Vue.set(state, 'networkChanges', {});
  }
};

const actions = {
  updateUnsavedChanges({ commit }, {networkId, value}) {
    commit('set_hasUnsavedChanges', {networkId, value});
    commit('set_workspaceChangesInLocalStorage');
  },
  clearNetworkChanges({ commit }) {
    commit('clear_networkChanges');
    commit('set_workspaceChangesInLocalStorage');
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
