const namespaced = true;

const state = {
  hideLayers: true,
  hideSidebar: true,
  userMode: 'advanced', //simple
  userID: '',
  userToken: '',
  platform: process.platform,
  appVersion: '',
  appPath: '',
  appIsOpen: false,
  timeIntervalDoRequest: 2500,
  requestCounter: 0,
  globalPopup: {
    showNetSettings: false,
    showNetResult: false,
    showCoreSideSettings: false,
    showInfoPopup: false,
    showErrorPopup: false,
    showWorkspaceBeforeImport: false,
  }
};
const getters = {
  GET_appPath(state) {
    return state.appPath
  },
  GET_userIsLogin(state) {
    return state.userToken ? true : false
  }
};

const mutations = {
  SET_hideLayers (state, value) {
    state.hideLayers = value
  },
  SET_hideSidebar (state, value) {
    state.hideSidebar = value
  },
  set_userToken (state, value) {
    state.userToken = value
  },
  SET_userID (state, value) {
    state.userID = value
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
    console.log('NET_trainingDone');
    commit('GP_showNetResult', true);
    dispatch('mod_workspace/SET_openTest', false, {root: true});
  },
  SET_userToken({commit, dispatch}, value) {
    commit('set_userToken', value);
    if(process.env.BUILD_TARGET !== 'web') {
     value
       ? dispatch('mod_api/API_runServer', null, {root: true})
       : dispatch('mod_api/API_CLOSE_core', null, {root: true});
    }
  },
  SET_timeIntervalDoRequest({commit, dispatch}, value) {
    commit('set_timeIntervalDoRequest', value);
  },
  GP_infoPopup({commit}, value) {
    commit('gp_infoPopup', value);
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
