const namespaced = true

const state = {
  hideLayers: true,
  hideSidebar: true
}

const mutations = {
  SET_hideLayers (state, value) {
    state.hideLayers = value
  },
  SET_hideSidebar (state, value) {
    state.hideSidebar = value
  }
}

const actions = {
  // someAsyncTask ({ commit }) {
  //   // do something async
  //   commit('INCREMENT_MAIN_COUNTER')
  // }
}

export default {
  namespaced,
  state,
  mutations,
  actions
}
