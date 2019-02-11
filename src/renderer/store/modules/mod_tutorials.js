const namespaced = true;

const state = {
  leftToolBarActive: false,
  rightToolBarActive: false,
  runButtonsActive: false,
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
