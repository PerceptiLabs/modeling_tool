import mixPanel       from 'mixpanel-browser'

const mixPanelToken = 'ff98c9e22047d4a1eef9146339e038ee';
const namespaced = true;

const state = {

};

const getters = {

};

const mutations = {

};

const actions = {
  TRACK_initMixPanel() {
    mixPanel.init(mixPanelToken);
  },
  TRACK_initMixPanelUser({}, id) {
    mixPanel.identify(id);
  },
  /* APP */
  EVENT_appStart({rootState}) {
    mixPanel.track('App Start', {
      'App Version': rootState.globalView.appVersion
    });
  },
  EVENT_appClose() {
    mixPanel.track('App Close');
  },
  /* Model */
  EVENT_modelSave({}, model) {
    mixPanel.track('Model Save', model);
  },
  EVENT_modelExport({}, data) {
    mixPanel.track('Model Export', data);
  },
  /* Training */
  EVENT_trainingStart({}, data) {
    mixPanel.track('Training Start', data);
  },
  EVENT_trainingStop() {
    mixPanel.track('Training Stop');
  },
  EVENT_trainingLayerView({}, ) {
    mixPanel.track('Training Layer View', {'Layer Name': '', 'Chart Type': ''});
  },
  /* Test */
  EVENT_testOpenTab() {
    mixPanel.track('Test Open Tab');
  },
  EVENT_testPlay({}, data) {
    mixPanel.track('Test Play', data);
  },
  EVENT_testStop() {
    mixPanel.track('Test Stop');
  },
  EVENT_testMove({}, direction) {
    mixPanel.track('Test Move', {direction});
  },
  /* Layer Settings */
  EVENT_applyLayerSettings({}, data) {
    mixPanel.track('Apply Layer Settings', {'Tab name': data});
  },
  /* Tutorial Mode */
  EVENT_tutorialModeStart() {
    mixPanel.track('Tutorial Mode Start');
  },
  EVENT_tutorialModeStop({}, step) {
    mixPanel.track('Tutorial Mode Stop', {step});
  },
  EVENT_tutorialModeFinished() {
    mixPanel.track('Tutorial Mode Finished');
  },
  /* Errors */
  EVENT_coreError({}, data) {
    mixPanel.track('Core Error', data);
  },
  EVENT_coreWarning({}, data) {
    mixPanel.track('Core Warning', data);
  },
  EVENT_cloudError({}, data) {
    mixPanel.track('Cloud Error', data);
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
