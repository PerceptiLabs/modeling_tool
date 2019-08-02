const namespaced = true;

const state = {
  userToken: '',
  userProfile: null
};

const getters = {
  GET_userIsLogin(state) {
    return !!state.userToken.length
  },
  GET_userID(state) {//'Guest' for the trackers
    const token = state.userToken;
    return !(token.length) ? 'Guest' : parseJwt(token).unique_name
  },
  GET_userRole() {//User, Advanced
    const token = state.userToken;
    return !(token.length) ? 'Guest' : parseJwt(token).role
  },
  GET_userProfile(state) {
    return state.userProfile
  },
};

const mutations = {
  set_userToken (state, value) {
    state.userToken = value;
  },
  set_userProfile (state, value) {
    state.userProfile = value
  },
};

const actions = {
  SET_userToken({commit, dispatch}, value) {
    commit('set_userToken', value);
    if(process.env.BUILD_TARGET !== 'web') {
      value
        ? dispatch('mod_api/API_runServer', null, {root: true})
        : dispatch('mod_api/API_CLOSE_core', null, {root: true});
    }
  },
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

function parseJwt(token) {
  var base64Url = token.split('.')[1];
  var base64 = base64Url.replace('-', '+').replace('_', '/');
  return JSON.parse(window.atob(base64));
}