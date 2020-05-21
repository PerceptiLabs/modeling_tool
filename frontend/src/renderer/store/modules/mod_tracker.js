import mixPanel from 'mixpanel-browser'
import {isElectron} from "@/core/helpers";

const mixPanelDesktopToken = 'ff98c9e22047d4a1eef9146339e038ee';
const mixPanelWebToken = '1480b2244fdd4d821227a29e2637f922';

const namespaced = true;

const state = {

};

const getters = {

};

const mutations = {

};

const actions = {
  TRACK_initMixPanel() {
    if (isElectron()) {
      mixPanel.init(mixPanelDesktopToken);
    } else {
      mixPanel.init(mixPanelWebToken);
    }
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
  TRACK_userLogin(ctx, email) {
    mixPanel.track('User login', {'Email': email});
  },
  TRACK_userRegistration(ctx, email) {
    mixPanel.track('User registration', {'Email': email});
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
  EVENT_modelCreation({}, modelType) {
    mixPanel.track('Model Creation', {'Type': modelType});
  },
  EVENT_modelSave({}, model) {
    mixPanel.track('Model Save', model);
  },
  EVENT_modelExport({}, data) {

    const payload = {};

    if (data.settings.Type == 'TFModel' && data.settings.Compressed) {
      payload['Type'] = 'tensorflow-compressed';
    } else if (data.settings.Type == 'TFModel' && !data.settings.Compressed) {
      payload['Type'] = 'tensorflow';
    } else if (data.settings.Type == 'ipynb') {
      payload['Type'] = 'notebook';
    }

    mixPanel.track('Model Export', payload);
  },
  /* Training */
  EVENT_trainingStart({}, data) {
    mixPanel.track('Training Start', data);
  },
  EVENT_trainingStop() {
    mixPanel.track('Training Stop');
  },
  EVENT_trainingCompleted() {
    mixPanel.track('Training Completed');
  },
  EVENT_trainingLayerView({}, ) {
    if(isElectron()) {
      mixPanel.track('Training Layer View', {'Layer Name': '', 'Chart Type': ''});
    }
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
  EVENT_applyLayerSettings({}, {componentName, tabName}) {
    mixPanel.track('Apply Layer Settings', {
      'Component name': componentName, 
      'Tab name': tabName
    });
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
