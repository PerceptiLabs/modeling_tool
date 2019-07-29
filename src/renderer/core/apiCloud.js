import store from '@/store'
import { baseUrlCloud }  from '@/core/constants.js'


const requestCloudApi = function (method, path, dataRequest) {
  const userToken = store.state.globalView.userToken;
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
    .then((response)=>{
      //console.log(response);
      return response
    })
    .catch((error)=>{
      throw (error.response.data);
    });
};

export { requestCloudApi };
