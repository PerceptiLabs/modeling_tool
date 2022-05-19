const namespaced = true;

const state = {
  userProfile: null,
};

const getters = {
  GET_userIsLogin(state) {
    return !!state.userProfile
  },
  GET_userID(state) {//'Guest' for the trackers
    return state.userProfile && state.userProfile.sub;
  },
  GET_userEmail(state) {
    return state.userProfile && state.userProfile.email;
  },
  GET_userProfile(state) {
    return state.userProfile;
  },
};

const mutations = {
  set_userProfile (state, value) {
    state.userProfile = value
  },
};

const actions = {
  SET_userProfile({commit}, value) {
    commit('set_userProfile', value);
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
