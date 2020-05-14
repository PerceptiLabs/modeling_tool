const namespaced = true;

const state = {
  isNotebookMode: false
};

const getters = {
    getNotebookMode(state) {
      return state.isNotebookMode;
    }
};

const mutations = {
  set_notebookMode(state, value) {
    if (typeof value === 'boolean') {
        state.isNotebookMode = value;
    } else {
        state.isNotebookMode = !state.isNotebookMode;
    }
  },
};

const actions = {
    SET_notebookMode({commit}, value) {
        commit('set_notebookMode', value);
    },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
