const namespaced = true;

const state = {
  isTestRunning: false,
  testStatus: null,
  testIntervalID: null,
  testData: null
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
  }
};

const actions = {
  setTestData(ctx, value) {
    ctx.commit("setTestDataMutation", value);
    ctx.dispatch("mod_webstorage/saveTestStatistic", value, { root: true });
  },
  testStart({ dispatch, commit }) {
    commit("setTestRunningMutation", true);
    dispatch("setTestData", null);
    dispatch("setTestMessage", ['Loading Data...']);

    const intervalID = setInterval(() => {
      dispatch("mod_api/API_getTestStatus", null, { root: true });
    }, 1000);
    commit("setTestIntervalIDMutation", intervalID);
  },
  testFinish({ commit, state }) {
    commit("setTestRunningMutation", false);
    if (state.testIntervalID) {
      clearInterval(state.testIntervalID);
    }
    commit("setTestIntervalIDMutation", null);
  },
  setTestMessage({ commit }, payload) {
    commit("setTestStatusMutation", payload);
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
};
