

const namespaced = true;

const state = {
  buffer: null
};

const mutations = {
  set_buffer(state, value) {
    state.buffer = value
  },
};

const actions = {
  SET_buffer({commit}, value) {
    commit('set_buffer', value)
  },
  CLEAR_buffer({commit}) {
    commit('set_buffer', null)
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
