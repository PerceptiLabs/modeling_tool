const namespaced = true;

const state = {
  onlineStatus: true,
  hideLayers: true,
  hideSidebar: true,
  platform: process.platform,
  appVersion: '',
  appPath: '',
  appIsOpen: false,
  appIsFullView: false,
  timeIntervalDoRequest: 2500,
  requestCounter: 0,
  globalPopup: {
    showNetSettings: false,
    showNetResult: false,
    showCoreSideSettings: false,
    showInfoPopup: false,
    showErrorPopup: false,
    showWorkspaceBeforeImport: false,
    showConfirmPopup: false,
  },
  popupConfirmCancel: null,
  popupConfirmOk: null,
};
const getters = {
  GET_appPath(state) {
    return state.appPath
  },

};

const mutations = {
  set_onlineStatus (state, value) {
    state.onlineStatus = value
  },
  SET_hideLayers (state, value) {
    state.hideLayers = value
  },
  SET_hideSidebar (state, value) {
    state.hideSidebar = value
  },
  SET_appVersion (state, value) {
    state.appVersion = value
  },
  SET_appIsOpen (state, value) {
    state.appIsOpen = value
  },
  SET_appPath (state, value) {
    state.appPath = value
  },
  SET_appIsFullView(state, value) {
    state.appIsFullView = value
  },
  set_timeIntervalDoRequest (state, value) {
    state.timeIntervalDoRequest = value
  },
  GP_showNetResult (state, value) {
    state.globalPopup.showNetResult = value
  },
  GP_showNetGlobalSet (state, value) {
    state.globalPopup.showNetSettings = value
  },
  GP_showCoreSideSettings (state, value) {
    state.globalPopup.showCoreSideSettings = value
  },
  GP_showWorkspaceBeforeImport (state, value) {
    state.globalPopup.showWorkspaceBeforeImport = value
  },
  gp_infoPopup(state, value) {
    state.globalPopup.showInfoPopup = value
  },
  gp_confirmPopup(state, value) {
    state.globalPopup.showConfirmPopup = value.text;
    state.popupConfirmCancel = value.cancel;
    state.popupConfirmOk = value.ok;
  },
  gp_errorPopup(state, value) {
    state.globalPopup.showErrorPopup = value
  },
  HIDE_allGlobalPopups (state) {
    for (var popup in state.globalPopup) {
      state.globalPopup[popup] = false
    }
  },
  set_requestCounter(state, value) {
    value
      ? state.requestCounter++
      : state.requestCounter--
  },
  clear_requestCounter(state) {
    state.requestCounter = 0
  },
};

const actions = {
  NET_trainingDone({commit, dispatch}) {
    commit('GP_showNetResult', true);
    dispatch('mod_workspace/SET_openTest', false, {root: true});
  },
  SET_onlineStatus({commit}, value) {
    commit('set_onlineStatus', value);
  },
  SET_timeIntervalDoRequest({commit, dispatch}, value) {
    commit('set_timeIntervalDoRequest', value);
  },
  GP_infoPopup({commit}, value) {
    commit('gp_infoPopup', value);
  },
  GP_confirmPopup({commit}, value) {
    commit('gp_confirmPopup', value);
  },
  GP_errorPopup({commit}, value) {
    commit('gp_errorPopup', value);
  },
  ADD_requestCounter({commit}) {
    commit('set_requestCounter', true);
  },
  REM_requestCounter({commit}) {
    commit('set_requestCounter', false);
  },
  CLEAR_requestCounter({commit}) {
    commit('clear_requestCounter');
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
