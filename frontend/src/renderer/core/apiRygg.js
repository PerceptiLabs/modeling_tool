import axios            from 'axios'
import { objectToQueryParams, getCookie } from '@/core/helpers'
import { stringifyNetworkObjects }   from "@/core/helpers.js";

import { RYGG_BASE_URL } from '@/core/constants'
import { RYGG_URL_CONFIG_PATH }   from "@/core/constants";
import { RYGG_VERSION_CONFIG_PATH } from "@/core/constants";
import { whenUrlIsResolved } from '@/core/urlResolver';
import { whenVersionIsResolved } from '@/core/versionResolver';

const whenRyggReady = whenUrlIsResolved(RYGG_URL_CONFIG_PATH, RYGG_BASE_URL)
  .then(url => {
    let ret = axios.create();
    ret.defaults.baseURL = url
    ret.defaults.headers.common["Content-Type"] = `application/json`;
    ret.defaults.params = {}
    return ret
  });

function whenHaveFileservingToken(){
  return whenRyggReady
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

export const ryggAvailability = () => {
  return whenHaveFileservingToken()
    .then(requestor => requestor.get("/app/version"))
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

// rygg sends back 422 when it's a user error and the body contains the user-visible error message
function convert422(error) {
  if (!error.response) {
    throw error;
  }
  let newErr = (error.response.status === 422) ? {userMessage: error.response.data} : {};
  throw newErr;
}

export const importRepositoryFromGithub = (data) => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileservingToken()
    .then(fs => fs.post(`/github/import?${queryParams}`, data))
    .catch(err => convert422(err))
}

export const exportAsGithubRepository = (data) => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileservingToken()
    .then(fs => fs.post(`/github/export?${queryParams}`, data))
    .then(res => { return res.data.URL; })
    .catch(err => convert422(err))
}

export const doesDirExist = (path) => {
  return whenHaveFileservingToken()
    .then(fs => fs.head(`/directories?path=${path}`))
    .then(res => {
      return (res.status === 200);
    }).catch((err) => {
      console.error(err);
      return false;
    })
}

export const getFolderContent = (path) => {
  return whenHaveFileservingToken()
    .then(fs => fs.get(`/directories/get_folder_content?path=${path}`))
    .then(res => {
      return (res.status === 200)? res.data : null
    })
}

export const getRootFolder = () => {
  return whenHaveFileservingToken()
    .then(fs => fs.get(`/directories/root`))
    .then(res => {
      return (res.status === 200)? res.data.path : "/"
    })
}

export const getResolvedDir = (path) => {
  return whenHaveFileservingToken()
    .then(fs => fs.get(`/directories/resolved_dir?path=${path}`))
    .then(res => {
      return (res.status === 200)? res.data.path : null
    })
    .catch(err => { return null })
}

export const getModelJson = (path) => {
  return whenHaveFileservingToken()
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
  return whenHaveFileservingToken()
    .then(fs => fs.post(`/json_models?path=${path}`, modelAsString))
}

export const updateModelMeta = async (model) => {
  const path = model.apiMeta.location;
  const updatedPcModel = await getModelJson(path);
  updatedPcModel.networkMeta = model.networkMeta;
  await saveModelJson(updatedPcModel);
}

export const doesFileExist = (path) => {
  return whenHaveFileservingToken()
    .then(fs => fs.head(`/files?path=${path}`))
    .then(res => {
      return (res.status === 200);
    }).catch((err) => {
      console.error(err);
      return false;
    })
}

export const getFileContent = (path) => {
  return whenHaveFileservingToken()
    .then(fs => fs.get(`/files/get_file_content?path=${path}`))
    .then(res => {
      return (res.status === 200) ? res.data : null;
    })
}

export const createFolder = (path) => {
  return whenHaveFileservingToken()
    .then(fs => fs.post(`/directories?path=${path}`))
    .then(res => {
      return (res.status === 200)? res.data.path : null
    })
}

export const createIssueInGithub = (data) => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileservingToken()
    .then(fs => fs.post(`/github/issue?${queryParams}`, data))
}

export const deleteFolder = (path) => {
  return whenHaveFileservingToken()
    .then(fs => fs.delete(`/directories?path=${path}`))
}

export const isUrlReachable = async (path) => {
  try {
    const fs = await whenHaveFileservingToken();
    const res = await fs.get(`/is_url_reachable?path=${path}`);
    let ret = (res.data.response_code === 200) ? true : false;
    return ret;
  } catch (err) {
    return false;
  }
}

export const uploadDatasetToFileserver = async (file, overwrite = false) => {
  try {
    const data = new FormData();
    data.append('file_uploaded', file);
    data.append('name', file.name);
    data.append('overwrite', overwrite ? 'true': 'false');
    const fs = await whenHaveFileservingToken();
    return await fs.post('/upload', data);
  } catch(e) {
    console.error(e);
  }
}

export const rygg = {

  get(path) {
    return whenRyggReady.then(requestor => requestor.get(path))
  },

  delete(path) {
    return whenRyggReady.then(requestor => requestor.delete(path))
  },

  post(path, payload) {
    return whenRyggReady.then(requestor => requestor.post(path, payload))
  },

  patch(path, payload) {
    return whenRyggReady.then(requestor => requestor.patch(path, payload))
  },

  put(path, payload) {
    return whenRyggReady.then(requestor => requestor.put(path, payload))
  },
};

