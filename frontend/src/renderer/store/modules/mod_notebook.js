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
  set_notebookMode(state, {value, dispatch}) {
    if (typeof value === 'boolean') {
        state.isNotebookMode = value;
        dispatch('globalView/hideSidebarAction', !value, {root: true});
    } else {
        state.isNotebookMode = !state.isNotebookMode;
        dispatch('globalView/hideSidebarAction', !state.isNotebookMode, {root: true});
    }
  },
};

const actions = {
    SET_notebookMode({commit, dispatch}, value) {
        commit('set_notebookMode',{ value, dispatch });
    },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
