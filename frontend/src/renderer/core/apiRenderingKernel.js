import axios            from 'axios'
// import { objectToQueryParams } from '@/core/helpers'
// import { stringifyNetworkObjects }   from "@/core/helpers.js";

import { RENDERING_KERNEL_BASE_URL } from '@/core/constants'
import { RENDERING_KERNEL_URL_CONFIG_PATH }   from "@/core/constants";
import { whenUrlIsResolved } from '@/core/urlResolver';

const whenRenderingKernelReady = whenUrlIsResolved(RENDERING_KERNEL_URL_CONFIG_PATH, RENDERING_KERNEL_BASE_URL)
  .then(url => {
    let ret = axios.create();
    ret.defaults.baseURL = url
    ret.defaults.headers.common["Content-Type"] = `application/json`;
    ret.defaults.params = {}
    return ret
  });

export const renderingKernel = {

  async hasCheckpoint(directory) {
    return whenRenderingKernelReady     
      .then(rk => rk.get(`/has_checkpoint?directory=${directory}`))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async exportModel(exportSettings, datasetSettings, userEmail, modelId, network, checkpointDirectory) {
    const payload = {
      exportSettings: exportSettings,
      datasetSettings: datasetSettings,
      network: network,
      checkpointDirectory: checkpointDirectory, 
      userEmail: userEmail,
      modelId: modelId,
    };
    return whenRenderingKernelReady
      .then(rk => rk.post('/export', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async serveModel(type, datasetSettings, userEmail, modelId, network, checkpointDirectory, modelName) {
    const payload = {
      type: type,
      payload: {
        datasetSettings: datasetSettings,
        network: network,
        checkpointDirectory: checkpointDirectory,
	userEmail: userEmail,
	modelName: modelName
      },
      userEmail: userEmail,
      modelId: modelId,
    };
    return whenRenderingKernelReady
      .then(rk => rk.post('/serving/start', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async isServedModelReady(modelId, userEmail) {
    return whenRenderingKernelReady
    .then(rk => rk.get(`/serving/model?model_id=${modelId}&user_email=${userEmail}`))
    .then(res => {
      return res.data;
    }).catch((err) => {
      console.error(err);
      return null;
    })
  },

  async waitForServedModelReady(type, datasetSettings, userEmail, modelId, network, checkpointDirectory, modelName) {
    await renderingKernel.serveModel(type, datasetSettings, userEmail, modelId, network, checkpointDirectory, modelName);
	
    return await (async function () {
      let url = await renderingKernel.isServedModelReady(modelId, userEmail);
      
      while(!url) {
        await new Promise(resolve => {
          setTimeout(resolve, 1000);
        });
	url = await renderingKernel.isServedModelReady(modelId, userEmail);
      }
      return url      
    })();
  },

  async getCode(network, layerId) {
    const payload = {
      network: network,
      layer_id: layerId
    };
    return whenRenderingKernelReady
      .then(rk => rk.post('/layer_code', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },
 
  async getDataTypes(path, userEmail) {
    return whenRenderingKernelReady
      .then(rk => rk.get(`/type_inference?path=${path}&user_email=${userEmail}`))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async getPreviews(network, datasetSettings, userEmail) {
    const payload = {
      network: network,
      datasetSettings: datasetSettings,
      userEmail: userEmail	
    };
    return whenRenderingKernelReady
      .then(rk => rk.post('/previews', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async getPreview(network, datasetSettings, layerId, userEmail) {
    const payload = {
      network: network,
      datasetSettings: datasetSettings,
      userEmail: userEmail	
    };
    return whenRenderingKernelReady
      .then(rk => rk.post(`/previews/${layerId}`, payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async getNetworkData(network, datasetSettings, userEmail) {
    // overlaps with getPreviews, but will eventually get deprecated
    const payload = {
      network: network,
      datasetSettings: datasetSettings,
      userEmail: userEmail	
    };
    return whenRenderingKernelReady
      .then(rk => rk.post('/network_data', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async putData(datasetSettings, userEmail) {
    const payload = {
      datasetSettings: datasetSettings,
      userEmail: userEmail	
    };
    return whenRenderingKernelReady
      .then(rk => rk.put('/data', payload))
      .then(res => {
        return (res.status === 200) ? res.data["datasetHash"] : null;
      })
  }, 
     
  async getVersion() {
    return whenRenderingKernelReady
      .then(rk => rk.get(`/version`))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async isDataReady(datasetHash, userEmail) {
    return whenRenderingKernelReady
    .then(rk => rk.get(`/data?dataset_hash=${datasetHash}&user_email=${userEmail}`))
    .then(res => {
      return (res.status === 200);
    }).catch((err) => {
      console.error(err);
      return false;
    })
  },    
    
  async getModelRecommendation(datasetSettings, userEmail, modelId, skippedWorkspace) {
    const payload = {
      datasetSettings: datasetSettings,
      user_email: userEmail,
      model_id: modelId,
      skipped_workspace: skippedWorkspace
    };
    return whenRenderingKernelReady
      .then(rk => rk.post('/model_recommendations', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },
  
  async waitForDataReady(datasetSettings, userEmail) {
    const datasetHash = await renderingKernel.putData(datasetSettings, userEmail);
	
    await (async function () {
      while(!await renderingKernel.isDataReady(datasetHash, userEmail)) {
        await new Promise(resolve => {
          setTimeout(resolve, 1000);
        });
      }
    })();
  },

  async startSession(payload) {
    return whenRenderingKernelReady
      .then(rk => rk.post('/session/start', payload))
      .then(res => {
        if (res.status !== 200) {
          throw new Error('Failed to start session');
        }
      })
  },

  async getTrainingUrl(receiver, userEmail) {
    return whenRenderingKernelReady
      .then(rk => rk.get(`/session/url?receiver=${receiver}&user_email=${userEmail}`))
      .then(res => {
        return (res.status === 200) ? res.data["url"] : null;
      })
  },

  async sessionProxy(action, receiver, userEmail, data) {
    const payload = {
      action: action,
      receiver: receiver,
      user_email: userEmail,
      data: data
    };
    return whenRenderingKernelReady
      .then(rk => rk.post('/session/proxy', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },
  async set_user(userEmail) {
    const payload = {
      userEmail,
    };
    return whenRenderingKernelReady
      .then(rk => rk.post(`/set_user`, payload));
  },
}


