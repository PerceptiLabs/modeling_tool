import {requestCloudApi}  from '@/core/apiCloud.js'
const namespaced = true;
const state = {};
const getters = {};
const mutations = {};
const actions = {
  /*COMMON ACTIONS*/
  // CloudAPI_updateToken({dispatch, rootState}) {
  //   const body = {
  //     "refreshToken": rootState.mod_user.userTokenRefresh
  //   };
  //   return requestCloudApi('post', 'Customer/UpdateToken', body)
  //     .then((response)=> {
  //       const tokens = response.data.data;
  //       dispatch('mod_user/SET_userToken', tokens, {root: true});
  //       console.log('new token', tokens);
  //       return tokens
  //     })
  //     .catch((error)=> {
  //       console.log('CloudAPI_updateToken logOut');
  //       dispatch('mod_events/EVENT_logOut', null, {root: true});
  //       throw (error);
  //     })
  // },
  /*USER ACTIONS*/
  CloudAPI_userLogin({dispatch}, userInfo) {
    return requestCloudApi('post', 'Customer/Login', userInfo)
      .then((response)=> {
        const tokens = response.data.data;
        dispatch('mod_user/SET_userToken', tokens, {root: true});
        dispatch('mod_user/CHECK_LOCAL_usersList', null, {root: true});
        return tokens
      })
      .catch((error)=> console.log('CloudAPI_userLogin', error) )
  },
  CloudAPI_userLogout({getters, rootState}) {
    const body = {
      "refreshToken": rootState.mod_user.userTokenRefresh
    };
    requestCloudApi('post', 'Customer/Logout', body)
      .then((response)=> {})
      .catch((error)=> console.log('CloudAPI_userLogout', error) )
  },
  CloudAPI_userCreate({dispatch}, userInfo) {
    return requestCloudApi('post', 'Customer/CreateGuest', userInfo)
      .then((response)=> {
        dispatch('globalView/GP_infoPopup',
          'A confirmation email has been sent to your email. Follow the link to complete the registration.',
          {root: true});
        return true
      })
      .catch((error)=> console.log('CloudAPI_userCreate', error) )
  },

  CloudAPI_userGetProfile({dispatch}) {
    return requestCloudApi('get', 'Customer/Profile')
      .then((response)=> {
        let profile = response.data.data;
        dispatch('mod_user/SET_userProfile', profile, {root: true});
        return true
      })
      .catch((error)=>  {
        if (error.response.status === 401) {
          localStorage.removeItem('currentUser');
        }
      } )
  },
  CloudAPI_userForgotPassword({dispatch}, email) {
    return requestCloudApi('post', 'Customer/ForgotPassword', `'${email}'`)
      .then((response)=> response.status === 200 )
      .catch((error)=> console.log('CloudAPI_userForgotPassword', error) )
  },
  CloudAPI_userSetProfile({dispatch}, user) {
    return requestCloudApi('post', 'Customer/Profile', user)
      .then((response)=> response.status === 200 )
      .catch((error)=> console.log('CloudAPI_userSetProfile', error) )
  },
  CloudAPI_userChangeEmail({dispatch}, dataBody) {
    return requestCloudApi('post', 'Customer/ChangeEmail', dataBody)
      .then((response)=> response.status === 200 )
      .catch((error)=> console.log('CloudAPI_userChangeEmail', error) )
  },
  CloudAPI_userChangePassword({dispatch}, dataBody) {
    return requestCloudApi('post', 'Customer/ChangePassword', dataBody)
      .then((response)=> response.status === 200 )
      .catch((error)=> console.log('CloudAPI_userChangePassword', error) )
  },
  CloudAPI_checkStatus({dispatch}) {
    return requestCloudApi('get', 'Customer/Profile')
      .then((response)=> response )
      .catch((error)=> console.log('CloudAPI_checkStatus', error) )
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
