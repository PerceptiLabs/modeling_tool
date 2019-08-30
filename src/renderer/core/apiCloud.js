import Vue    from 'vue'
import store  from '@/store'
import { baseUrlCloud }  from '@/core/constants.js'


const requestCloudApi = function (method, path, dataRequest) {
  console.log('first request');
  const userToken = store.state.mod_user.userToken;
  const headers = userToken.length
    ? {'authorization': `Bearer ${userToken}`}
    : '';

  return Vue.http({
    method: method,
    url: baseUrlCloud + path,
    headers: headers,
    data: dataRequest
    //...queryParams // data: {request body}, params: {query params}
  })
    .then((response)=> response)
    .catch((error)=> {
      console.error(error.response.status);
      if(error.response.status === 401) {
        store.dispatch('mod_apiCloud/CloudAPI_updateToken')
          .then(()=> {
            console.log('second request');
            return requestCloudApi(method, path, dataRequest)
          })
      }
      else {
        store.dispatch('mod_tracker/EVENT_cloudError', error);
        store.dispatch('globalView/GP_errorPopup', error.response.data);
        throw (error);
      }
    })


    ;
};

export { requestCloudApi };
// test@test.com