const namespaced = true;

const state = {
  testData: []
};

const getters = {
  GET_testData(state) {
    return state.testData;
  },
};

const mutations = {
  setTestDataMutation(state, value) {
    state.testData = value;
  },
};

const actions = {
  setTestData(ctx, value){
    ctx.commit('setTestDataMutation', value)
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
