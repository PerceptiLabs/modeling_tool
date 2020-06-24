const namespaced = true;
import { localStorageGridKey } from '@/core/constants.js';
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
    showNetResult: false,
    showCoreSideSettings: false,
    showInfoPopup: false,
    ComingSoonPopup: false,
    showErrorPopup: false,
    showWorkspaceBeforeImport: false,
    showConfirmPopup: false,
    coreNotFoundPopup: false,
    showFilePickerPopup: false,
    showLoadSettingPopup: false,
    showSaveNetworkPopup: false,
    showExportNetworkPopup: false
  },
  popupConfirmCancel: null,
  popupConfirmOk: null,
  pageTitle: '',
  isGridEnabled: false,
};
const getters = {
  GET_appPath(state) {
    return state.appPath
  },
};

const mutations = {
  setPageTitleMutation(state, value) {
    state.pageTitle = value;
  },
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
  GP_showCoreSideSettings (state, value) {
    state.globalPopup.showCoreSideSettings = value
  },
  GP_showWorkspaceBeforeImport (state, value) {
    state.globalPopup.showWorkspaceBeforeImport = value
  },
  gp_infoPopup(state, value) {
    state.globalPopup.showInfoPopup = value
  },
  gp_ComingSoonPopup(state, value) {
    state.globalPopup.ComingSoonPopup = value
  },
  coreNotFoundPopup(state, value) {
    // state.globalPopup.coreNotFoundPopup = value;
  },
  set_filePickerPopup(state, value) {
    state.globalPopup.showFilePickerPopup = value;
  },
  set_loadSettingPopup(state, value) {
    state.globalPopup.showLoadSettingPopup = value.visible;
    state.popupConfirmOk = value.ok;
  },
  set_saveNetworkPopup(state, value) {
    state.globalPopup.showSaveNetworkPopup = value;
  },
  set_exportNetworkPopup(state, value) {
    state.globalPopup.showExportNetworkPopup = value;
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
  setGridStateMutation(state, value) {
    localStorage.setItem(localStorageGridKey, value);
    state.isGridEnabled = value;
  }
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
  GP_ComingSoonPopup({commit}) {
    commit('gp_infoPopup', 'a');
    commit('gp_ComingSoonPopup', true);
  },
  ShowCoreNotFoundPopup({ commit, rootState, dispatch }) {
    // if (rootState.mod_api.statusLocalCore === 'online') { return; }

    // let isServerRequestDone = false;
    // dispatch('mod_api/checkCoreAvailability', null, { root: true })
    //   .then(() =>{
    //     isServerRequestDone = true;
    //   })
    //   .catch((e) =>{
    //     isServerRequestDone = true;
    //   });

    // const delayActionDispatch = setTimeout(() => {
    //   const coreIsOffline = rootState.mod_api.statusLocalCore === 'offline';
    //   //if server responds more then a second or currently is offline show the core offline modal
    //   if(coreIsOffline || !isServerRequestDone) {
    //     commit('coreNotFoundPopup', true);
    //   }
    //   clearTimeout(delayActionDispatch)
    // }, 1000);

  },
  SET_filePickerPopup({commit}, value) {
    commit('set_filePickerPopup', value);
  },
  SET_loadSettingPopup({commit}, value) {
    commit('set_loadSettingPopup', value);
  },
  SET_saveNetworkPopup({commit}, value) {
    commit('set_saveNetworkPopup', value);
  },
  SET_exportNetworkPopup({commit}, value) {
    commit('set_exportNetworkPopup', value);
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
  },
  hideSidebarAction({commit}, value) {
    commit('SET_hideSidebar', value)
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
