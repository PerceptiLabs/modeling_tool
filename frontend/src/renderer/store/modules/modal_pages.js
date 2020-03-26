const namespaced = true;

const state = {
  isOpen: false,
  currentPage: null,
};

const getters = {

};

const mutations = {
  setActivePageMutation(state, page) {
    state.currentPage = page;
    state.isOpen = true;
  },
  closePageMutation(state) {
    state.isOpen = false;
    state.currentPage = null;
  }
};

const actions = {
  setActivePageAction({commit}, page) {
    commit('setActivePageMutation', page);
  },
  closePageAction({commit}) {
    commit('closePageMutation');
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions,
}
