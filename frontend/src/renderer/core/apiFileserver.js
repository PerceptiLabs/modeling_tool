import axios            from 'axios'
import { objectToQueryParams } from '@/core/helpers'
import { FILE_SERVER_BASE_URL } from '@/core/constants'
import { stringifyNetworkObjects }   from "@/core/helpers.js";

const fileServerHttpReqest =  axios.create();
fileServerHttpReqest.defaults.baseURL = FILE_SERVER_BASE_URL
fileServerHttpReqest.defaults.headers.common["Content-Type"] = `application/json`;
fileServerHttpReqest.defaults.params = {}

function getCookie(name) {
    const cookieArr = document.cookie.split(";");

    for(var i = 0; i < cookieArr.length; i++) {
        const cookiePair = cookieArr[i].split("=");

        if(name == cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }

    return null;
}

export function pullTokenFromEnv() {
  if (!!fileServerHttpReqest.defaults.params['token']) {
    return;
  }

  // Try, in order, the cookie, env var, and finally the session storage
  const token =
    getCookie("fileserver_token") ||
    process.env.PL_FILE_SERVING_TOKEN ||
    sessionStorage.fileserver_token

  if (!!token) {
    fileServerHttpReqest.defaults.params['token'] = token

    // Since we lose the cookie easily, save the token to session storage
    sessionStorage.fileserver_token = token
  }
}

export const fileserverAvailability = () => {
  pullTokenFromEnv();
  return fileServerHttpReqest.get("/version")
  .then(res => {
    return (res.status === 200) ? "AVAILABLE" : "UNAVAILABLE"
  })
  .catch(err => {
    return (err.response && err.response.status === 400)? "BAD_TOKEN" : "UNAVAILABLE"
  })
}

export const importRepositoryFromGithub = (data) => {
  pullTokenFromEnv();
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/import?${queryParams}`, data);
}

export const exportAsGithubRepository = (data) => {
  pullTokenFromEnv();
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/export?${queryParams}`, data)
}

export const doesDirExist = (path) => {
  pullTokenFromEnv();
  return fileServerHttpReqest.head(`/directories?path=${path}`)
  .then(res => {
    return (res.status === 200);
  })
}

export const getFolderContent = (path) => {
  pullTokenFromEnv();
  return fileServerHttpReqest.get(`/directories/get_folder_content?path=${path}`)
    .then(res => {
      return (res.status === 200)? res.data : null
    })
}

export const getRootFolder = () => {
  pullTokenFromEnv();
  return fileServerHttpReqest.get(`/directories/root`)
    .then(res => {
      return (res.status === 200)? res.data.path : "/"
    })
}

export const getResolvedDir = (path) => {
  pullTokenFromEnv();
  return fileServerHttpReqest.get(`/directories/resolved_dir?path=${path}`)
    .then(res => {
      return (res.status === 200)? res.data.path : null
    })
    .catch(err => { return null })
}

export const getModelJson = (path) => {
  pullTokenFromEnv();
  return fileServerHttpReqest.get(`/json_models?path=${path}`)
    .then(res => {
      let ret = (res.status === 200)? res.data.model_body : null
      return ret
    })
    .catch(err => { return null })
}

export const saveModelJson = (model) => {
  pullTokenFromEnv();
  const path = `${model.apiMeta.location}`;
  const modelAsString = stringifyNetworkObjects(model)
  return fileServerHttpReqest.post(`/json_models?path=${path}`, modelAsString)
}

export const doesFileExist = (path) => {
  pullTokenFromEnv();
  return fileServerHttpReqest.head(`/files?path=${path}`)
  .then(res => {
    return (res.status === 200);
  })
}

export const createFolder = (path) => {
  pullTokenFromEnv();
  return fileServerHttpReqest.post(`/directories?path=${path}`)
    .then(res => {
      return (res.status === 200)? res.data.path : null
    })
}

export const createIssueInGithub = (data) => {
  pullTokenFromEnv();
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/issue?${queryParams}`, data)
}
