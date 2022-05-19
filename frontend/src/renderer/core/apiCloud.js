import store            from '@/store'
import axios            from 'axios'
import { baseUrlCloud } from '@/core/constants.js'

const requestCloudApi = function (method, path, data, params) {
  return Promise.reject({
    response: {}
  });
  // if(!store.state.globalView.onlineStatus) {
  //   return new Promise((resolve, reject) => resolve);
  // }
  // return httpRequest(method, path, data, params)
  //   .then((response)=> response)
  //   .catch((error)=> {
  //     if(error.response.status === 401) { return 'updateToken' }
  //     else {
  //       store.dispatch('mod_tracker/EVENT_cloudError', {method, path, error});
  //       store.dispatch('globalView/GP_errorPopup', error.response.data);
  //       throw(error.response)
  //     }
  //   })
  //   .then((answer)=> {
  //     if(answer === 'updateToken') {
  //       return CloudAPI_updateToken()
  //         .then(()=> httpRequest(method, path, data))
  //         .then((answ)=> answ)
  //         .catch((error)=> {
  //           throw(error)
  //         })
  //     }
  //     else return answer
  //   })
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

export { requestCloudApi };
