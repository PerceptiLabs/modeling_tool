const namespaced = true;

const state = {
  userToken: '',
  userProfile: null,
  getLocalUserList: JSON.parse(localStorage.getItem('usersList')),
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
  GET_LOCAL_userInfo(state, getters) {
    return state.getLocalUserList[getters.GET_userID]
  }
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
  // GET_LOCAL_usersList() {
  //   console.log('GET_LOCAL_usersList');
  //   return
  // },
  CHECK_LOCAL_usersList({dispatch, getters, state}) {
    //console.log('CHECK_LOCAL_usersList', dispatch);
    let usersList = state.getLocalUserList;
    //console.log('CHECK_LOCAL_usersList', usersList);
    const userId = getters.GET_userID;
    const defaultUserInfo = {
      showFirstAppTutorial: true,
      projectsList: []
    };
    //console.log('usersList', usersList, 'userId', userId);
    if(usersList) {
      if(usersList[userId]) return;
    }
    else {
      usersList = {};
    }
    dispatch('SET_LOCAL_userInfo', {userData: defaultUserInfo, localList: usersList});
  },
  SET_LOCAL_userInfo({getters, state}, { userData, localList } ) {
    //console.log('SET_LOCAL_userInfo', userData, localList);
    let usersList = localList || state.getLocalUserList;
    //console.log('usersList', usersList);
    const userId = getters.GET_userID;
    usersList[userId] = userData;
    //console.log(usersList);
    localStorage.setItem('usersList', JSON.stringify(usersList));
  },
  UPDATE_LOCAL_userInfo({dispatch, getters}, { key, data }) {
    let userInfo = getters.GET_LOCAL_userInfo;
    //console.log('UPDATE_LOCAL_userInfo', userInfo);
    userInfo[key] = data;
    dispatch('SET_LOCAL_userInfo', {'userData': userInfo });
  },
  // GET_LOCAL_userInfo({getters, state}) {
  //   let usersList = state.getLocalUserList[getters.GET_userID];
  //   const userId = ;
  //   return usersList[userId]
  // }
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