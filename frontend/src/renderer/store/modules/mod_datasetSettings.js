const namespaced = true;

const state = {
  startupFolder: null,
};

const mutations = {
  SET_startupFolder(state, value) {
    state.startupFolder = value;
  }
};

const actions = {
  setStartupFolder({commit}, path) {
    commit('SET_startupFolder', path);
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
};
