import axios            from 'axios'
import { objectToQueryParams } from '@/core/helpers'
import { stringifyNetworkObjects, getCookie }   from "@/core/helpers.js";

import { FILESERVER_BASE_URL } from '@/core/constants'
import { FILESERVER_URL_CONFIG_PATH }   from "@/core/constants";
import { whenUrlIsResolved } from '@/core/urlResolver';

const whenFileserverReady = whenUrlIsResolved(FILESERVER_URL_CONFIG_PATH, FILESERVER_BASE_URL)
  .then(url => {
    let ret = axios.create();
    ret.defaults.baseURL = url
    ret.defaults.headers.common["Content-Type"] = `application/json`;
    ret.defaults.params = {}
    return ret
  });

function whenHaveFileserverToken(){
  return whenFileserverReady
    .then(requestor => {
      if (!!requestor.defaults.params['token']) {
        return requestor;
      }

      // Try, in order, the cookie, env var, and finally the session storage
      const token =
        getCookie("fileserver_token") ||
        process.env.PL_FILE_SERVING_TOKEN ||
        sessionStorage.fileserver_token;

      if (!!token) {
        requestor.defaults.params['token'] = token;

        // Since we lose the cookie easily, save the token to session storage
        sessionStorage.fileserver_token = token;
      }
      return requestor;
    });
}

export const fileserverAvailability = () => {
  return whenHaveFileserverToken()
    .then(requestor => requestor.get("/version"))
    .then(res => {
      return (res.status === 200) ? "AVAILABLE" : "UNAVAILABLE"
    }, (reject) => {
      throw reject;
    })
    .catch(err => {
      if (err.response && !!err.response.data){ console.log(err.response.data) }
      return (err.response && err.response.status === 400)? "BAD_TOKEN" : "UNAVAILABLE"
    })
}

// fileserver sends back 422 when it's a user error and the body contains the user-visible error message
function convert422(error) {
  if (!error.response) {
    throw error;
  }
  let newErr = (error.response.status === 422) ? {userMessage: error.response.data} : {};
  throw newErr;
}

export const importRepositoryFromGithub = (data) => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileserverToken()
    .then(fs => fs.post(`/github/import?${queryParams}`, data))
    .catch(err => convert422(err))
}

export const exportAsGithubRepository = (data) => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileserverToken()
    .then(fs => fs.post(`/github/export?${queryParams}`, data))
    .then(res => { return res.data.URL; })
    .catch(err => convert422(err))
}

export const doesDirExist = (path) => {
  return whenHaveFileserverToken()
    .then(fs => fs.head(`/directories?path=${path}`))
    .then(res => {
      return (res.status === 200);
    })
}

export const getFolderContent = (path) => {
  return whenHaveFileserverToken()
    .then(fs => fs.get(`/directories/get_folder_content?path=${path}`))
    .then(res => {
      return (res.status === 200)? res.data : null
    })
}

export const getRootFolder = () => {
  return whenHaveFileserverToken()
    .then(fs => fs.get(`/directories/root`))
    .then(res => {
      return (res.status === 200)? res.data.path : "/"
    })
}

export const getResolvedDir = (path) => {
  return whenHaveFileserverToken()
    .then(fs => fs.get(`/directories/resolved_dir?path=${path}`))
    .then(res => {
      return (res.status === 200)? res.data.path : null
    })
    .catch(err => { return null })
}

export const getModelJson = (path) => {
  return whenHaveFileserverToken()
    .then(fs => fs.get(`/json_models?path=${path}`))
    .then(res => {
      let ret = (res.status === 200)? res.data.model_body : null
      return ret
    })
    .catch(err => { return null })
}

export const saveModelJson = (model) => {
  const path = `${model.apiMeta.location}`;
  const modelAsString = stringifyNetworkObjects(model)
  return whenHaveFileserverToken()
    .then(fs => fs.post(`/json_models?path=${path}`, modelAsString))
}

export const doesFileExist = (path) => {
  return whenHaveFileserverToken()
    .then(fs => fs.head(`/files?path=${path}`))
    .then(res => {
      return (res.status === 200);
    })
}

export const createFolder = (path) => {
  return whenHaveFileserverToken()
    .then(fs => fs.post(`/directories?path=${path}`))
    .then(res => {
      return (res.status === 200)? res.data.path : null
    })
}

export const createIssueInGithub = (data) => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileserverToken()
    .then(fs => fs.post(`/github/issue?${queryParams}`, data))
}

export const deleteFolder = (path) => {
  return whenHaveFileserverToken()
    .then(fs => fs.delete(`/directories?path=${path}`))
}
