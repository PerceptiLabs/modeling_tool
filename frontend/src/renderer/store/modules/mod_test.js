const namespaced = true;

const state = {
  isTestRunning: false,
  testStatus: null,
  testData: null,
  testSessionId: null
};

const getters = {
  GET_testData(state) {
    return state.testData;
  },
  GET_testRunning(state) {
    return state.isTestRunning;
  },
  GET_testStatus(state) {
    return state.testStatus;
  },
  GET_testSessionId(state) {
    return state.testSessionId;
  }  
};

const mutations = {
  setTestDataMutation(state, value) {
    state.testData = value;
  },
  setTestRunningMutation(state, value) {
    state.isTestRunning = value;
  },
  setTestStatusMutation(state, value) {
    state.testStatus = value;
  },
  setTestIntervalIDMutation(state, value) {
    state.testIntervalID = value;
  },
  setTestSessionIdMutation(state, value) {
    state.testSessionId = value;
  }
};

const actions = {
  setTestData(ctx, value) {
    ctx.commit("setTestDataMutation", value);
    ctx.dispatch("mod_webstorage/saveTestStatistic", value, { root: true });
  },
  testStart({ dispatch, commit }, payload) {
    commit("setTestRunningMutation", true);
    dispatch("setTestData", null);
    dispatch("setTestMessage", ['Loading Data...']);
    dispatch("setTestSessionId", payload);    
      
    dispatch("mod_api/API_getTestStatus", null, { root: true });
  },
  testFinish({ commit, state }) {
    commit("setTestRunningMutation", false);
  },
  setTestMessage({ commit }, payload) {
    commit("setTestStatusMutation", payload);
  },
  setTestSessionId({ commit }, payload) {
    commit("setTestSessionIdMutation", payload);
  }  
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
};
