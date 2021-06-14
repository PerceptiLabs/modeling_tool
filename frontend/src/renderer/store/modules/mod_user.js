import { deepCloneNetwork, deepCopy, isLocalStorageAvailable }  from "@/core/helpers.js";

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
  GET_userToken(state) {
    return state.userToken;
  },
  GET_isUserFirstLogin(state, getters) {
    //['first login'] is defined by the mapper in KeyCloak
    if (!getters.GET_userTokenInfo) { return false; }
    else if (typeof getters.GET_userTokenInfo['first login'] === 'undefined') { return true; }

    return getters.GET_userTokenInfo['first login'];
  },
  GET_userTokenInfo(state) {
    const token = state.userToken;
    return token.length ? parseJwt(token) : null;
  },
  GET_userID(state, getters) {//'Guest' for the trackers
    const info = getters.GET_userTokenInfo;
    return !info ? 'Guest' : info.sub;
  },
  GET_userRole(state, getters) {//User, Advanced
    const info = getters.GET_userTokenInfo;
    return !info ? 'Guest' : info.role
  },
  GET_userEmail(state, getters) {
    const info = getters.GET_userTokenInfo;
    return !info ? 'Guest' : info.email
  },
  GET_userProfile(state) {
    return process.env.NO_KC ? null : state.userProfile;
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
  delete_userWorkspace (state, id) {
   if(state.getLocalUserList[id]) state.getLocalUserList[id].workspace = null
  },
};

const actions = {
  SET_userToken({commit, dispatch}, tokens) {
    commit('set_userToken', tokens);
  },
  SET_userTokenLocal({commit, dispatch}, tokens) {
    if (!isLocalStorageAvailable()) { return; }
    localStorage.setItem('currentUser', JSON.stringify(tokens));
  },
  SET_userTokenSession({}, tokens) {
    sessionStorage.setItem('currentUser', JSON.stringify(tokens));
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
      projectsList: [],
      workspace: null
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
    let usersList = localList || deepCopy(state.getLocalUserList);
    const userId = getters.GET_userID;
    usersList[userId] = userData;
    commit('set_localUserList', usersList);
    localStorage.setItem('usersList', JSON.stringify(usersList));
  },
  UPDATE_LOCAL_userInfo({dispatch, getters}, { key, data }) {
    let userInfo = deepCopy(getters.GET_LOCAL_userInfo);
    userInfo[key] = data;
    dispatch('SET_LOCAL_userInfo', {'userData': userInfo });
  },
  SAVE_LOCAL_workspace({rootState, dispatch}) {
    const cloneWS = deepCloneNetwork({
      workspaceContent: rootState.mod_workspace.workspaceContent,
      currentNetwork: rootState.mod_workspace.currentNetwork,
    });
    dispatch('UPDATE_LOCAL_userInfo', { key: 'workspace', data: cloneWS });
  },
  DELETE_userWorkspace({getters, commit}) {
    commit('delete_userWorkspace', getters.GET_userID);
  }
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
