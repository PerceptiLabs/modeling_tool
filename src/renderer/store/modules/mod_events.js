const namespaced = true;

const state = {
  calcArray: 0,
};

const mutations = {
  set_calcArray(state) {
    state.calcArray++
  }
};

const actions = {
  EVENT_calcArray({commit}) {
    commit('set_calcArray')
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
