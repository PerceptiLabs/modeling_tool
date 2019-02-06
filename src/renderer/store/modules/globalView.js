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
  updateStatus: 'before update', // ('before update', 'downloading', not update, 'done')
  showPopupUpdates: false,
  globalPopup: {
    showNetSettings: false,
    showNetResult: false,
    showCoreSideSettings: false,
    showInfoPopup: false
  }
};
const getters = {
  GET_appPath(state) {
    return state.appPath
  },
  GET_userIsLogin(state) {
    if(state.userToken) return true;
    else return false;

  }
};

const mutations = {
  SET_hideLayers (state, value) {
    state.hideLayers = value
  },
  SET_hideSidebar (state, value) {
    state.hideSidebar = value
  },
  SET_userToken (state, value) {
    state.userToken = value
  },
  SET_userID (state, value) {
    state.userID = value
  },
  SET_appVersion (state, value) {
    state.appVersion = value
  },
  SET_appPath (state, value) {
    state.appPath = value
  },
  SET_updateStatus (state, value) {
    state.updateStatus = value
  },
  SET_showPopupUpdates (state, value) {
    state.showPopupUpdates = value
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
  GP_infoPopup(state, value) {
    state.globalPopup.showInfoPopup = value
  },
  HIDE_allGlobalPopups (state) {
    for (var popup in state.globalPopup) {
      state.globalPopup[popup] = false
    }
  },
};

const actions = {
  NET_trainingStart({dispatch, commit}) {
    commit('HIDE_allGlobalPopups');
    //commit('SET_statisticsIsOpen', true);
    dispatch('mod_statistics/STAT_defaultSelect', null, {root: true});
  },
  NET_trainingDone({state, commit, dispatch}) {
    //commit('SET_appMode', 'training-done');
    commit('GP_showNetResult', true);
    //dispatch('mod_api/API_stopTraining', null, {root: true});
    dispatch('mod_workspace/SET_canTestStatistics', true, {root: true});
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
