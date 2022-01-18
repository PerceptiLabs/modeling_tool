import axios from "axios";
import LogRocket from "logrocket";
import { RENDERING_KERNEL_BASE_URL } from "@/core/constants";
import { RENDERING_KERNEL_URL_CONFIG_PATH } from "@/core/constants";
import { LOCAL_STORAGE_CURRENT_USER } from "@/core/constants";
import { whenUrlIsResolved } from "@/core/urlResolver";

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
    const userToken = localStorage.getItem(LOCAL_STORAGE_CURRENT_USER);
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
      network: network,
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
    type,
    datasetSettings,
    userEmail,
    modelId,
    network,
    trainingSessionId,
    modelName,
  ) {
    const payload = {
      type: type,
      datasetSettings: datasetSettings,
      network: network,
      userEmail: userEmail,
      modelName: modelName,
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
    type,
    datasetSettings,
    userEmail,
    modelId,
    network,
    checkpointDirectory,
    modelName,
  ) {
    const servingSessionId = await renderingKernel.serveModel(
      type,
      datasetSettings,
      userEmail,
      modelId,
      network,
      checkpointDirectory,
      modelName,
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

  async getCode(network, modelId, layerId) {
    const payload = {
      network: network,
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
      network: network,
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
      network: network,
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
      network: network,
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
      .then(rk =>
        rk.get(
          `/datasets/preprocessing/${preprocessingSessionId}?user_email=${userEmail}`,
        ),
      )
      .then(res => {
        return res.status === 200 ? res.data : false;
      })
      .catch(err => {
        console.error(err);
        return false;
      });
  },

  async getModelRecommendation(
    datasetSettings,
    userEmail,
    modelId,
    skippedWorkspace,
  ) {
    const payload = {
      datasetSettings: datasetSettings,
      userEmail: userEmail,
      modelId: modelId,
      skippedWorkspace: skippedWorkspace,
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

  async waitForDataReady(datasetSettings, userEmail, cb) {
    const preprocessingSessionId = await renderingKernel.putData(
      datasetSettings,
      userEmail,
    );

    await (async function() {
      while (1) {
        const res = await renderingKernel.isDataReady(
          preprocessingSessionId,
          userEmail,
        );
        if (res && res.is_complete) {
          break;
        }
        if (res && res.message && cb) {
          cb(res.message);
        }
        await new Promise(resolve => {
          setTimeout(resolve, 1000);
        });
      }
    })();
  },

  async startTraining(
    modelId,
    trainingSessionId,
    network,
    datasetSettings,
    trainingSettings,
    checkpointDirectory,
    loadCheckpoint,
    userEmail,
  ) {
    const payload = {
      network: network,
      datasetSettings: datasetSettings,
      trainingSettings: trainingSettings,
      checkpointDirectory: checkpointDirectory,
      loadCheckpoint: loadCheckpoint,
      userEmail: userEmail,
    };

    return whenRenderingKernelReady
      .then(rk =>
        rk.post(`/models/${modelId}/training/${trainingSessionId}`, payload),
      )
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

  async importModel(datasetId, modelFilePath) {
    const payload = {
      datasetId: datasetId,
      modelFilePath: modelFilePath,
    };
    return whenRenderingKernelReady
      .then(rk => rk.post("/models/import", payload))
      .then(res => {
        return res.status === 200 ? res.data : null;
      });
  },
};
