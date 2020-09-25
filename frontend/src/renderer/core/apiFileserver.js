import axios            from 'axios'
import { objectToQueryParams } from '@/core/helpers'
import { FILE_SERVER_BASE_URL } from '@/core/constants'
import { stringifyNetworkObjects }   from "@/core/helpers.js";

const fileServerHttpReqest =  axios.create();
fileServerHttpReqest.defaults.baseURL = FILE_SERVER_BASE_URL
fileServerHttpReqest.defaults.headers.common["Content-Type"] = `application/json`;
fileServerHttpReqest.defaults.params = {}
fileServerHttpReqest.defaults.params['token'] = process.env.PL_FILE_SERVING_TOKEN

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

if (!process.env.PL_FILE_SERVING_TOKEN) {
  // This section is for when the frontend is built as static files.
  // (process.env is not available then)
	const token = getCookie("fileserver_token")
	fileServerHttpReqest.defaults.params['token'] = token
}

export const fileserverAvailability = () => {
  return fileServerHttpReqest.get("/version")
  .then(res => {
    return (res.status === 200) ? "AVAILABLE" : "UNAVAILABLE"
  })
  .catch(err => {
    return (err.response && err.response.status === 400)? "BAD_TOKEN" : "UNAVAILABLE"
  })
}

export const importRepositoryFromGithub = (data) => {
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/import?${queryParams}`, data);
}

export const exportAsGithubRepository = (data) => {
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/export?${queryParams}`, data)
}

export const doesDirExist = (path) => {
  return fileServerHttpReqest.head(`/directories?path=${path}`)
  .then(res => {
    return (res.status === 200);
  })
}

export const getFolderContent = (path) => {
  return fileServerHttpReqest.get(`/directories/get_folder_content?path=${path}`)
    .then(res => {
      return (res.status === 200)? res.data : null
    })
}

export const getRootFolder = () => {
  return fileServerHttpReqest.get(`/directories/root`)
    .then(res => {
      return (res.status === 200)? res.data.path : "/"
    })
}

export const getResolvedDir = (path) => {
  return fileServerHttpReqest.get(`/directories/resolved_dir?path=${path}`)
    .then(res => {
      return (res.status === 200)? res.data.path : null
    })
    .catch(err => { return null })
}

export const getModelJson = (path) => {
  return fileServerHttpReqest.get(`/json_models?path=${path}`)
    .then(res => {
      let ret = (res.status === 200)? res.data.model_body : null
      return ret
    })
    .catch(err => { return null })
}

export const saveModelJson = (model) => {
  const path = `${model.apiMeta.location}`;
  const modelAsString = stringifyNetworkObjects(model)
  return fileServerHttpReqest.post(`/json_models?path=${path}`, modelAsString)
}

export const doesFileExist = (path) => {
  return fileServerHttpReqest.head(`/files?path=${path}`)
  .then(res => {
    return (res.status === 200);
  })
}

export const createFolder = (path) => {
  return fileServerHttpReqest.post(`/directories?path=${path}`)
    .then(res => {
      return (res.status === 200)? res.data.path : null
    })
}

export const createIssueInGithub = (params, data) => {
  const queryParams = objectToQueryParams(params);
  return fileServerHttpReqest.post(`/github/issue?${queryParams}`, data)
}
