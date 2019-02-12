const namespaced = true;

const state = {
  showTutorial: false,
  leftToolBarActive: false,
  rightToolBarActive: false,
  runButtonsActive: false,
  activeStep: 0,
  firstTimeApp: localStorage.showFirstAppTutorial || true
};

const mutations = {
  SET_leftToolBarActive(state, value) {
    state.leftToolBarActive = value;
  },
  SET_rightToolBarActive(state, value) {
    state.rightToolBarActive = value;
  },
  SET_runButtonsActive(state, value) {
    state.runButtonsActive = value;
  },
  SET_runButtonsActive(state, value) {
    state.runButtonsActive = value;
  },
  SET_activeStep(state, value) {
    state.activeStep = value;
  },
  SET_showTutorial(state, value) {
    state.showTutorial = value;
  },
  SET_firstTimeApp(state, value) {
    localStorage.showFirstAppTutorial = true;
    state.showTutorial = value;
  }
};

const actions = {
 
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
