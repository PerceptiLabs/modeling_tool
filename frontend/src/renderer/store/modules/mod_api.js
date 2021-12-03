import { coreRequest } from "@/core/apiWeb.js";
import { renderingKernel } from "@/core/apiRenderingKernel.js";
import {
  deepCopy,
  parseJWT,
  isWeb,
  isEnvDataWizardEnabled,
  checkpointDirFromProject,
} from "@/core/helpers.js";
import { createNotebookJson } from "@/core/helpers/notebook-helper.js";
import { pathSlash, sessionStorageInstanceIdKey } from "@/core/constants.js";
import { createCoreNetwork } from "@/core/helpers";
import {
  getModelJson as rygg_getModelJson,
  doesDirExist as rygg_doesDirExist,
} from "@/core/apiRygg";
import cloneDeep from "lodash.clonedeep";
import { v4 as uuidv4 } from "uuid";
import router from "@/router";
import base64url from "base64url";

const namespaced = true;
//let pauseAction = 'Pause';

const state = {
  instanceId: null,
  statusLocalCore: "offline", //online
  headlessState: [],
  coreVersions: null,
};

const getters = {
  GET_coreNetworkElementList(state, getters, rootState, rootGetters) {
    return rootGetters["mod_workspace/GET_currentNetworkElementList"];
  },
  GET_coreNetworkId(state, getters, rootState, rootGetters) {
    return rootGetters["mod_workspace/GET_currentNetworkId"];
  },
  GET_coreNetwork(state, getters, rootState, rootGetters) {
    const network = rootGetters["mod_workspace/GET_currentNetwork"];
    let layers = {};
    const rootPath = network.networkRootFolder;
    for (let layer in network.networkElementList) {
      const el = network.networkElementList[layer];
      if (el.componentName === "LayerContainer") continue;

      /*prepare checkpoint*/
      const checkpointPath = {
        load_checkpoint:
          rootGetters["mod_workspace/GET_currentNetworkModeWeightsState"],
        path: "",
      };

      if (el.checkpoint.length >= 2) {
        checkpointPath.path = el.checkpoint[1];

        if (checkpointPath.path.slice(-1) !== "/") {
          checkpointPath.path += "/";
        } else if (checkpointPath.path.slice(-1) !== "\\") {
          checkpointPath.path += "\\";
        }

        checkpointPath.path += "checkpoint";
      } else {
        checkpointPath.path = network.apiMeta.location + "/checkpoint";
      }

      // const namesConnectionOut = [];
      // const namesConnectionIn = [];

      // el.connectionOut.forEach(id => {
      //   const name =  network.networkElementList[id].layerName;
      //   namesConnectionOut.push([id, name])
      // });

      // el.connectionIn.forEach(id => {
      //   const name =  network.networkElementList[id].layerName;
      //   namesConnectionIn.push([id, name])
      // });

      /*prepare elements*/
      layers[el.layerId] = {
        Name: el.layerName,
        Type: el.componentName,
        checkpoint: checkpointPath,
        endPoints: el.endPoints,
        Properties: el.layerSettings,
        Code: el.layerCode,
        backward_connections: el.backward_connections,
        forward_connections: el.forward_connections,
        visited: el.visited,
        previewVariable: el.previewVariable,
      };
    }
    return layers;
  },
  GET_networkNameById: (state, getters, rootState, rootGetters) => id => {
    const network = rootGetters["mod_workspace/GET_networkByNetworkId"](id);
    return network.networkName;
  },
  GET_coreNetworkById: (state, getters, rootState, rootGetters) => id => {
    const network = rootGetters["mod_workspace/GET_networkByNetworkId"](id);
    let layers = {};

    for (let layer in network.networkElementList) {
      const el = network.networkElementList[layer];
      if (el.componentName === "LayerContainer") continue;

      /*prepare checkpoint*/
      const checkpointPath = {
        load_checkpoint: rootGetters[
          "mod_workspace/GET_currentNetworkModeWeightsStateById"
        ](id),
        path: "",
      };

      if (el.checkpoint.length >= 2) {
        checkpointPath.path = el.checkpoint[1];

        if (checkpointPath.path.slice(-1) !== "/") {
          checkpointPath.path += "/";
        } else if (checkpointPath.path.slice(-1) !== "\\") {
          checkpointPath.path += "\\";
        }

        checkpointPath.path += "checkpoint";
      } else {
        checkpointPath.path = network.apiMeta.location + "/checkpoint";
      }

      /*prepare elements*/
      layers[el.layerId] = {
        Name: el.layerName,
        Type: el.componentName,
        checkpoint: checkpointPath,
        endPoints: el.endPoints,
        Properties: el.layerSettings,
        Code: el.layerCode,
        backward_connections: el.backward_connections,
        forward_connections: el.forward_connections,
        visited: el.visited,
        previewVariable: el.previewVariable,
      };
    }
    return layers;
  },
  GET_coreNetworkWithCheckpointConfig: (
    state,
    getters,
    rootState,
    rootGetters,
  ) => (loadCheckpoint = false) => {
    const network = rootGetters["mod_workspace/GET_currentNetwork"];
    let layers = {};
    const rootPath = network.networkRootFolder;
    for (let layer in network.networkElementList) {
      const el = network.networkElementList[layer];
      if (el.componentName === "LayerContainer") continue;

      /*prepare checkpoint*/
      const checkpointPath = {
        load_checkpoint: loadCheckpoint,
        path: "",
      };

      if (el.checkpoint.length >= 2) {
        checkpointPath.path = el.checkpoint[1];

        if (checkpointPath.path.slice(-1) !== "/") {
          checkpointPath.path += "/";
        } else if (checkpointPath.path.slice(-1) !== "\\") {
          checkpointPath.path += "\\";
        }

        checkpointPath.path += "checkpoint";
      } else {
        checkpointPath.path = network.apiMeta.location + "/checkpoint";
      }

      /*prepare elements*/
      layers[el.layerId] = {
        Name: el.layerName,
        Type: el.componentName,
        checkpoint: checkpointPath,
        endPoints: el.endPoints,
        Properties: el.layerSettings,
        Code: el.layerCode,
        backward_connections: el.backward_connections,
        forward_connections: el.forward_connections,
        visited: el.visited,
        previewVariable: el.previewVariable,
      };
    }
    return layers;
  },
  get_headlessState: state => networkId => {
    const headlessState = state.headlessState.find(hs => hs.id === networkId);

    if (!headlessState) {
      return;
    }

    return headlessState.isHeadless;
  },
  // maybe another flag for within or not alayerId
  GET_descendentsIds: (state, getters) => (pivotLayer, withPivot = true) => {
    const networkList = getters.GET_coreNetworkElementList;
    let listIds = getDescendants(pivotLayer, []);
    if (withPivot) {
      listIds.push(pivotLayer.layerId);
    }
    return listIds;
    function getDescendants(networkElement, dataIds) {
      if (networkElement.forward_connections.length === 0) {
        return dataIds;
      }
      for (let index in networkElement.forward_connections) {
        const layerId = networkElement.forward_connections[index].dst_id;
        dataIds.push(layerId);
        getDescendants(networkList[layerId], dataIds);
      }
      return dataIds;
    }
  },
};

const mutations = {
  SET_statusLocalCore(state, value) {
    state.statusLocalCore = value;
  },
  set_headlessState(state, { id, value }) {
    const headlessState = state.headlessState.find(hs => hs.id === id);

    if (!headlessState) {
      state.headlessState.push({
        id: id,
        isHeadless: value,
      });
    } else {
      headlessState.isHeadless = value;
    }
  },
  API_setAppInstanceMutation(state, payload) {
    state.instanceId = payload;
  },
  SET_coreVersions(state, value) {
    state.coreVersions = value;
  },
};

const actions = {
  //---------------
  //  CORE
  //---------------
  checkCoreAvailability({ commit, dispatch, state }) {
    console.error("checkCoreAvailability is deprecated!");
  },
  checkCoreVersions({ commit, dispatch, state }) {
    const theData = {
      action: "version",
      value: "",
    };
    return renderingKernel
      .getVersion()
      .then(versions => {
        commit("SET_coreVersions", {
          python: versions.python
            .split(".")
            .slice(0, 2)
            .join("."),
          tensorflow: versions.tensorflow,
        });
        if (state.statusLocalCore !== "online") {
          commit("SET_statusLocalCore", "online");
        }
      })
      .catch(() => {
        if (state.statusLocalCore === "online") {
          commit("SET_statusLocalCore", "offline");
        }
      });
  },

  API_closeCore(context, receiver) {
    const theData = {
      receiver: receiver,
      action: "closeCore",
      value: "",
    };
    coreRequest(theData)
      .then(data => {
        return;
      })
      .catch(err => {
        console.error(err);
      });
  },

  API_CLOSE_core() {
    const theData = {
      receiver: "server",
      action: "Close",
      value: "",
    };
    coreRequest(theData)
      .then(data => {
        return;
      })
      .catch(err => {
        console.error(err);
      });
  },
  //---------------
  //  NETWORK TRAINING
  //---------------
  API_testStart({ dispatch, getters, rootGetters, commit }, payload) {
    const { modelIds, checkpoint_paths } = payload;

    let models = {};

    modelIds.forEach(id => {
      const network = rootGetters["mod_workspace/GET_networkByNetworkId"](id);

      models[id] = {};
      models[id].layers = getters.GET_coreNetworkById(id);
      models[id].model_name = network.networkName;
      models[id].training_session_id = base64url(checkpoint_paths[id]);
      models[id].datasetSettings = network.networkMeta.datasetSettings;
      models[id].data_path = payload.dataPath;
    });

    const userEmail = rootGetters["mod_user/GET_userEmail"];

    return renderingKernel
      .startTesting(models, payload.testTypes, userEmail)
      .then(data => {
        dispatch("mod_test/testStart", data, { root: true });
      })
      .catch(err => {
        console.error(err);
      });
  },
  API_testStop({ dispatch }) {
    const theData = {
      receiver: "test_requests",
      action: "StopTests",
    };
    dispatch("mod_test/setTestMessage", ["Stopping Tests..."], { root: true });
    return coreRequest(theData)
      .then(() => {
        dispatch("mod_test/testFinish", null, { root: true });
      })
      .catch(err => {
        console.error(err);
      });
  },
  API_closeTest({ dispatch }) {
    const theData = {
      receiver: "test_requests",
      action: "CloseTests",
    };
    dispatch("mod_test/setTestMessage", ["Stopping Tests..."], { root: true });
    return coreRequest(theData)
      .then(() => {
        dispatch("mod_test/testFinish", null, { root: true });
      })
      .catch(err => {
        console.error(err);
      });
  },
  API_getTestStatus({ dispatch, getters, rootGetters }) {
    const sessionId = rootGetters["mod_test/GET_testSessionId"];
    /*if(!sessionId) { 
      setTimeout(() => {
        dispatch('API_getTestStatus');
      }, 1000);
      return
    }*/

    let startTime = new Date().getTime();

    return renderingKernel
      .getTestingStatus(sessionId)
      .then(data => {
        if (!data) {
          setTimeout(() => {
            dispatch("API_getTestStatus");
          }, 1000);
          return;
        }
        let endTime = new Date().getTime();
        const responseDuration = endTime - startTime;
        const delay = responseDuration >= 1000 ? 0 : 1000 - responseDuration;
        if (data.status === "Completed") {
          dispatch("API_getTestResults");
        } else if (data.error) {
          dispatch("API_closeTest");
          dispatch(
            "globalView/GP_errorPopup",
            data.error.message + "\n\n" + data.error.details,
            { root: true },
          );
        } else {
          setTimeout(() => {
            dispatch("API_getTestStatus");
          }, delay);
          dispatch(
            "mod_test/setTestMessage",
            [data.update_line_1, data.update_line_2],
            { root: true },
          );
        }
      })
      .catch(err => {
        console.error(err);
      });
  },
  API_getTestResults({ dispatch, getters, rootGetters }) {
    const sessionId = rootGetters["mod_test/GET_testSessionId"];

    return renderingKernel
      .getTestingResults(sessionId)
      .then(data => {
        //
        if (typeof data === "string") {
          data = JSON.parse(data.replace(/NaN/g, "0"));
        }
        console.log("data", data);
        dispatch("API_closeTest");
        dispatch("mod_test/setTestData", data, { root: true });
        dispatch("mod_test/setTestMessage", null, { root: true });
      })
      .catch(err => {
        console.error(err);
      });
  },

  API_startTraining(
    { dispatch, getters, rootGetters },
    { loadCheckpoint = false } = {},
  ) {
    const modelId = rootGetters["mod_workspace/GET_currentNetworkId"];
    const network = getters.GET_coreNetworkWithCheckpointConfig(loadCheckpoint);
    const datasetSettings =
      rootGetters["mod_workspace/GET_currentNetworkDatasetSettings"];
    const userEmail = rootGetters["mod_user/GET_userEmail"];
    const trainingSettings =
      rootGetters["mod_workspace/GET_modelTrainingSetting"];
    const checkpointDirectory =
      rootGetters["mod_workspace/GET_currentNetworkCheckpointDirectory"];
    const trainingSessionId = base64url(checkpointDirectory);

    const trackingData = {
      modelId: modelId,
      userEmail: userEmail,
    };
    return renderingKernel
      .startTraining(
        modelId,
        trainingSessionId,
        network,
        datasetSettings,
        trainingSettings,
        checkpointDirectory,
        loadCheckpoint,
        userEmail,
      )
      .then(() => {
        dispatch("mod_workspace/EVENT_startDoRequest", true, { root: true });
        dispatch("mod_tracker/EVENT_trainingStart", trackingData, {
          root: true,
        });
        setTimeout(
          () =>
            dispatch("mod_workspace/EVENT_chartsRequest", null, { root: true }),
          500,
        );
      })
      .catch(err => {
        dispatch("mod_workspace/SET_statusNetworkCoreStatus", "Failed", {
          root: true,
        });
        console.error(err);
      });
  },

  API_pauseTraining({ dispatch, rootGetters }) {
    const modelId = rootGetters["mod_workspace/GET_currentNetworkId"];
    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](modelId);
    const trainingSessionId = base64url(checkpointDirectory);

    renderingKernel
      .pauseTraining(modelId, trainingSessionId)
      .then(() => {
        dispatch(
          "mod_workspace/SET_statusNetworkCoreDynamically",
          {
            modelId: modelId,
            Status: "Pausing",
          },
          { root: true },
        );
      })
      .catch(err => {
        console.error(err);
      });
  },
  API_unpauseTraining({ dispatch, rootGetters }) {
    const modelId = rootGetters["mod_workspace/GET_currentNetworkId"];
    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](modelId);
    const trainingSessionId = base64url(checkpointDirectory);

    renderingKernel
      .unpauseTraining(modelId, trainingSessionId)
      .then(data => {
        dispatch("mod_workspace/EVENT_startDoRequest", true, { root: true });
        dispatch(
          "mod_workspace/SET_statusNetworkCoreDynamically",
          {
            modelId: modelId,
            Status: "Resuming",
          },
          { root: true },
        );
      })
      .catch(err => {
        console.error(err);
      });
  },
  API_stopTraining({ dispatch, rootGetters }, receiver = null) {
    const modelId =
      receiver || rootGetters["mod_workspace/GET_currentNetworkId"];
    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](modelId);
    const trainingSessionId = base64url(checkpointDirectory);

    renderingKernel
      .stopTraining(modelId, trainingSessionId)
      .then(data => {
        dispatch("mod_workspace/saveCurrentModelAction", null, { root: true });
        dispatch("mod_tracker/EVENT_trainingCompleted", "User stopped", {
          root: true,
        });
        dispatch(
          "mod_workspace/SET_statusNetworkCoreDynamically",
          {
            modelId: modelId,
            Status: "Stopping",
          },
          { root: true },
        );
      })
      .catch(err => {
        console.error(err);
      });
  },

  API_skipValidTraining({ rootGetters }) {
    const theData = {
      receiver: rootGetters["mod_workspace/GET_currentNetworkId"],
      action: "SkipToValidation",
      value: "",
    };
    coreRequest(theData)
      .then(data => {})
      .catch(err => {
        console.error(err);
      });
  },

  API_getResultInfo({ rootGetters }) {
    const networkId = rootGetters["mod_workspace/GET_currentNetworkId"]; // Shouldn't it be current network for GET_currentNetworkIdForKernelRequests?
    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](networkId);
    const trainingSessionId = base64url(checkpointDirectory);

    //console.log('API_getResultInfo', theData);
    return renderingKernel
      .getTrainingResults(networkId, trainingSessionId, "end-results")
      .then(data => data)
      .catch(err => {
        console.error(err);
      });
  },

  //---------------
  //  NETWORK TESTING
  //---------------
  API_postTestStart({ rootGetters, dispatch }) {
    const theData = {
      receiver: rootGetters["mod_workspace/GET_currentNetworkId"],
      action: "startTest",
      value: "",
    };
    return coreRequest(theData)
      .then(data => {
        dispatch("mod_tracker/EVENT_testOpenTab", null, { root: true });
      })
      .catch(err => {
        console.error(err);
      });
  },

  API_checkNetworkRunning({ rootGetters }, receiver) {
    const modelId =
      receiver || rootGetters["mod_workspace/GET_currentNetworkId"];
    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](modelId);
    const trainingSessionId = base64url(checkpointDirectory);

    return renderingKernel
      .getTrainingStatus(modelId, trainingSessionId)
      .then(data => {
        const hasResults = Object.keys(data).length > 0;
        return { content: hasResults };
      });
  },

  API_checkTrainedNetwork({ rootGetters }, receiver = null) {
    const modelId =
      receiver || rootGetters["mod_workspace/GET_currentNetworkId"];
    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](modelId);
    const trainingSessionId = base64url(checkpointDirectory);

    return renderingKernel
      .getTrainingStatus(modelId, trainingSessionId)
      .then(data => {
        const hasResults = Object.keys(data).length > 0;
        return { result: hasResults, receiver: receiver }; // For some reason, this method needs to return the receiver...
      });
  },

  API_saveTrainedNetwork(
    { dispatch, getters, rootGetters },
    { Location, frontendNetwork, networkName },
  ) {
    console.error("API_saveTrainedNetwork is deprecated!");
  },

  //---------------
  //  ELEMENT SETTINGS
  //---------------
  API_getInputDim({ dispatch, getters, rootGetters }) {
    const net = getters.GET_coreNetwork;
    const datasetSettings =
      rootGetters["mod_workspace/GET_currentNetworkDatasetSettings"];
    const userEmail = rootGetters["mod_user/GET_userEmail"];
    const modelId = rootGetters["mod_workspace/GET_currentNetworkId"];

    return renderingKernel
      .getLayerInfoAll(modelId, net, datasetSettings, userEmail)
      .then(data => {
        if (data.error) {
          dispatch(
            "globalView/GP_errorPopup",
            res.error.message + "\n\n" + res.error.details,
            { root: true },
          );
        }

        if (data)
          return dispatch("mod_workspace/SET_elementInputDim", data, {
            root: true,
          });
      })
      .catch(err => {
        console.error(err);
      });
  },

  API_getOutputDim({ dispatch, getters, rootGetters }) {
    console.error("API_getOutputDim is deprecated!");
  },

  API_getPreviewSample(
    { dispatch, getters, rootGetters },
    { layerId, varData },
  ) {
    console.error("API_getPreviewSample is deprecated!");
  },

  API_getPreviewVariableList({ dispatch, getters, rootGetters }, layerId) {
    const net = getters.GET_coreNetwork;
    const datasetSettings =
      rootGetters["mod_workspace/GET_currentNetworkDatasetSettings"];
    const userEmail = rootGetters["mod_user/GET_userEmail"];

    // console.log('getPreviewVariableList Request', theData);
    return renderingKernel
      .getLayerInfo(net, datasetSettings, layerId, userEmail)
      .then(data => {
        return data;
      })
      .catch(err => {
        console.error(err);
      });
  },

  API_getCode({ dispatch, getters, rootGetters }, { layerId, settings }) {
    const net = getters.GET_coreNetwork;
    const modelId = getters.GET_coreNetworkId;
    if (settings) net[layerId].Properties = settings;

    // console.log('getCode - layerId', layerId);
    return renderingKernel
      .getCode(net, modelId, layerId)
      .then(data => {
        // console.log('getCode - response', data);
        // console.log('getCode - layerId', layerId);
        return data;
      })
      .catch(err => {
        console.log("API_getCode error");
        console.error(err);
      });
  },

  API_getGraphOrder({ rootGetters }, jsonNetwork) {
    console.error("API_getGraphOrder is deprecated!");
  },

  API_getNotebookImports({ rootGetters }, jsonNetwork) {
    console.error("API_getNotebookImports is deprecated!");
  },

  API_getNotebookRunscript({ rootGetters }, jsonNetwork) {
    console.error("API_getNotebookRunscript is deprecated!");
  },

  API_getPartitionSummary({ getters, rootGetters }, { layerId, settings }) {
    console.error("API_getPartitionSummary is deprecated!");
  },

  API_getDataMeta({ getters, rootGetters }, { layerId, settings }) {
    console.error("API_getDataMeta is deprecated!");
  },
  //---------------
  //  IMPORT/EXPORT
  //---------------
  API_parse({ dispatch, getters, rootState, rootGetters }, path) {
    console.error("API_parse is deprecated!");
  },

  async API_exportData({ rootGetters, getters, dispatch }, settings) {
    const userEmail = rootGetters["mod_user/GET_userEmail"];
    const modelId = settings.modelId;
    const datasetSettings = rootGetters[
      "mod_workspace/GET_currentNetworkDatasetSettingsByModelId"
    ](settings.modelId);

    async function exportClosure() {
      const network = getters.GET_coreNetworkById(settings.modelId);
      const networkName = getters.GET_networkNameById(modelId);
      const checkpointDirectory = rootGetters[
        "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
      ](settings.modelId);
      const trainingSessionId = base64url(checkpointDirectory);

      if (settings.Type != "Serve Gradio") {
        // TODO: serving TEMPORARILY falls under export
        return renderingKernel.exportModel(
          settings,
          datasetSettings,
          userEmail,
          modelId,
          network,
          trainingSessionId,
        );
      } else {
        const url = renderingKernel.waitForServedModelReady(
          "gradio",
          datasetSettings,
          userEmail,
          modelId,
          network,
          trainingSessionId,
          networkName,
        );
        return url;
      }
    }

    const trackerData = {
      result: "",
      network: getters.GET_coreNetworkById(settings.modelId),
      settings,
    };

    return exportClosure()
      .then(data => {
        // dispatch('globalView/GP_infoPopup', data, {root: true});
        trackerData.result = "success";
        return Promise.resolve(data);
      })
      .catch(err => {
        console.error(err);
        dispatch("globalView/GP_errorPopup", err, { root: true });
        trackerData.result = "error";
        return Promise.reject(err);
      })
      .finally(() => {
        dispatch("mod_tracker/EVENT_modelExport", trackerData, { root: true });
      });
  },
  //---------------
  //  OTHER
  //---------------
  API_getStatus({ rootGetters, rootState, dispatch, commit }, payload) {
    const networkId =
      payload && payload.networkIndex !== undefined
        ? rootState.mod_workspace.workspaceContent[payload.networkIndex]
            .networkID
        : rootGetters["mod_workspace/GET_currentNetworkIdForKernelRequests"];
    const network = rootGetters["mod_workspace/GET_networkByNetworkId"](
      networkId,
    );

    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](networkId);

    const trainingSessionId = base64url(checkpointDirectory);
    renderingKernel
      .getTrainingStatus(networkId, trainingSessionId)
      .then(data => {
        if (!data) return;

        if (
          network.networkMeta &&
          network.networkMeta.coreStatus &&
          !data.error &&
          data.Status !== "Finished" &&
          ((data.Status !== "Paused" &&
            network.networkMeta.coreStatus.Status === "Pausing") ||
            (data.Status !== "Stopped" &&
              network.networkMeta.coreStatus.Status === "Stopping") ||
            (data.Status === "Paused" &&
              network.networkMeta.coreStatus.Status === "Resuming"))
        ) {
          data.Status = network.networkMeta.coreStatus.Status;
        }

        dispatch(
          "mod_workspace/SET_statusNetworkCoreDynamically",
          { modelId: networkId, ...data },
          { root: true },
        );

        if (data.error) {
          dispatch("mod_workspace/EVENT_startDoRequest", false, { root: true });
          commit("mod_empty-navigation/set_emptyScreenMode", 0, { root: true });
          dispatch("mod_workspace/setViewType", "model", { root: true });
          dispatch(
            "mod_workspace/SET_statisticsAndTestToClosed",
            { networkId: networkId },
            { root: true },
          );
          dispatch(
            "globalView/GP_errorPopup",
            data.error.message + "\n\n" + data.error.details,
            { root: true },
          );
        }

        // Do not update status when the coreStatus is stopped or paused
        if (
          data.Status === "Paused" ||
          data.Status === "Finished" ||
          data.Status === "Stopped"
        ) {
          dispatch(
            "mod_workspace/EVENT_stopRequest",
            { networkId },
            { root: true },
          );
        }
      })
      .catch(err => {
        if (!err.toString().match(/Error: connect ECONNREFUSED/)) {
          console.error(err);
        }
      });
  },
  API_getModelStatus({ rootGetters, dispatch, commit }, modelId) {
    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](modelId);

    const trainingSessionId = base64url(checkpointDirectory);
    renderingKernel
      .getTrainingStatus(modelId, trainingSessionId)
      .then(data => {
        dispatch(
          "mod_workspace/SET_statusNetworkCoreDynamically",
          {
            ...data,
            modelId: modelId,
          },
          { root: true },
        );

        if (data && data.Status === "Finished") {
          dispatch(
            "mod_workspace/EVENT_stopRequest",
            { networkId: modelId },
            { root: true },
          );
        }
      })
      .catch(err => {
        if (!err.toString().match(/Error: connect ECONNREFUSED/)) {
          console.error(err);
        }
      });
  },

  API_setHeadless({ commit, getters, rootGetters }, value) {
    // Checking headless state and only sending if:
    // - different or
    // - never sent before

    // This is because the Kernel can current not handle a request
    // that sets the same state (i.e. true -> true).

    console.error("API_setHeadless is deprecated!");
  },

  API_updateResults({ rootGetters, dispatch, commit, rootState }, payload) {
    const networkId =
      payload && payload.networkIndex !== undefined
        ? rootState.mod_workspace.workspaceContent[payload.networkIndex]
            .networkID
        : rootGetters["mod_workspace/GET_currentNetworkIdForKernelRequests"];

    const checkpointDirectory = rootGetters[
      "mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId"
    ](networkId);

    const theData = {
      receiver: networkId,
      action: "updateResults",
      value: {
        trainingSessionId: base64url(checkpointDirectory),
      },
    };
    return coreRequest(theData)
      .then(data => {
        return data;
      })
      .catch(err => {
        // if error stop update results req
        dispatch("mod_workspace/EVENT_startDoRequest", false, { root: true });
        commit("mod_empty-navigation/set_emptyScreenMode", 0, { root: true });
        dispatch("mod_workspace/setViewType", "model", { root: true });
        dispatch(
          "mod_workspace/SET_statisticsAndTestToClosed",
          {
            networkId:
              rootGetters["mod_workspace/GET_currentNetwork"].networkID,
          },
          { root: true },
        );
        dispatch("globalView/GP_errorPopup", err.response.data, { root: true });
      });
  },

  API_setUserInCore({}) {
    console.error("API_setUserInCore is deprecated!");
  },
  // @param {object} payload | { networkId: variableName }
  API_getBatchPreviewSample({ getters, dispatch, rootGetters }, payload) {
    if (!payload) {
      payload = {};
    }

    const networkList = getters.GET_coreNetworkElementList;
    const networkId = rootGetters["mod_workspace/GET_currentNetworkId"];
    const userEmail = rootGetters["mod_user/GET_userEmail"];
    let net = cloneDeep(getters.GET_coreNetwork);
    for (let elId in payload) {
      net[elId]["getPreview"] = payload[elId] !== undefined;
    }
    const datasetSettings =
      rootGetters["mod_workspace/GET_currentNetworkDatasetSettings"];

    // console.log(
    //   'API_getBatchPreviewSample req',
    //   theData
    // );

    dispatch(
      "mod_workspace/setChartComponentLoadingState",
      { descendants: Object.keys(payload), value: true, networkId },
      { root: true },
    );

    return renderingKernel
      .getPreviews(networkId, net, datasetSettings, userEmail)
      .then(res => {
        // console.group('getNetworkData');
        // console.log(
        //   'API_getBatchPreviewSample res',
        //   theData,
        //   res
        // );
        // console.log('previews', res.previews);
        // console.groupEnd();
        if (res.error) {
          dispatch(
            "globalView/GP_errorPopup",
            res.error.message + "\n\n" + res.error.details,
            { root: true },
          );
        }

        if (res.newNetwork && Object.keys(res.newNetwork).length > 0) {
          for (let ix in res.newNetwork) {
            const currentEl = networkList[ix];
            const saveSettings = {
              elId: ix,
              set: res.newNetwork[ix].Properties,
              code: { Output: res.newNetwork[ix].Code },
              tabName: currentEl.layerSettingsTabName,
              visited: res.newNetwork[ix].visited,
            };
            dispatch(
              "mod_workspace/SET_elementSettings",
              { settings: deepCopy(saveSettings) },
              { root: true },
            );
          }
        }
        if (res.outputDims) {
          dispatch("mod_workspace/SET_elementOutputDim", res.outputDims, {
            root: true,
          });
          dispatch(
            "mod_workspace-notifications/setNotifications",
            {
              networkId: rootGetters["mod_workspace/GET_currentNetworkId"],
              kernelResponses: res.outputDims,
            },
            { root: true },
          );
        }

        if (res.previews && Object.keys(res.previews).length > 0) {
          Object.keys(res.previews).map(previewKey => {
            dispatch(
              "mod_workspace/SET_NetworkChartData",
              {
                layerId: previewKey,
                payload: res.previews[previewKey],
              },
              { root: true },
            );
          });
        }

        if (res.trainedLayers) {
          dispatch(
            "mod_workspace/SET_layerTrainedStatus",
            {
              networkId,
              trainedLayers: res.trainedLayers,
            },
            { root: true },
          );
        }

        return res;
      })
      .catch(e => {
        console.error(e);
        return e;
      })
      .finally(() => {
        dispatch(
          "mod_workspace/setChartComponentLoadingState",
          { descendants: Object.keys(payload), value: false, networkId },
          { root: true },
        );
        dispatch("mod_events/EVENT_calcArray", null, { root: true });
        dispatch("mod_workspace/SET_networkSnapshot", {}, { root: true });
      });
  },
  API_getBatchPreviewSampleForElementDescendants(
    { getters, dispatch, rootGetters },
    layerId,
  ) {
    const networkList = getters.GET_coreNetworkElementList;
    const pivotLayer = networkList[layerId];
    let descendants = getDescendants(pivotLayer, []);
    const userEmail = rootGetters["mod_user/GET_userEmail"];
    const networkId = rootGetters["mod_workspace/GET_currentNetworkId"];
    let net = cloneDeep(getters.GET_coreNetwork);

    function getDescendants(networkElement, dataIds) {
      if (networkElement.forward_connections.length === 0) {
        return dataIds;
      }
      for (let index in networkElement.forward_connections) {
        const layerId = networkElement.forward_connections[index].dst_id;
        dataIds.push(layerId);
        getDescendants(networkList[layerId], dataIds);
      }
      return dataIds;
    }

    descendants.push(layerId);

    dispatch(
      "mod_workspace/setChartComponentLoadingState",
      { descendants, value: true, networkId },
      { root: true },
    );

    for (let ix in net) {
      let el = net[ix];
      if (descendants.indexOf(ix) !== -1) {
        net[ix]["getPreview"] = true;
      } else {
        net[ix]["getPreview"] = false;
      }
    }
    const datasetSettings =
      rootGetters["mod_workspace/GET_currentNetworkDatasetSettings"];

    return renderingKernel
      .getPreviews(networkId, net, datasetSettings, userEmail)
      .then(res => {
        // console.group('API_getBatchPreviewSampleForElementDescendants');
        // console.log(
        //   'API_getBatchPreviewSampleForElementDescendants res',
        //   theData,
        //   res
        // );
        // console.log('previews', res.previews);
        // console.groupEnd();

        if (res.error) {
          dispatch(
            "globalView/GP_errorPopup",
            res.error.message + "\n\n" + res.error.details,
            { root: true },
          );
        }

        if (res.outputDims) {
          dispatch("mod_workspace/SET_elementOutputDim", res.outputDims, {
            root: true,
          });
          dispatch(
            "mod_workspace-notifications/setNotifications",
            {
              networkId: rootGetters["mod_workspace/GET_currentNetworkId"],
              kernelResponses: res.outputDims,
            },
            { root: true },
          );
        }

        if (res.newNetwork && Object.keys(res.newNetwork).length > 0) {
          for (let ix in res.newNetwork) {
            const currentEl = networkList[ix];
            const saveSettings = {
              elId: ix,
              set: res.newNetwork[ix].Properties,
              code: { Output: res.newNetwork[ix].Code },
              tabName: currentEl.layerSettingsTabName,
              visited: res.newNetwork[ix].visited,
            };
            dispatch(
              "mod_workspace/SET_elementSettings",
              { settings: deepCopy(saveSettings) },
              { root: true },
            );
          }
        }

        if (res.previews && Object.keys(res.previews).length > 0) {
          Object.keys(res.previews).map(previewKey => {
            dispatch(
              "mod_workspace/SET_NetworkChartData",
              {
                layerId: previewKey,
                payload: res.previews[previewKey],
              },
              { root: true },
            );
          });
        }
        return res;
      })
      .catch(e => {
        console.error(e);
      })
      .finally(() => {
        dispatch(
          "mod_workspace/setChartComponentLoadingState",
          { descendants, value: false, networkId },
          { root: true },
        );
      });
  },
  async API_scanCheckpoint(ctx, { networkId, path }) {
    const isDirExist = await rygg_doesDirExist(path);
    if (!isDirExist) {
      return {
        networkId,
        hasCheckpoint: false,
      };
    }

    const trainingSessionId = base64url(checkpointDirFromProject(path));

    return renderingKernel
      .hasCheckpoint(networkId, trainingSessionId)
      .then(res => {
        return {
          networkId,
          hasCheckpoint: res,
        };
      })
      .catch(e => console.error(e));
  },

  API_UploadKernelLogs(ctx, payload) {
    console.error("API_UploadKernelLogs is deprecated!");
  },

  API_setAppInstance({ commit }) {
    let instanceKey = sessionStorage.getItem(sessionStorageInstanceIdKey);
    if (instanceKey === null) {
      instanceKey = uuidv4();
      sessionStorage.setItem(sessionStorageInstanceIdKey, instanceKey);
    }
    commit("API_setAppInstanceMutation", instanceKey);
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions,
};
