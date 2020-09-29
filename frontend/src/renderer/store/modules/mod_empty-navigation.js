const namespaced = true;

const state = {
  emptyScreenMode: 0
};

const getters = {
    getEmptyScreenMode(state) {
      return state.emptyScreenMode;
    }
};

const mutations = {
    set_emptyScreenMode(state, value) {
        state.emptyScreenMode = value;
    }
};

const actions = {
    SET_emptyScreenMode({commit}, value) {
        commit('set_emptyScreenMode', value);
    },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
