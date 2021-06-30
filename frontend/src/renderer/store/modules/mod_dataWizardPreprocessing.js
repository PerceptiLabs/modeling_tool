const namespaced = true;

const state = {
  openedElIndex: null, // null is not opened
};

const getters = {
  getElementPreProcessingIndex(state) {
    return state.openedElIndex;
  }
};

const mutations = {
  set_elementPreProcessing(state, value) {
    state.openedElIndex = value;
  }
};

const actions = {
  TOGGLE_elementPreProcessing({commit}, value) {
    commit('set_elementPreProcessing', value);
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
