import Vue from 'vue';

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
    return Object.keys(state.networkChanges);
  },
};

const mutations = {
  set_hasUnsavedChanges(state, {networkId, value}) {
    if (!networkId) { return; }

    Vue.set(state.networkChanges, networkId, value);
  },
  clear_networkChanges() {
    Vue.set(state, 'networkChanges', {});
  }
};

const actions = {};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
