import Vue    from 'vue'
import store  from '@/store'
import { baseUrlCloud }  from '@/core/constants.js'


const requestCloudApi = function (method, path, dataRequest, isUpdate) {
  console.log('first request', path);
  let isUpdates = isUpdate === undefined ? true : isUpdate;
  const userToken = store.state.mod_user.userToken;
  const headers = userToken.length
    ? {'authorization': `Bearer ${userToken}`}
    : '';
  console.log('userToken', userToken);
  return Vue.http({
    method: method,
    url: baseUrlCloud + path,
    headers: headers,
    data: dataRequest
    //...queryParams // data: {request body}, params: {query params}
  })
    .then((response)=> response)
    .catch((error)=> {
      console.log(error.response.status, isUpdates);
      if(error.response.status === 401 && isUpdates) {
        store.dispatch('mod_apiCloud/CloudAPI_updateToken')
          .then(()=> {
            console.log('second request', path);
            requestCloudApi(method, path, dataRequest, false)
          })
          .catch((error)=> {
            throw (error);
          })
      }
      else {
        store.dispatch('mod_tracker/EVENT_cloudError', error);
        store.dispatch('globalView/GP_errorPopup', error.response.data);
        throw (error);
      }
    })
};

export { requestCloudApi };
// test@test.com