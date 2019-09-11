const namespaced = true;

const state = {
  userToken: '',
  userTokenRefresh: '',
  userProfile: null,
  getLocalUserList: null,
};

const getters = {
  GET_userIsLogin(state) {
    return !!state.userToken.length
  },
  GET_userID(state) {//'Guest' for the trackers
    const token = state.userToken;
    return !token.length ? 'Guest' : parseJwt(token).unique_name
  },
  GET_userRole() {//User, Advanced
    const token = state.userToken;
    return !token.length ? 'Guest' : parseJwt(token).role
  },
  GET_userProfile(state) {
    return state.userProfile
  },
  GET_LOCAL_userInfo(state, getters) {
    if(state.getLocalUserList) {
      return state.getLocalUserList[getters.GET_userID]
    }
  }
};

const mutations = {
  set_userToken (state, tokens) {
    state.userToken = tokens.accessToken;
    state.userTokenRefresh = tokens.refreshToken;
  },
  set_userProfile (state, value) {
    state.userProfile = value
  },
  set_localUserList (state, value) {
    state.getLocalUserList = value
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
  RESET_userToken({commit}) {
    commit('set_userToken', {
      accessToken: '',
      refreshToken: ''
    });
  },
  SET_userProfile({commit}, value) {
    commit('set_userProfile', value);
  },
  CHECK_LOCAL_usersList({dispatch, getters, state}) {
    let usersList = state.getLocalUserList;
    const userId = getters.GET_userID;
    const defaultUserInfo = {
      showFirstAppTutorial: true,
      projectsList: []
    };
    if(usersList) {
      if(usersList[userId]) return;
    }
    else {
      usersList = {};
    }
    dispatch('SET_LOCAL_userInfo', {userData: defaultUserInfo, localList: usersList});
  },
  GET_LOCAL_userInfo({commit}) {
    commit('set_localUserList', JSON.parse(localStorage.getItem('usersList')));
  },
  SET_LOCAL_userInfo({getters, state, commit}, { userData, localList } ) {
    let usersList = localList || JSON.parse(JSON.stringify(state.getLocalUserList));
    const userId = getters.GET_userID;
    usersList[userId] = userData;
    commit('set_localUserList', usersList);
    localStorage.setItem('usersList', JSON.stringify(usersList));
  },
  UPDATE_LOCAL_userInfo({dispatch, getters}, { key, data }) {
    let userInfo = JSON.parse(JSON.stringify(getters.GET_LOCAL_userInfo));
    userInfo[key] = data;
    dispatch('SET_LOCAL_userInfo', {'userData': userInfo });
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