import { deepCopy } from "@/core/helpers.js";

const namespaced = true;

const state = {
  elementNetworkField: null,
  elementNetworkWindow: null
};

const getters = {

};

const mutations = {
  set_elementNetworkField(state, el) {
    state.elementNetworkField = el
  },
  set_elementNetworkWindow(state, el) {
    state.elementNetworkWindow = el
  }
};

const actions = {
  SET_elementNetworkField({commit, dispatch}, el) {
    commit('set_elementNetworkField', el);
  },
  SET_elementNetworkWindow({commit, dispatch}, el) {
    commit('set_elementNetwork', el);
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions,
}
