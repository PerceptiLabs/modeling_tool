import { deepCloneNetwork, deepCopy }  from "@/core/helpers.js";

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
  GET_userTokenInfo(state) {
    const token = state.userToken;
    return token.length ? parseJwt(token) : null;
  },
  GET_userID(state, getters) {//'Guest' for the trackers
    const info = getters.GET_userTokenInfo;
    return !info ? 'Guest' : info.unique_name
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
  delete_userWorkspace (state, id) {
    state.getLocalUserList[id].workspace = null
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
