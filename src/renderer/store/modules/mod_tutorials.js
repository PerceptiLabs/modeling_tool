const namespaced = true;

const state = {
  showTutorial: false,
  activeStep: 0,
  firstTimeApp: localStorage.showFirstAppTutorial ? false : true
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
    state.firstTimeApp = value;
  },
  SET_firstTimeApp(state, value) {
    localStorage.showFirstAppTutorial = value;
    state.showTutorial = value;
    state.firstTimeApp = value;
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
