import axios from "axios";
import LogRocket from "logrocket";
import { RENDERING_KERNEL_BASE_URL } from "@/core/constants";
import { RENDERING_KERNEL_URL_CONFIG_PATH } from "@/core/constants";
import { whenUrlIsResolved } from "@/core/urlResolver";
import AuthService from "@/core/auth";

let logRocketURL = null;
LogRocket.getSessionURL(function(sessionURL) {
  logRocketURL = sessionURL;
});

const whenRenderingKernelReady = whenUrlIsResolved(
  RENDERING_KERNEL_URL_CONFIG_PATH,
  RENDERING_KERNEL_BASE_URL,
).then(url => {
  const config = {
    baseURL: url,
    headers: { "Content-Type": "application/json" },
    params: {},
  };
  let ret = axios.create(config);

  ret.interceptors.request.use(function(config) {
    const userToken = AuthService.getToken();
    config.headers["Authorization"] = `Bearer ${userToken}`;

    if (logRocketURL) {
      config.headers["X-LogRocket-URL"] = logRocketURL;
    }
    return config;
  });

  return ret;
});

export const renderingKernel = {
  async hasCheckpoint(modelId, trainingSessionId) {
    return whenRenderingKernelReady
      .then(rk =>
        rk.get(
          `/models/${modelId}/training/${trainingSessionId}/has_checkpoint`,
        ),
      )
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async exportModel(
    exportSettings,
    datasetSettings,
    userEmail,
    modelId,
    network,
    trainingSessionId,
    trainingSettings,
    frontendSettings,
  ) {
    const payload = {
      exportSettings: exportSettings,
      datasetSettings: datasetSettings,
      graphSettings: network,
      userEmail: userEmail,
      trainingSettings: trainingSettings,
      frontendSettings: frontendSettings,
    };
    return whenRenderingKernelReady
      .then(rk =>
        rk.put(
          `/models/${modelId}/export?training_session_id=${trainingSessionId}`,
          payload,
        ),
      )
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async serveModel(
    datasetSettings,
    userEmail,
    modelId,
    network,
    trainingSessionId,
    modelName,
    settings
  ) {

    const payload = {
      datasetSettings: datasetSettings,
      graphSettings: network,
      userEmail: userEmail,
      modelName: modelName,
      settings: settings,
      ttl: 60
    };
    return whenRenderingKernelReady
      .then(rk =>
        rk.post(
          `/inference/serving/${modelId}?training_session_id=${trainingSessionId}`,
          payload,
        ),
      )
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async isServedModelReady(servingSessionId) {
    return whenRenderingKernelReady
      .then(rk => rk.get(`/inference/serving/${servingSessionId}/status`))
      .then(res => {
        return res.data && res.data["url"];
      })
      .catch(err => {
        console.error(err);
        return null;
      });
  },

  async waitForServedModelReady(
    datasetSettings,
    userEmail,
    modelId,
    network,
    checkpointDirectory,
    modelName,
    settings,
  ) {
    const servingSessionId = await renderingKernel.serveModel(
      datasetSettings,
      userEmail,
      modelId,
      network,
      checkpointDirectory,
      modelName,
      settings
    );

    return await (async function() {
      let url = await renderingKernel.isServedModelReady(servingSessionId);

      while (!url) {
        await new Promise(resolve => {
          setTimeout(resolve, 1000);
        });
        url = await renderingKernel.isServedModelReady(servingSessionId);
      }
      return url;
    })();
  },

  async downloadFile(url) {
    return whenRenderingKernelReady
      .then(rk => rk.get(url, {responseType: 'arraybuffer'}))
      .then(res => {
        // Since the browser cannot download directly from the backend url
        const type = res.headers['content-type']
        const blob = new Blob([res.data], {type: type})
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = 'model.zip'
        link.click()    
      });    
  },  

  async getCode(network, modelId, layerId) {
    const payload = {
      graphSettings: network
    };
    return whenRenderingKernelReady
      .then(rk => rk.post(`/models/${modelId}/layers/${layerId}/code`, payload))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async getDataTypes(datasetId, userEmail) {
    return whenRenderingKernelReady
      .then(rk =>
        rk.get(
          `/datasets/type_inference?dataset_id=${datasetId}&user_email=${userEmail}`,
        ),
      )
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async getLayerInfoAll(modelId, network, datasetSettings, userEmail) {
    const payload = {
      graphSettings: network,
      datasetSettings: datasetSettings,
      userEmail: userEmail,
    };
    return whenRenderingKernelReady
      .then(rk => rk.post(`/models/${modelId}/layers/info`, payload))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async getLayerInfo(modelId, network, datasetSettings, layerId, userEmail) {
    const payload = {
      graphSettings: network,
      datasetSettings: datasetSettings,
      userEmail: userEmail,
    };
    return whenRenderingKernelReady
      .then(rk => rk.post(`/models/${modelId}/layers/${layerId}/info`, payload))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async getTrainingStatus(modelId, trainingSessionId) {
    return whenRenderingKernelReady
      .then(rk =>
        rk.get(`/models/${modelId}/training/${trainingSessionId}/status`),
      )
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async getTrainingResults(modelId, trainingSessionId, type, layerId, view) {
    let url = `/models/${modelId}/training/${trainingSessionId}/results?type=${type}`;

    if (layerId !== undefined) {
      url += `&layerId=${layerId}`;
    }
    if (view !== undefined) {
      url += `&view=${view}`;
    }

    return whenRenderingKernelReady
      .then(rk => rk.get(url))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async getPreviews(modelId, network, datasetSettings, userEmail) {
    const payload = {
      graphSettings: network,
      datasetSettings: datasetSettings,
      userEmail: userEmail,
    };
    return whenRenderingKernelReady
      .then(rk => rk.post(`/models/${modelId}/layers/previews`, payload))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async putData(datasetSettings, userEmail) {
    const payload = {
      datasetSettings: datasetSettings,
      userEmail: userEmail,
    };
    return whenRenderingKernelReady
      .then(rk => rk.put("/datasets/preprocessing", payload))
      .then(res => {
        return res.status === 200 ? res.data["preprocessingSessionId"] : null;
      });
  },

  async getVersion() {
    return whenRenderingKernelReady
      .then(rk => rk.get(`/version`))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async isDataReady(preprocessingSessionId, userEmail) {
    return whenRenderingKernelReady
    .then(rk => rk.get(`/datasets/preprocessing/${preprocessingSessionId}?user_email=${userEmail}`))
    .then(res => {
      return (res.status === 200) ? res.data : false;
    }).catch((err) => {
      console.error(err);
      return false;
    })
  },    
    
  async getModelRecommendation(projectId, datasetId, datasetSettings, userEmail, modelName, skippedWorkspace, modelPath) {
    const payload = {
      projectId: projectId,
      datasetId: datasetId,
      datasetSettings: datasetSettings,
      userEmail: userEmail,
      modelName: modelName,
      skippedWorkspace: skippedWorkspace,
      modelPath: modelPath
    };
    return whenRenderingKernelReady
      .then(rk => rk.post("/models/recommendations", payload))
      .then(res => {
        if (res.status === 200) {
          return res.data;
        }
        throw res.data;
      });
  },

  async waitForDataReady(datasetSettings, userEmail, cb, errCallback) {
    const preprocessingSessionId = await renderingKernel.putData(datasetSettings, userEmail);
        
    await (async function () {
      while(1) {
        const res = await renderingKernel.isDataReady(preprocessingSessionId, userEmail);
          if (res && res.is_complete) {
          break;
        }
        if (res && res.message && cb) {
          cb(res.message);
        }
        if (res && res.error && errCallback) {
          errCallback(res.error);
          break;
        }
        await new Promise(resolve => {
          setTimeout(resolve, 1000);
        });
      }
    })();
  },

  async startTraining(
    modelId,
    network,
    datasetSettings,
    trainingSettings,
    checkpointDirectory,
    loadCheckpoint,
    userEmail,
  ) {
    const payload = {
      graphSettings: network,
      datasetSettings: datasetSettings,
      trainingSettings: trainingSettings,
      checkpointDirectory: checkpointDirectory,
      loadCheckpoint: loadCheckpoint,
      userEmail: userEmail,
    };

    return whenRenderingKernelReady
      .then(rk => rk.post(`/models/${modelId}/training`, payload))
      .then(res => {
        if (res.status !== 200) {
          throw new Error("Failed to start training");
        }
      });
  },

  async pauseTraining(modelId, trainingSessionId) {
    return whenRenderingKernelReady
      .then(rk =>
        rk.put(`/models/${modelId}/training/${trainingSessionId}/pause`),
      )
      .then(res => {
        if (res.status !== 200) {
          throw new Error("Failed to pause training");
        }
      });
  },

  async unpauseTraining(modelId, trainingSessionId) {
    return whenRenderingKernelReady
      .then(rk =>
        rk.put(`/models/${modelId}/training/${trainingSessionId}/unpause`),
      )
      .then(res => {
        if (res.status !== 200) {
          throw new Error("Failed to unpause training");
        }
      });
  },

  async stopTraining(modelId, trainingSessionId) {
    return whenRenderingKernelReady
      .then(rk =>
        rk.put(`/models/${modelId}/training/${trainingSessionId}/stop`),
      )
      .then(res => {
        if (res.status !== 200) {
          throw new Error("Failed to stop training");
        }
      });
  },

  async set_user(userEmail) {
    const payload = {
      userEmail,
    };
    return whenRenderingKernelReady.then(rk => rk.post(`/user`, payload));
  },

  async startTesting(modelsInfo, tests, userEmail) {
    const payload = {
      modelsInfo: modelsInfo,
      tests: tests,
      userEmail: userEmail,
    };

    return whenRenderingKernelReady
      .then(rk => rk.post(`/inference/testing`, payload))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async getTestingStatus(testingSessionId) {
    return whenRenderingKernelReady
      .then(rk => rk.get(`/inference/testing/${testingSessionId}/status`))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async getTestingResults(testingSessionId) {
    return whenRenderingKernelReady
      .then(rk => rk.get(`/inference/testing/${testingSessionId}/results`))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },

  async importModel(archiveFilePath, projectId, datasetId, modelName, modelFilePath) {
    const payload = {
      archiveFilePath: archiveFilePath,      
      projectId: projectId,
      datasetId: datasetId,
      modelName: modelName,
      modelFilePath: modelFilePath,
    };
    return whenRenderingKernelReady
      .then(rk => rk.post("/models/import", payload))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },
};
