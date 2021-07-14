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
    showDeleteConfirmPopup: false,
    showFilePickerPopup: false,
    showLoadSettingPopup: false,
    showSaveNetworkPopup: false,
    showExportNetworkPopup: false,
    showExportNetworkToGitHubPopup: false,
    showImportNetworkfromGitHubOrLocalPopup: false,
    showNewModelPopup: false,
    showCreateIssuesPopup: false,
    showAppAbout: false,
    showGlobalTrainingSettingsPopup: {
      isOpen: false,
      cb: () => null,
    },
    showTestConfigurationPopup: false,
  },
  popupConfirmCancel: null,
  popupConfirmOk: null,
  pageTitle: '',
  isGridEnabled: false,
  isMiniMapNavigatorOpened: false,
  isEnterpriseApp: false,
  shouldCloseAllGlobalPopups: false,
};
const getters = {
  GET_appPath(state) {
    return state.appPath
  },
  get_isEnterpriseApp(state) {
    return state.isEnterpriseApp;
  }
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
  set_newModelPopup(state, value) {
    state.globalPopup.showNewModelPopup = value;
  },
  set_exportNetworkPopup(state, value) {
    state.globalPopup.showExportNetworkPopup = value;
  },
  set_exportNetworkToGitHubPopup(state, value) {
    state.globalPopup.showExportNetworkToGitHubPopup = value;
  },
  set_showImportNetworkfromGitHubOrLocalPopup(state, value) {
    state.globalPopup.showImportNetworkfromGitHubOrLocalPopup = value;
  },
  set_createIssuesPopup(state, value) {
    state.globalPopup.showCreateIssuesPopup = value;
  },
  gp_confirmPopup(state, value) {
    state.globalPopup.showConfirmPopup = value.text;
    state.popupConfirmCancel = value.cancel;
    state.popupConfirmOk = value.ok;
  },
  gp_deleteConfirmPopup(state, value) {
    state.globalPopup.showDeleteConfirmPopup = value.show === undefined ? true : value.show;
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
  },
  set_showAppAbout(state, value) {
    state.globalPopup.showAppAbout = value;
  },
  setMiniMapNavigationMutation(state, value) {
    localStorage.setItem('isMiniMapNavigatorOpened', value);
    state.isMiniMapNavigatorOpened = value;
  },
  showGlobalTrainingSettingsMutation(state, payload) {
    state.globalPopup.showGlobalTrainingSettingsPopup = {
      isOpen: payload.isOpen,
      cb: payload.cb,
    };
  },
  showTestConfigurationPopupMutation(state, value) {
    state.globalPopup.showTestConfigurationPopup = value;
  },
  set_isEnterpriseApp(state, isEnterpriseAppValue) {
    state.isEnterpriseApp = isEnterpriseAppValue;
  }
};

const actions = {
  NET_trainingDone({commit, dispatch}) {
    commit('GP_showNetResult', true);
    dispatch('mod_api/API_getBatchPreviewSample', null, {root: true});
    dispatch('mod_tutorials/setCurrentView', 'tutorial-general-results-view', {root: true});
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
  SET_filePickerPopup({commit}, value) {
    commit('set_filePickerPopup', value);
  },
  SET_loadSettingPopup({commit}, value) {
    commit('set_loadSettingPopup', value);
  },
  SET_saveNetworkPopup({commit}, value) {
    commit('set_saveNetworkPopup', value);
  },
  SET_newModelPopup({commit}, value) {
    commit('set_newModelPopup', value);
  },
  SET_exportNetworkPopup({commit}, value) {
    commit('set_exportNetworkPopup', value);
  },
  SET_exportNetworkToGithubPopup({commit}, value) {
    commit('set_exportNetworkToGitHubPopup', value);
  },
  SET_showImportNetworkfromGitHubOrLocalPopup({commit}, value) {
    commit('set_showImportNetworkfromGitHubOrLocalPopup', value);
  },
  SET_createIssuesPopup({commit}, value) {
    commit('set_createIssuesPopup', value);
  },  
  GP_confirmPopup({commit}, value) {
    commit('gp_confirmPopup', value);
  },
  GP_deleteConfirmPopup({commit}, value) {
    commit('gp_deleteConfirmPopup', value);
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
  },
  showGlobalTrainingSettingsAction(ctx, payload) {
    ctx.dispatch('mod_workspace/checkForRunSettingsAction', null, { root: true })
    ctx.commit('showGlobalTrainingSettingsMutation', payload);
  },
  showTestConfigurationPopupAction({commit}, value) {
    commit('showTestConfigurationPopupMutation', value);
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
