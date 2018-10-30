const namespaced = true;

const state = {
  hideLayers: true,
  hideSidebar: true,
  appMode: 'edit',
  userMode: 'advanced', //simple
  globalPopup: {
    showNetSettings: false,
    showCoreSideSettings: false
  }
};

const mutations = {
  SET_hideLayers (state, value) {
    state.hideLayers = value
  },
  SET_hideSidebar (state, value) {
    state.hideSidebar = value
  },
  SET_appMode (state, value) {
    state.appMode = value
  },
  SET_showNetGlobalSet (state, value) {
    state.showNetGlobalSet = value
  },
};

const actions = {
  closeGlobalPopup ({ commit }) {
    // do something async
    commit('INCREMENT_MAIN_COUNTER')
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
