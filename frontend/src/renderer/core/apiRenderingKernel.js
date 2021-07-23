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

  async getNetworkData(network, datasetSettings) {
    const payload = {
      network: network,
      datasetSettings: datasetSettings
    };
    return whenRenderingKernelReady
      .then(rk => rk.post('/network_data', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async putData(datasetSettings) {
    const payload = {
      datasetSettings: datasetSettings
    };
    return whenRenderingKernelReady
      .then(rk => rk.put('/data', payload))
      .then(res => {
        return (res.status === 200) ? res.data : null;
      })
  },

  async putData(datasetSettings) {
    const payload = {
      datasetSettings: datasetSettings
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

  async isDataReady(datasetHash) {
    return whenRenderingKernelReady
    .then(rk => rk.get(`/data?dataset_hash=${datasetHash}`))
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


}

