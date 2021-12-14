import axios from "axios";
import { objectToQueryParams, getCookie } from "@/core/helpers";
import { stringifyNetworkObjects } from "@/core/helpers.js";

import { RYGG_BASE_URL } from "@/core/constants";
import { RYGG_URL_CONFIG_PATH } from "@/core/constants";
import { RYGG_VERSION_CONFIG_PATH } from "@/core/constants";
import { LOCAL_STORAGE_CURRENT_PROJECT } from "@/core/constants";
import { whenUrlIsResolved } from "@/core/urlResolver";
import { whenVersionIsResolved } from "@/core/versionResolver";
import { filePickerStorageKey } from "@/core/constants.js";

export const TASK_SUCCEEDED_STATE = "SUCCESS";
export const TASK_COMPLETED_STATES = [TASK_SUCCEEDED_STATE, "FAILED"];

const whenRyggReady = Promise.all([
  whenUrlIsResolved(RYGG_URL_CONFIG_PATH, RYGG_BASE_URL),
  whenVersionIsResolved(RYGG_VERSION_CONFIG_PATH),
]).then(([url]) => {
  let ret = axios.create();
  ret.defaults.baseURL = url;
  ret.defaults.headers.common["Content-Type"] = `application/json`;
  ret.defaults.params = {};
  return ret;
});

function whenHaveFileservingToken() {
  return whenRyggReady.then(requestor => {
    if (!!requestor.defaults.params["token"]) {
      return requestor;
    }

    // Try, in order, the cookie, env var, and finally the session storage
    const token =
      getCookie("fileserver_token") ||
      process.env.PL_FILE_SERVING_TOKEN ||
      sessionStorage.fileserver_token;

    if (!!token) {
      requestor.defaults.params["token"] = token;

      // Since we lose the cookie easily, save the token to session storage
      sessionStorage.fileserver_token = token;
    }
    return requestor;
  });
}

function currentProject() {
  let ret = parseInt(localStorage.getItem(LOCAL_STORAGE_CURRENT_PROJECT));
  if (!ret) {
    let msg = "called before current project is set";
    console.error(msg);
    throw new Error(msg);
  }
  return ret;
}

export const ryggAvailability = () => {
  return whenHaveFileservingToken()
    .then(requestor => requestor.get("/app/version/"))
    .then(
      res => {
        return res.status === 200 ? "AVAILABLE" : "UNAVAILABLE";
      },
      reject => {
        throw reject;
      },
    )
    .catch(err => {
      if (err && err.response && !!err.response.data) {
        console.log(err.response.data);
      }
      return err && err.response && err.response.status === 400
        ? "BAD_TOKEN"
        : "UNAVAILABLE";
    });
};

// rygg sends back 422 when it's a user error and the body contains the user-visible error message
function convert422(error) {
  if (!error.response) {
    throw error;
  }
  let newErr =
    error.response.status === 422 ? { userMessage: error.response.data } : {};
  throw newErr;
}

export const importRepositoryFromGithub = data => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileservingToken()
    .then(fs => fs.post(`/github/import?${queryParams}`, data))
    .catch(err => convert422(err));
};

export const exportAsGithubRepository = data => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileservingToken()
    .then(fs => fs.post(`/github/export?${queryParams}`, data))
    .then(res => {
      return res.data.URL;
    })
    .catch(err => convert422(err));
};

export const doesDirExist = path => {
  return whenHaveFileservingToken()
    .then(fs =>
      fs.head(`/directories?path=${path}&project_id=${currentProject()}`),
    )
    .then(res => {
      return res.status === 200;
    })
    .catch(err => {
      console.error(err);
      return false;
    });
};

export const getResolvedDir = path => {
  return whenHaveFileservingToken()
    .then(fs =>
      fs.get(
        `/directories/resolved_dir?path=${path}&project_id=${currentProject()}`,
      ),
    )
    .then(res => {
      return res.status === 200 ? res.data.path : null;
    })
    .catch(err => {
      return null;
    });
};

export const getModelJsonById = async model_id => {
  try {
    let fs = await whenHaveFileservingToken();
    let res = await fs.get(`/models/${model_id}/get_json/`);
    return res.status === 200 ? res.data.model_body : null;
  } catch (e) {
    return null;
  }
};

export const saveModelJson = async model => {
  const model_id = model.frontendSettings.apiMeta.model_id;
  if (!model_id) {
    let msg = "missing model_id";
    console.error(msg);
    console.log("model", model);
    throw new Error(msg);
  }
  const modelAsString = stringifyNetworkObjects(model);
  const url = `/models/${model_id}/save_json/`;

  let fs = await whenHaveFileservingToken();
  return await fs.post(url, modelAsString);
};

export const updateModelMeta = async model => {
  if (!model.frontendSettings.apiMeta.project) {
    let msg = "missing project from updateModelMeta";
    console.error(msg);
    throw new Error(msg);
  }
  const project_id = model.frontendSettings.apiMeta.project;
  if (currentProject() !== project_id) {
    let msg = "project_id mismatch";
    console.error(msg);
    throw new Error(msg);
  }
  let updatedPcModel = await getModelJsonById(
    model.frontendSettings.apiMeta.model_id,
  );
  if (updatedPcModel) {
    updatedPcModel.frontendSettings.networkMeta =
      model.frontendSettings.networkMeta;
  } else {
    updatedPcModel = {
      frontendSettings: {
        networkMeta: model.frontendSettings.networkMeta,
      },
    };
  }
  await saveModelJson(updatedPcModel);
};

export const getNextModelName = async prefix => {
  let fs = await whenHaveFileservingToken();
  const resp = await fs.get(
    `/models/next_name/?project_id=${currentProject()}&prefix=${prefix}`,
  );
  return resp.data.next_name;
};

export const doesFileExist = path => {
  return whenHaveFileservingToken()
    .then(fs => fs.head(`/files?path=${path}&project_id=${currentProject()}`))
    .then(res => {
      return res.status === 200;
    })
    .catch(err => {
      console.error(err);
      return false;
    });
};

export const getDatasetContent = async datasetId => {
  let fs = await whenHaveFileservingToken();
  let res = await fs.get(`/datasets/${datasetId}/content/`);
  console.log("res", res);
  return res.status === 200 ? res.data.file_contents : null;
};

export const pickFile = (title, initialDir = null, fileTypes = null) => {
  if (!initialDir && localStorage.hasOwnProperty(filePickerStorageKey)) {
    initialDir = localStorage.getItem(filePickerStorageKey);
  }
  return whenHaveFileservingToken()
    .then(fs =>
      fs.get(`/files/pick_file`, {
        params: {
          title: title,
          initial_dir: initialDir,
          file_types: fileTypes,
        },
      }),
    )
    .then(res => {
      return res.status === 200 ? res.data : null;
    })
    .then(res => {
      if (res && res.path) {
        localStorage.setItem(filePickerStorageKey, res.path);
      }
      return res;
    });
};

export const saveAsFile = (title, initialDir = null, fileTyps = null) => {
  if (!initialDir && localStorage.hasOwnProperty(filePickerStorageKey)) {
    initialDir = localStorage.getItem(filePickerStorageKey);
  }
  return whenHaveFileservingToken()
    .then(fs =>
      fs.get(`/files/saveas_file`, {
        params: {
          title: title,
          initial_dir: initialDir,
          file_types: fileTyps,
        },
      }),
    )
    .then(res => {
      return res.status === 200 ? res.data : null;
    })
    .then(res => {
      if (res && res.path) {
        localStorage.setItem(filePickerStorageKey, res.path);
      }
      return res;
    });
};

export const pickDirectory = (title, initialDir = null) => {
  if (!initialDir && localStorage.hasOwnProperty(filePickerStorageKey)) {
    initialDir = localStorage.getItem(filePickerStorageKey);
  }

  return whenHaveFileservingToken()
    .then(fs =>
      fs.get(`/directories/pick_directory`, {
        params: {
          title: title,
          initial_dir: initialDir,
        },
      }),
    )
    .then(res => {
      return res.status === 200 ? res.data : null;
    });
};

export const createFolder = path => {
  return whenHaveFileservingToken()
    .then(fs =>
      fs.post(`/directories?path=${path}&project_id=${currentProject()}`),
    )
    .then(res => {
      return res.status === 200 ? res.data.path : null;
    });
};

export const createIssueInGithub = data => {
  const queryParams = objectToQueryParams(data);
  return whenHaveFileservingToken().then(fs =>
    fs.post(
      `/github/issue?${queryParams}&project_id=${currentProject()}`,
      data,
    ),
  );
};

export const deleteFolder = path => {
  return whenHaveFileservingToken().then(fs =>
    fs.delete(`/directories?path=${path}&project_id=${currentProject()}`),
  );
};

export const getPublicDatasets = () => {
  return whenHaveFileservingToken()
    .then(fs => fs.get("/datasets/remote/"))
    .then(res => res.data);
};

export const getPublicDatasetCategories = () => {
  return whenHaveFileservingToken()
    .then(fs => fs.get("/datasets/remote_categories/"))
    .then(res => res.data);
};

export const downloadDataset = ({ id, name, projectId, path }) => {
  return whenHaveFileservingToken()
    .then(fs =>
      fs.post(
        `/datasets/create_from_remote/?id=${id}&name=${name}&project_id=${projectId}&path=${path}`,
        {},
      ),
    )
    .then(res => res.data && res.data.task_id);
};

/**
 * @typedef { Object } createClassificationSegmentationResponse
 * @property {string} task_id
 * @property {number} dataset_id
 * @property {string} dataset_location
 */
/**
 * @param {string} dataset_path
 * @returns {createClassificationSegmentationResponse}
 */
export const rygg_createClassificationDataset = async dataset_path => {
  try {
    const fs = await whenHaveFileservingToken();
    const res = await fs.post(
      `/datasets/create_classification_dataset/?project_id=${currentProject()}&dataset_path=${dataset_path}`,
      {},
    );
    return res.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

/**
 * @param {string} image_path - Path to images
 * @param {string} mask_path - Path to masks
 * @returns {createClassificationSegmentationResponse}
 */
export const rygg_createSegmentationDataset = async (image_path, mask_path) => {
  try {
    const fs = await whenHaveFileservingToken();
    const res = await fs.post(
      `/datasets/create_segmentation_dataset/?project_id=${currentProject()}&image_path=${image_path}&mask_path=${mask_path}`,
      {},
    );
    return res.data;
  } catch (e) {
    console.error(e);
    throw e;
  }
};

export const uploadDatasetToFileserver = async (file, overwrite = false) => {
  try {
    const data = new FormData();
    data.append("file_uploaded", file);
    data.append("name", file.name);
    data.append("overwrite", overwrite ? "true" : "false");
    const fs = await whenHaveFileservingToken();
    const res = await fs.post(
      `/datasets/create_from_upload/?project_id=${currentProject()}`,
      data,
    );
    if (![200, 201].includes(res.status)) {
      console.error("failed", res);
      return null;
    }
    return res;
  } catch (e) {
    console.error(e);
  }
};

export const isTaskComplete = status => {
  return TASK_COMPLETED_STATES.indexOf(status) >= 0;
};

export const getTaskStatus = async task_id => {
  let fs = await whenHaveFileservingToken();
  const res = await fs.get(`/tasks/${task_id}/`);
  return res.data;
};

export const cancelTask = async task_id => {
  let fs = await whenHaveFileservingToken();

  await fs.delete(`/tasks/${task_id}/`);
};

/**
 *
 * @param {Object} payload
 * @param {number} payload.project
 * @param {string} payload.name
 * @param {string} payload.location
 * @returns {Promise<AxiosResponse<any>>}
 */
export const createDataset = async payload => {
  try {
    console.error("createDataset", payload);
    const fs = await whenHaveFileservingToken();
    return await fs.post("datasets/", {
      project_id: currentProject(),
      ...payload,
    });
  } catch (e) {
    console.error(e);
  }
};
/**
 *
 * @param {string} filename
 * @returns {Promise<AxiosResponse<any>>}
 */
export const getDatasets = async filename => {
  try {
    const fs = await whenHaveFileservingToken();
    return await fs.get(
      `datasets/?filename=${filename}&project_id=${currentProject()}`,
    );
  } catch (e) {
    return Promise.reject(e);
  }
};
/**
 *
 * @param {number} datasetId
 * @returns {Promise<AxiosResponse<any>>}
 */
export const deleteDataset = async datasetId => {
  try {
    const fs = await whenHaveFileservingToken();
    return await fs.delete(`datasets/${datasetId}`);
  } catch (e) {
    return Promise.reject(e);
  }
};

/**
 *
 * @param {number} datasetId
 * @param {number} modelId
 * @returns {Promise<AxiosResponse<any>>}
 */
export const unregisterModel = async (datasetId, modelId) => {
  try {
    const fs = await whenHaveFileservingToken();
    return await fs.delete(`datasets/${datasetId}/models/?ids=${modelId}`);
  } catch (e) {
    return Promise.reject(e);
  }
};

/**
 *
 * @param {number} id
 * @returns {Promise<AxiosResponse<any>>}
 */
export const getDataset = async id => {
  try {
    const fs = await whenHaveFileservingToken();
    return await fs.get(`datasets/${id}/?project_id=${currentProject()}`);
  } catch (e) {
    return Promise.reject(e);
  }
};

/**
 *
 * @param {number} id
 * @returns {Promise<AxiosResponse<any>>}
 */
export const removeDataset = async id => {
  try {
    const fs = await whenHaveFileservingToken();
    return await fs.delete(`datasets/${id}/?project_id=${currentProject()}`);
  } catch (e) {
    return Promise.reject(e);
  }
};

export const attachModelsToDataset = async (id, models) => {
  const payload = {
    models,
  };
  try {
    const project_id = currentProject();
    const fs = await whenHaveFileservingToken();
    return await fs.patch(`datasets/${id}/`, payload);
  } catch (e) {
    return Promise.reject(e);
  }
};

export const isEnterpriseApp = async () => {
  if (sessionStorage.hasOwnProperty("isEnterpriseApp")) {
    return sessionStorage.getItem("isEnterpriseApp") == "true";
  }

  const fs = await whenHaveFileservingToken();
  const { data } = await fs.get("app/is_enterprise/");
  const ret = data.is_enterprise;
  sessionStorage.setItem("isEnterpriseApp", ret);
  return ret;
};

/**
 *
 * @param {string} default_directory
 * @param {string} name (required)
 */
export const createProjectWithDefaultDir = async (name, default_directory) => {
  if (
    !(await isEnterpriseApp()) &&
    (default_directory === null || default_directory.length == 0)
  ) {
    throw new Error("missing default_directory");
  }
  try {
    let fs = await whenHaveFileservingToken();
    let req = { name: name };
    if (!(await isEnterpriseApp())) {
      req.default_directory = default_directory;
    }

    let project_res = await fs.post("/projects/", req);
    if (![200, 201].includes(project_res.status)) {
      console.error("failed", project_res);
      return null;
    }
    let project_id = project_res.data.project_id;

    if (default_directory && !isEnterpriseApp()) {
      let folder_res = await fs.post(
        `/directories?path=${default_directory}&project_id=${project_id}`,
      );
      if (![200, 201].includes(folder_res.status)) {
        return null;
      }
      let path = folder_res.data.path;
      let patch_res = await fs.patch(`/projects/${project_id}/`, {
        default_directory: path,
      });
      if (![200, 201].includes(patch_res.status)) {
        return null;
      }
    }
    return project_res;
  } catch (e) {
    console.error(e);
    return Promise.reject(e);
  }
};

export const rygg = {
  get(path) {
    return whenRyggReady.then(requestor => requestor.get(path));
  },

  delete(path) {
    return whenRyggReady.then(requestor => requestor.delete(path));
  },

  post(path, payload) {
    return whenRyggReady.then(requestor => requestor.post(path, payload));
  },

  patch(path, payload) {
    return whenRyggReady.then(requestor => requestor.patch(path, payload));
  },

  put(path, payload) {
    return whenRyggReady.then(requestor => requestor.put(path, payload));
  },
};
