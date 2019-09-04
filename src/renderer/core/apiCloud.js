import Vue    from 'vue'
import store  from '@/store'
import { baseUrlCloud }  from '@/core/constants.js'


const requestCloudApi = function (method, path, dataRequest) {
  const userToken = store.state.mod_user.userToken;
  const headers = userToken.length
    ? {'authorization': `Bearer ${userToken}`}
    : '';
  console.log('first request token', userToken);
  return Vue.http({
    method: method,
    url: baseUrlCloud + path,
    headers: headers,
    data: dataRequest
    //...queryParams // data: {request body}, params: {query params}
  })
    .then((response)=> response)
    .catch((error)=> {
      console.log(error);
      if(error.response.status === 401) { return 'updateToken' }
      else {
        store.dispatch('mod_tracker/EVENT_cloudError', error);
        store.dispatch('globalView/GP_errorPopup', error.response.data);
        throw (error);
      }
    })
    .then((data)=> {
      if(data === 'updateToken') {
        return CloudAPI_updateToken()
          .then(()=> singleRequest(method, path, dataRequest))
          .then((data)=> data)
          .catch((error)=> { throw (error) })
      }
      else return data
    })

};

function singleRequest(method, path, dataRequest) {
  console.log('second request token', store.state.mod_user.userToken);
  return Vue.http({
    method: method,
    url: baseUrlCloud + path,
    headers: {'authorization': `Bearer ${store.state.mod_user.userToken}`},
    data: dataRequest
    //...queryParams // data: {request body}, params: {query params}
  })
    .then((response)=> response)
}

function CloudAPI_updateToken() {
  const body = {
    "refreshToken": store.state.mod_user.userTokenRefresh
  };
  return singleRequest('post', 'Customer/UpdateToken', body)
    .then((response)=> {
      const tokens = response.data.data;
      store.dispatch('mod_user/SET_userToken', tokens, {root: true});
      console.log('new token', tokens.accessToken);
      return tokens
    })
    .catch((error)=> {
      console.log('CloudAPI_updateToken logOut');
      store.dispatch('mod_events/EVENT_logOut', null, {root: true});
      store.dispatch('globalView/GP_errorPopup', 'You have not worked with the application for a long time. Please login');
    })
}

export { requestCloudApi };
// test@test.com