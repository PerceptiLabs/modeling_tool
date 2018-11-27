const baseURL = 'https://quantumnet.azurewebsites.net/api/';

const requestCloudApi = function (method, path, params, callback) {
  //this.$store.dispatch('addCounterRequest');
  //let token = getCookie('benary');
  let queryParams = {};
  if(method === "get") {
    queryParams.params =
      {
        ...params,
        //'store': this.$i18n.locale,
      };

  }
  else {
    queryParams.data = params;
    //queryParams.params = {'store': this.$i18n.locale}
  }

  this.$http({
    method: method,
    url: baseURL + path,
    //headers: {'Authorization': 'Bearer ' + token},
    ...queryParams
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

// this.requestApiContent('get', 'me/messages', queryParams, (result, response) => {
//   if (result === 'success') {
//     let total = response;
//   }
// })
export { baseURL, requestCloudApi};
