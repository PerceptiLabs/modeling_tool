const baseURL = 'https://quantumnet.azurewebsites.net/api/';

const requestCloudApi = function (method, path, dataRequest, callback) {
  this.$http({
    method: method,
    url: baseURL + path,
    //headers: {'X-Requested-With': 'XMLHttpRequest'},
    data: dataRequest
    //...queryParams // data: {request body}, params: {query params}
  })
    .then((response)=>{
      //this.$store.dispatch('remCounterRequest');
      callback('success', response);
    })
    .catch((error)=>{
      console.log(error);
      ///this.$store.dispatch('remCounterRequest');
      callback('error');
    });
};

export { baseURL, requestCloudApi};
