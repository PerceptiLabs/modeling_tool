const namespaced = true;

const state = {
  hideLayers: true,
  hideSidebar: true,
  appMode: 'edit',
  userMode: 'advanced', //simple
  showStatistics: true,
  globalPopup: {
    showNetSettings: false,
    showNetResult: false,
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
  SET_showStatistics (state, value) {
    state.showStatistics = value
  },
  SET_appMode (state, value) {
    state.appMode = value;
    if(value === 'training') {
      state.showStatistics = true
    }
    if(value === 'training-done') {
      state.globalPopup.showNetResult = true
    }
  },
  SET_showGlobalSet (state, value) {
    state.globalPopup.showNetSettings = value
  },
  SET_showCoreSideSettings (state, value) {
    state.globalPopup.showCoreSideSettings = value
  },
  HIDE_allGlobalPopups (state) {
    for (var popup in state.globalPopup) {
      state.globalPopup[popup] = false
    }
  }
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
