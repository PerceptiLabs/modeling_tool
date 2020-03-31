import mixPanel from 'mixpanel-browser'
import {isElectron} from "@/core/helpers";

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
  TRACK_createUser({}, userEmail) {
    mixPanel.people.set_once({
      "$email": userEmail,
      "$created": new Date(),
    });
  },
  TRACK_updateUser({}, userEmail) {
    mixPanel.people.set({
      "$email": userEmail,
      "$last_login": new Date(),
    });
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
    if(isElectron()) {
      mixPanel.track('Model Save', model);
    }
  },
  EVENT_modelExport({}, data) {
    if(isElectron()) {
      mixPanel.track('Model Export', data);
    }
  },
  /* Training */
  EVENT_trainingStart({}, data) {
    if(isElectron()) {
      mixPanel.track('Training Start', data);
    }
  },
  EVENT_trainingStop() {
    if(isElectron()) {
      mixPanel.track('Training Stop');
    }
  },
  EVENT_trainingLayerView({}, ) {
    if(isElectron()) {
      mixPanel.track('Training Layer View', {'Layer Name': '', 'Chart Type': ''});
    }
  },
  /* Test */
  EVENT_testOpenTab() {
    if(isElectron()) {
      mixPanel.track('Test Open Tab');
    }
  },
  EVENT_testPlay({}, data) {
    if(isElectron()) {
      mixPanel.track('Test Play', data);
    }
  },
  EVENT_testStop() {
    if(isElectron()) {
      mixPanel.track('Test Stop');
    }
  },
  EVENT_testMove({}, direction) {
    if(isElectron()) {
      mixPanel.track('Test Move', {direction});
    }
  },
  /* Layer Settings */
  EVENT_applyLayerSettings({}, data) {
    if(isElectron()) {
      mixPanel.track('Apply Layer Settings', {'Tab name': data});
    }
  },
  /* Tutorial Mode */
  EVENT_tutorialModeStart() {
    if(isElectron()) {
      mixPanel.track('Tutorial Mode Start');
    }
  },
  EVENT_tutorialModeStop({}, step) {
    if(isElectron()) {
      mixPanel.track('Tutorial Mode Stop', {step});
    }
  },
  EVENT_tutorialModeFinished() {
    if(isElectron()) {
      mixPanel.track('Tutorial Mode Finished');
    }
  },
  /* Errors */
  EVENT_coreError({}, data) {
    if(isElectron()) {
      mixPanel.track('Core Error', data);
    }
  },
  EVENT_coreWarning({}, data) {
    if(isElectron()) {
      mixPanel.track('Core Warning', data);
    }
  },
  EVENT_cloudError({}, data) {
    if(isElectron()) {
      mixPanel.track('Cloud Error', data);
    }
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
