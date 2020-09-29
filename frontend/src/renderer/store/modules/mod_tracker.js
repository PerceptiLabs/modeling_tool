import mixPanel from 'mixpanel-browser'
import { isElectron } from "@/core/helpers";
import { isDevelopMode } from "@/core/constants";

const mixPanelDesktopToken = 'ff98c9e22047d4a1eef9146339e038ee';
const mixPanelWebToken = isDevelopMode ? 
  '8312db76002e43f8a9dc9acf9a12c1fc' :
  '1480b2244fdd4d821227a29e2637f922';

const namespaced = true;


const state = {
  currentScreen: null,
  currentScreenStartTime: null,

  codeEditorFocusStartTime: null,
};

const getters = {
  getCurrentScreen(state) {
    return state.currentScreen;
  },
  getCurrentScreenStartTime(state) {
    return state.currentScreenStartTime;
  },
  getCodeEditorInFocusStartTime(state) {
    return state.codeEditorFocusStartTime;
  }
};

const mutations = {
  setCurrentScreen(state, value) {
    if (value) {
      state.currentScreen = value;
      state.currentScreenStartTime = Date.now();
    } else {
      state.currentScreen = null;
      state.currentScreenStartTime = null;
    }
  },
  setCodeEditorFocusStartTime(state, value) {
    state.codeEditorFocusStartTime = value;
  }
};

const actions = {
  TRACK_initMixPanel() {
    if (isDevelopMode) {
      mixPanel.init(mixPanelWebToken);
      mixPanel.opt_out_tracking();
    } else if (isElectron()) {
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
  /* Screen tracking */
  EVENT_screenChange({getters, commit}, { screenName = ''}) {

    const oldScreenName = getters.getCurrentScreen;
    const oldTimestamp = getters.getCurrentScreenStartTime;
    const newTimestamp = Date.now();

    commit('setCurrentScreen', screenName);

    if (oldScreenName && oldTimestamp && newTimestamp) {
      const seconds = ((newTimestamp - oldTimestamp) / 1000).toFixed(2);
      mixPanel.track('Time spent on view', { ScreenName: oldScreenName, TimeInSeconds: seconds } );
    }
  },
  /* Model */
  EVENT_modelCreation({}, modelType) {
    mixPanel.track('Model Creation', {'Type': modelType});
  },
  EVENT_modelSave({}, model) {
    try { 
      mixPanel.track('Model Save', model);
    } catch (err) {
      // Circular dependencies or large payload will trigger the error
    }
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
  /* Workspace */
  EVENT_toolbarPreviewButtonToggle({}, buttonState = true) {
    mixPanel.track('Preview button toggle', { 'Button state': buttonState });
  },
  EVENT_toolbarNotebookButtonToggle({}, buttonState = false) {
    mixPanel.track('Notebook button toggle', { 'Button state': buttonState });
  },
  EVENT_consoleWindowToggle({}, toggleState = false) {
    mixPanel.track('Console window toggle', { 'Window state': toggleState });
  },
  /* Training */
  EVENT_trainingStart({}, data) {
    mixPanel.track('Training Start', data);
  },
  EVENT_trainingStop() {
    mixPanel.track('Training Stop');
  },
  EVENT_trainingCompleted({}, reason = '') {
    mixPanel.track('Training Completed', { 'Completed reason': reason });
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
  /* Training/test view tab */
  EVENT_viewboxMetricSelect({}, { view = 'Statistics', layerType = '', selectedMetric = '' }) {
    mixPanel.track('Viewbox metric selected', { view, layerType, selectedMetric } );
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
  /* Code editor in focus */
  EVENT_codeEditorStartFocus({getters, commit}) {
    commit('setCodeEditorFocusStartTime', Date.now());
  },
  EVENT_codeEditorStopFocus({getters, commit}) {

    const oldInFocusStartTime = getters.getCodeEditorInFocusStartTime;
    const newInFocusStartTime = Date.now();

    commit('setCodeEditorFocusStartTime', null);
    
    if (oldInFocusStartTime && newInFocusStartTime) {
      const seconds = ((newInFocusStartTime - oldInFocusStartTime) / 1000).toFixed(2);
      mixPanel.track('Code editor in focus', { TimeInSeconds: seconds } );
    }
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
