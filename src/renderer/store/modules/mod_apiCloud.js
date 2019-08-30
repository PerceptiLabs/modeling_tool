import {requestCloudApi}  from '@/core/apiCloud.js'

const namespaced = true;
const state = {};
const getters = {};
const mutations = {};
const actions = {
  /*COMMON ACTIONS*/
  CloudAPI_updateToken({dispatch, rootState}) {
    const body = {
      "refreshToken": rootState.mod_user.userTokenRefresh
    };
    console.log(body);
    return requestCloudApi('post', 'Customer/UpdateToken', body)
      .then((response)=> {
        console.log('CloudAPI_updateToken ok');
        const tokens = response.data.data;
        dispatch('mod_user/SET_userToken', tokens, {root: true});
        return tokens
      })
      .catch((error)=> {
        console.log('CloudAPI_updateToken logOut');
        dispatch('mod_events/EVENT_logOut', null, {root: true});
      })
  },
  /*USER ACTIONS*/
  CloudAPI_userLogin({dispatch}, userInfo) {
    return requestCloudApi('post', 'Customer/Login', userInfo)
      .then((response)=> {
        const tokens = response.data.data;
        dispatch('mod_user/SET_userToken', tokens, {root: true});
        dispatch('mod_user/CHECK_LOCAL_usersList', null, {root: true});
        dispatch('mod_tracker/TRACK_createUser', userInfo.Email, {root: true});
        return tokens
      })
      // .catch((error)=> {
      //   console.log(error);
      //   throw (error);
      // })
  },
  CloudAPI_userLogout({getters, rootState}) {
    const body = {
      "refreshToken": rootState.mod_user.userTokenRefresh
    };
    requestCloudApi('post', 'Customer/Logout', body)
  },
  CloudAPI_userCreate({dispatch}, userInfo) {
    return requestCloudApi('post', 'Customer/CreateGuest', userInfo)
      .then((response)=> {
        dispatch('globalView/GP_infoPopup',
          'A confirmation email has been sent to your email. Follow the link to complete the registration.',
          {root: true});
        return true
      })
    // .catch((error)=> {
    //   console.log(error);
    //   throw (error);
    // })
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
