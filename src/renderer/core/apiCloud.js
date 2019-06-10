const baseURL = 'https://quantumnet.azurewebsites.net/api/';

const requestCloudApi = function (method, path, dataRequest) {
  return this.$http({
    method: method,
    url: baseURL + path,
    //headers: {'X-Requested-With': 'XMLHttpRequest'},
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
