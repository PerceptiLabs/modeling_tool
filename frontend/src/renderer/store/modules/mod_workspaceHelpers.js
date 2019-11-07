import { deepCopy } from "@/core/helpers.js";

const namespaced = true;

const state = {
  networkSize: null
};

const getters = {

};

const mutations = {
  set_networkSize(state, size) {
    state.networkSize = deepCopy(size)
  }
};

const actions = {
  SET_networkSize({commit, dispatch}, size) {
    commit('set_networkSize', size);
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions,
}
