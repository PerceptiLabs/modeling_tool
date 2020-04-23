

const namespaced = true;

const state = {
  buffer: null,
  clipBoardNetworkList: {}
};

const mutations = {
  set_buffer(state, value) {
    state.buffer = value
  },
  set_clipBoardNetworkList(state, value) {
    state.clipBoardNetworkList = Object.assign({}, value);
  }
};

const actions = {
  SET_buffer({commit}, value) {
    commit('set_buffer', value)
  },
  CLEAR_buffer({commit}) {
    commit('set_buffer', null)
  },
  SET_clipBoardNetworkList({commit}, value) {
    commit('set_clipBoardNetworkList', value)
  },
  CLEAR_clipBoardNetworkList({commit}, value) {
    commit('set_clipBoardNetworkList', {})
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
