const namespaced = true;

const state = {
  isTestRunning: false,
  testData: []
};

const getters = {
  GET_testData(state) {
    return state.testData;
  },
  GET_testRunning(state) {
    return state.isTestRunning;
  }
};

const mutations = {
  setTestDataMutation(state, value) {
    state.testData = value;
  },
  setTestRunningMutation(state, value) {
    state.isTestRunning = value;
  }
};

const actions = {
  setTestData(ctx, value){
    ctx.commit('setTestDataMutation', value)
  },
  testStart({commit}) {
    commit('setTestRunningMutation', true)
  },
  testFinish({commit}) {
    commit('setTestRunningMutation', false)
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
