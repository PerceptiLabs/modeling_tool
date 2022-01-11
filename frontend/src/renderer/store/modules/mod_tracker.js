import mixPanel from "mixpanel-browser";
import { isDevelopMode } from "@/core/constants";
import Analytics from "@/core/analytics";
import { resolveProxyUrl } from "@/core/helpers/mixpanel-helper";

const mixPanelDesktopToken = "ff98c9e22047d4a1eef9146339e038ee";
const mixPanelWebToken = isDevelopMode
  ? "8312db76002e43f8a9dc9acf9a12c1fc"
  : "1480b2244fdd4d821227a29e2637f922";

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
  },
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
  },
};

const actions = {
  TRACK_initMixPanel() {
    resolveProxyUrl().then(proxyUrl => {
      if (proxyUrl) {
        mixPanel.init(mixPanelWebToken, {
          api_host: proxyUrl,
        });
      } else {
        mixPanel.init(mixPanelWebToken);
      }

      if (isDevelopMode) {
        mixPanel.opt_in_tracking();
      } else {
        mixPanel.opt_in_tracking();
      }
    });
  },
  TRACK_initMixPanelUser({}, { email }) {
    mixPanel.identify(email);
  },
  TRACK_createUser({}, { email }) {
    mixPanel.people.set_once({
      $email: email,
      $created: new Date(),
    });
  },
  TRACK_updateUser({}, { given_name, family_name, name, email }) {
    mixPanel.people.set({
      $email: email,
      $first_name:
        given_name && !given_name.includes("perceptilabs_") ? given_name : "",
      $last_name:
        family_name && !family_name.includes("perceptilabs_")
          ? family_name
          : "",
      $name: name && !name.includes("perceptilabs_") ? name : "",
      $last_login: new Date(),
    });
  },
  TRACK_userLogin(ctx, email) {
    mixPanel.track("User login", { Email: email });
  },
  TRACK_userRegistration(ctx, email) {
    mixPanel.track("User registration", { Email: email });
  },
  TRACK_helpOption(ctx, helpOption) {
    mixPanel.track("Help option", { "Option name": helpOption });
  },
  /* APP */
  EVENT_appStart({ rootState }) {
    mixPanel.track("App Start", {
      "App Version": rootState.globalView.appVersion,
    });
  },
  /* Questionnaire */
  EVENT_questionnaireSubmitted({ getters, commit }, { answers }) {
    for (const answer of answers) {
      // wanted to wrap all of the answers in a single object but filtering in
      // MixPanel can only go 1 layer deep
      mixPanel.track("Questionnaire response", {
        Question: answer.q,
        ...answer.a,
      });
    }
  },
  /* Screen tracking */
  EVENT_screenChange({ getters, commit }, { screenName = "" }) {
    const oldScreenName = getters.getCurrentScreen;
    const oldTimestamp = getters.getCurrentScreenStartTime;
    const newTimestamp = Date.now();

    if (oldScreenName === screenName) {
      return;
    }

    commit("setCurrentScreen", screenName);

    if (oldScreenName && oldTimestamp && newTimestamp) {
      const seconds = ((newTimestamp - oldTimestamp) / 1000).toFixed(2);

      mixPanel.track("Time spent on view", {
        ScreenName: oldScreenName,
        TimeInSeconds: seconds,
      });
    }
  },
  /* Model */
  EVENT_modelCreation({}, modelType) {
    mixPanel.track("Model Creation", { Type: modelType });
  },
  EVENT_modelSave({}, model) {
    try {
      mixPanel.track("Model Save", model);
    } catch (err) {
      // Circular dependencies or large payload will trigger the error
    }
  },
  EVENT_modelExport({}, { settings }) {
    const payload = {};

    if (settings.Type == "TFModel" && settings.Compressed) {
      payload["Type"] = "tensorflow-compressed";
    } else if (settings.Type == "TFModel" && !settings.Compressed) {
      payload["Type"] = "tensorflow";
    } else if (settings.Type == "ipynb") {
      payload["Type"] = "notebook";
    } else if (settings.Type == "GitHub") {
      payload["Type"] = "GitHub";
      payload["GH Username"] = settings["GH Username"];
      payload["GH Repo URL"] = settings["GH Repo URL"];
      payload["Export Successful"] = settings["Export Successful"];
    }

    mixPanel.track("Model Export", payload);
  },
  EVENT_modelDeletion({}, modelType = "Normal") {
    mixPanel.track("Model Deletion", { Type: modelType });
  },
  /* Workspace */
  EVENT_toolbarPreviewButtonToggle({}, buttonState = true) {
    mixPanel.track("Preview button toggle", { "Button state": buttonState });
  },
  EVENT_toolbarNotebookButtonToggle({}, buttonState = false) {
    mixPanel.track("Notebook button toggle", { "Button state": buttonState });
  },
  EVENT_consoleWindowToggle({}, toggleState = false) {
    mixPanel.track("Console window toggle", { "Window state": toggleState });
  },
  /* Training */
  EVENT_trainingStart({}, data) {
    mixPanel.track("Training Start", data);
  },
  EVENT_trainingStop() {
    mixPanel.track("Training Stop");
  },
  EVENT_trainingCompleted({}, reason = "") {
    mixPanel.track("Training Completed", { "Completed reason": reason });
    Analytics.googleAnalytics.trackCustomEvent("training-completed");
  },
  /* Training/test view tab */
  EVENT_viewboxMetricSelect(
    {},
    { view = "Statistics", layerType = "", selectedMetric = "" },
  ) {
    mixPanel.track("Viewbox metric selected", {
      view,
      layerType,
      selectedMetric,
    });
  },
  /* Layer Settings */
  EVENT_applyLayerSettings({}, { componentName, tabName }) {
    mixPanel.track("Apply Layer Settings", {
      "Component name": componentName,
      "Tab name": tabName,
    });
  },
  /* Tutorial Mode */
  EVENT_tutorialModeStart() {
    mixPanel.track("Tutorial Mode Start");
  },
  EVENT_tutorialModeStop({}, step) {
    mixPanel.track("Tutorial Mode Stop", { step });
  },
  EVENT_tutorialModeFinished() {
    mixPanel.track("Tutorial Mode Finished");
  },
  EVENT_hideTips(ctx) {
    mixPanel.track("Hide tutorial tips");
  },
  EVENT_skipChecklist(ctx) {
    mixPanel.track("Skip Get Started checklist");
  },
  /* Code editor in focus */
  EVENT_codeEditorStartFocus({ getters, commit }) {
    commit("setCodeEditorFocusStartTime", Date.now());
  },
  EVENT_codeEditorStopFocus({ getters, commit }) {
    const oldInFocusStartTime = getters.getCodeEditorInFocusStartTime;
    const newInFocusStartTime = Date.now();

    commit("setCodeEditorFocusStartTime", null);

    if (oldInFocusStartTime && newInFocusStartTime) {
      const seconds = (
        (newInFocusStartTime - oldInFocusStartTime) /
        1000
      ).toFixed(2);
      mixPanel.track("Code editor in focus", { TimeInSeconds: seconds });
    }
  },
  /* Errors */
  EVENT_coreError({}, data) {
    mixPanel.track("Core Error", data);
  },
  EVENT_coreWarning({}, data) {
    mixPanel.track("Core Warning", data);
  },
  EVENT_cloudError({}, data) {
    mixPanel.track("Cloud Error", data);
  },

  // Question mark and Intercom
  TRACK_questionMark({}) {
    mixPanel.track("Click question mark");
  },
  TRACK_toggleIntercom({}, data) {
    mixPanel.track("Toggle Intercom", data);
  },
  /* data wizard */
  TRACK_datasetDownload(_, payload) {
    mixPanel.track("Dataset download", payload);
  },
  TRACK_datasetSearch(_, value) {
    mixPanel.track("Dataset search", { value });
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions,
};
