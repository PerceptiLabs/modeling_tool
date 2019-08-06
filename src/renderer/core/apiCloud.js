import store from '@/store'
import { baseUrlCloud }  from '@/core/constants.js'


const requestCloudApi = function (method, path, dataRequest) {
  const userToken = store.state.mod_user.userToken;
  const headers = userToken.length
    ? {'authorization': `Bearer ${userToken}`}
    : '';

  return this.$http({
    method: method,
    url: baseUrlCloud + path,
    headers: headers,
    data: dataRequest
    //...queryParams // data: {request body}, params: {query params}
  })
    .then((response)=> response)
    .catch((error)=> {
      store.dispatch('mod_tracker/EVENT_cloudError', error);
      throw (error.response.data);
    });
};

export { requestCloudApi };
