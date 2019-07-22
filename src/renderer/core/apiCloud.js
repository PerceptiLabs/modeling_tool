//const baseURL = 'https://quantumnet-cont.azurewebsites.net/api/';
const baseURL = 'https://perceptilabs-dev.azurewebsites.net/api/';

const requestCloudApi = function (method, path, dataRequest) {
  let headers = localStorage.getItem('userToken')
    ? {'authorization': 'Bearer ' + localStorage.getItem('userToken')}
    : '';

  return this.$http({
    method: method,
    url: baseURL + path,
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

export { baseURL, requestCloudApi};
