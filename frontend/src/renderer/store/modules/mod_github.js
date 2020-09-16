const namespaced = true;

const state = {
  isGithubTokenSetted: false,
  githubToken: undefined,
};

const getters = {

};

const mutations = {
  setGithubTokenMutation(state, token) {
    state.isGithubTokenSetted = true;
    state.githubToken = token;
  },
};

const actions = {
  setGithubTokenAction({commit}, token) {
    commit('setGithubTokenMutation', token);
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions,
}
