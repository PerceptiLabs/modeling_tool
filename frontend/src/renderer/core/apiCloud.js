import store            from '@/store'
import axios            from 'axios'
import { baseUrlCloud } from '@/core/constants.js'


const requestCloudApi = function (method, path, data, params) {
  // if(!store.state.globalView.onlineStatus) {
  //   return new Promise((resolve, reject) => resolve);
  // }
  return httpRequest(method, path, data, params)
    .then((response)=> response)
    .catch((error)=> {
      if(error.response.status === 401) { return 'updateToken' }
      else {
        store.dispatch('mod_tracker/EVENT_cloudError', {method, path, error});
        //console.log('error.response', error.response);
        store.dispatch('globalView/GP_errorPopup', error.response.data);
        console.log(error);
      }
    })
    .then((answer)=> {
      if(answer === 'updateToken') {
        return CloudAPI_updateToken()
          .then(()=> httpRequest(method, path, data))
          .then((answ)=> answ)
          .catch((error)=> {
            throw(error)
          })
      }
      else return answer
    })
};

function httpRequest(method, path, data, params) {
  const userToken = store.state.mod_user.userToken;
  const headers = {
    'Content-Type': 'application/json-patch+json',
  };

  if(userToken.length) {
    headers.Authorization = `Bearer ${userToken}`
  }
  return axios({
    headers,
    method,
    url: baseUrlCloud + path,
    data,
    params
  })
    .then((response)=> response)
    .catch((error) => {
      throw (error);
    });
}

function CloudAPI_updateToken() {
  const body = {
    "refreshToken": store.state.mod_user.userTokenRefresh
  };
  console.log('CloudAPI_updateToken', body);
  console.log('user tokens / token refresh', store.state.mod_user.userToken, store.state.mod_user.userTokenRefresh);
  return httpRequest('post', 'Customer/UpdateToken', body)
    .then((response)=> {
      console.log('CloudAPI_updateToken answer', response);
      const tokens = response.data.data;
      store.dispatch('mod_user/SET_userToken', tokens, {root: true});
      return tokens
    })
    .catch((error)=> {
      store.dispatch('mod_events/EVENT_logOut', false, {root: true});
      store.dispatch('globalView/GP_errorPopup', 'You have not worked with the application for a long time. Please login');
      console.log(error);
    })
}

export { requestCloudApi };
