const namespaced = true;

const state = {
  hideLayers: true,
  hideSidebar: true,
  appMode: 'edit',  //'training', 'training-pause', 'training-done', 'addArrow'
  userMode: 'advanced', //simple
  statisticsIsOpen: false,
  userToken: '',
  globalPopup: {
    showNetSettings: false,
    showNetResult: false,
    showCoreSideSettings: false,
    showInfoPopup: false
  }
};

const mutations = {
  SET_hideLayers (state, value) {
    state.hideLayers = value
  },
  SET_hideSidebar (state, value) {
    state.hideSidebar = value
  },
  SET_statisticsIsOpen (state, value) {
    state.statisticsIsOpen = value
  },
  SET_appMode (state, value) {
    state.appMode = value;
  },
  SET_showNetResult (state, value) {
    state.globalPopup.showNetResult = value
  },
  SET_showGlobalSet (state, value) {
    state.globalPopup.showNetSettings = value
  },
  SET_showCoreSideSettings (state, value) {
    state.globalPopup.showCoreSideSettings = value
  },
  SET_infoPopup(state, value) {
    state.globalPopup.showInfoPopup = value
  },
  SET_userToken (state, value) {
    state.userToken = value
  },
  HIDE_allGlobalPopups (state) {
    for (var popup in state.globalPopup) {
      state.globalPopup[popup] = false
    }
  },
};

const actions = {
  NET_trainingStart({dispatch, commit}) {
    //commit('SET_appMode', 'training');
    commit('HIDE_allGlobalPopups');
    commit('SET_statisticsIsOpen', true);
    dispatch('mod_workspace/a_SET_networkStatistics', true, {root: true});
    dispatch('mod_statistics/STAT_defaultSelect', null, {root: true});
  },
  NET_trainingDone({state, commit, dispatch}) {
    commit('SET_appMode', 'training-done');
    commit('SET_showNetResult', true);
    dispatch('mod_workspace/a_SET_canTestStatistics', true, {root: true});
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
