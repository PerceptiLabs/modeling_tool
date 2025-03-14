import {
  generateID,
  calcLayerPosition,
  deepCloneNetwork,
  isLocalStorageAvailable,
  stringifyNetworkObjects,
  deepCopy,
  checkpointDirFromProject,
} from "@/core/helpers.js";
import { widthElement, LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY, LOCAL_STORAGE_WORKSPACE_SHOW_MODEL_PREVIEWS, defaultTrainingSettings } from '@/core/constants.js'
import Vue from 'vue'
import router from '@/router'
import { deleteFolder as rygg_deleteFolder } from '@/core/apiRygg';
import cloneDeep from 'lodash.clonedeep';
import { saveModelJson as rygg_saveModelJson, updateModelMeta as rygg_updateModelMeta } from '@/core/apiRygg';
import { lockedComponentsNames } from "@/core/constants.js";
import store from '@/store';
import { disassembleModel, defaultNetwork } from "@/core/helpers/model-helper";
import { attachForwardAndBackwardConnectionsToNetwork } from "@/core/modelHelpers";
const namespaced = true;

const state = {
  workspaceContent: [],
  unparsedModels: [],
  currentNetwork: 0,
  currentModelIndex: -1,
  currentStatsIndex: -1,
  currentTestIndex: -1,
  dragElement: null,
  startArrowID: null,
  webLoadingDataFlag: false,
  preArrow: {
    show: false,
    start: { x: 0, y: 0 },
    stop: { x: 0, y: 0 },
  },
  positionForCopyElement: {
    cursor: { x: 0, y: 0 },
    elementsPosition: [],
    cursorInsideWorkspace: true
  },
  showStartTrainingSpinner: false,
  isOpenElement: false,
  // for dragging multiple elements
  dragBoxContainer: {
    isVisible: false,
    top: 0,
    left: 0,
    width: 0,
    height: 0,
  },
  isSettingInputFocused: false, // is chenghed when focus/blur on sidebar setting input (it's made for preventing component remove when press backspace in input)
  viewType: localStorage.getItem(LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY) || 'model', // [model,statistic,test]
  showModelPreviews: localStorage.hasOwnProperty(LOCAL_STORAGE_WORKSPACE_SHOW_MODEL_PREVIEWS) ? localStorage.getItem(LOCAL_STORAGE_WORKSPACE_SHOW_MODEL_PREVIEWS) === 'true' : true,
  fetchedPreviewsNetworksIds: [],
  copyOrCutNetworkSnapshot: [],
  defaultNetwork: defaultNetwork
};

const getters = {
  GET_networkIndexById: (state) => (networkId) => {
    const networkIndex = state.workspaceContent.findIndex(w => w.networkID == networkId);
    if (networkIndex === -1) {
      throw new Error(`Network: ${networkId} doesn't exists.`);
    }
    return networkIndex
  },
  GET_networkIsNotEmpty(state) {
    return !!state.workspaceContent.length
  },
  GET_networkSnapshotIsNotEmpty(state, getters) {
    if (state.workspaceContent.length === 0 ||
      !state.workspaceContent[state.currentNetwork] ||
      !state.workspaceContent[state.currentNetwork].networkSnapshots ||
      !state.workspaceContent[state.currentNetwork].networkSnapshots.length === 0) {
      return false;
    }

    return true;

  },
  GET_currentNetwork(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork]
      : deepCloneNetwork(state.defaultNetwork);
  },
  GET_currentNetworkDatasetSettings(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork].networkMeta.datasetSettings
      : null
  },
  GET_currentNetworkDatasetSettingsByModelId: (state, getters) => (modelId = null) => {
    return getters.GET_networkByNetworkId(modelId).networkMeta.datasetSettings
  },
  GET_currentNetworkCheckpointDirectory(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? checkpointDirFromProject(state.workspaceContent[state.currentNetwork].apiMeta.location)
      : null
  },
  GET_currentNetworkCheckpointDirectoryByModelId: (state, getters) => (modelId = null) => {
    const network = getters.GET_networkByNetworkId(modelId);
    return (network && network.apiMeta ? checkpointDirFromProject(network.apiMeta.location) : null) || null;
  },
  GET_currentNetworkIndex(state, getters) {
    return state.currentNetwork;
  },
  GET_networkByNetworkId: (state, getters) => (modelId) => {
    if (!modelId) { return null; }
    return state.workspaceContent.find(wc => parseInt(wc.apiMeta.model_id, 10) === parseInt(modelId, 10));
  },
  GET_currentNetworkId(state, getters) {
    return getters.GET_networkIsNotEmpty && state.workspaceContent[state.currentNetwork]
      ? state.workspaceContent[state.currentNetwork].networkID
      : 0
  },
  GET_currentNetworkIdForKernelRequests(state, getters) {
    if (!getters.GET_networkIsNotEmpty) { return 0; }

    if (getters.GET_testIsOpen) {
      return state.workspaceContent[state.currentNetwork].networkID + 't';
    } else {
      return state.workspaceContent[state.currentNetwork].networkID;
    }
  },
  GET_currentModelIndex(state) {
    return state.currentModelIndex;
  },
  GET_currentStatsIndex(state) {
    return state.currentStatsIndex;
  },
  GET_currentTestIndex(state) {
    return state.currentTestIndex;
  },
  GET_networkElementById: state => layerId => {
    return state.workspaceContent[state.currentNetwork].networkElementList[layerId];
  },
  GET_networkElementConnectionInChartData: state => layerId => {
    let connnectionInData = [];
    state.workspaceContent[state.currentNetwork].networkElementList[layerId].connectionIn.forEach(connectionInLayerId => {
      let chartData = state.workspaceContent[state.currentNetwork].networkElementList[connectionInLayerId].chartData;
      chartData = chartData && chartData.series && chartData.series[0].data || '';
      connnectionInData.push(chartData);
    })
    return connnectionInData;
  },
  // connectionIn
  GET_currentNetworkElementList(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork].networkElementList
      : [];
  },
  GET_currentNetworkElementListLength(state, getters) {
    return getters.GET_currentNetworkElementList
      ? getters.GET_currentNetworkElementList.length
      : 0
  },
  GET_networkCoreStatus(state, getters) {
    return getters.GET_networkIsNotEmpty && getters.GET_currentNetwork.networkMeta.coreStatus
      ? getters.GET_currentNetwork.networkMeta.coreStatus.Status
      : null
  },
  GET_networkCoreStatusByModelId: (state, getters) => (modelId = null) => {
    const coreStatus = getters.GET_networkByNetworkId(modelId).networkMeta.coreStatus;
    return coreStatus && coreStatus.Status;
  },
  GET_currentSelectedEl(state, getters) {
    let selectedIndex = [];
    if (getters.GET_networkIsNotEmpty) {
      let elList = getters.GET_currentNetworkElementList;
      for (var el in elList) {
        if (elList[el].componentName === 'LayerContainer' && elList[el].layerNone) continue;
        if (elList[el].layerMeta.isSelected) selectedIndex.push(elList[el]);
      }
    }
    return selectedIndex;
  },
  GET_currentSelectedElIds(state, getters) {
    let selectedIds = [];
    if (getters.GET_networkIsNotEmpty) {
      let elList = getters.GET_currentNetworkElementList;
      for (var el in elList) {
        if (elList[el].layerMeta.isSelected) selectedIds.push(el);
      }
    }
    return selectedIds;
  },
  // Snapshot version of the above functions
  GET_networkSnapshotElementById: (state, getters) => layerId => {
    return getters.GET_currentNetworkSnapshotElementList[layerId];
  },
  GET_currentNetworkSnapshotElementList(state, getters) {

    if (!getters.GET_networkSnapshotIsNotEmpty ||
      !getters.GET_currentNetwork.networkSnapshots ||
      !getters.GET_currentNetwork.networkSnapshots.length > 0) {
      return [];
    }

    return getters.GET_currentNetwork.networkSnapshots[0];
  },
  GET_currentSelectedElementsInSnapshot(state, getters) {
    let selectedIndex = [];
    if (getters.GET_networkIsNotEmpty) {
      let elList = getters.GET_currentNetworkSnapshotElementList;
      for (var el in elList) {
        if (elList[el].componentName === 'LayerContainer' && elList[el].layerNone) continue;
        if (elList[el].layerMeta.isSelected) selectedIndex.push(elList[el]);
      }
    }
    return selectedIndex;
  },
  GET_currentNetworkZoom(state, getters) {
    if (!getters.GET_networkIsNotEmpty) { return 1; }

    if (getters.GET_statisticsOrTestIsOpen) {
      return getters.GET_currentNetwork.networkMeta.zoomSnapshot || 1;
    } else {
      return getters.GET_currentNetwork.networkMeta.zoom;
    }
  },
  GET_currentNetworkModeWeightsState(state, getters) {
    if (!getters.GET_networkIsNotEmpty) { return false; }

    if (getters.GET_currentNetwork.networkMeta &&
      getters.GET_currentNetwork.networkMeta.usingWeights &&
      typeof getters.GET_currentNetwork.networkMeta.usingWeights === 'boolean') {
      return getters.GET_currentNetwork.networkMeta.usingWeights;
    } else {
      return false;
    }

  },
  GET_currentNetworkModeWeightsStateById: (state, getters) => (id) => {
    const net = getters.GET_networkByNetworkId(id);
    if (!net) { return false; }

    if (net.networkMeta &&
      net.networkMeta.usingWeights &&
      typeof net.networkMeta.usingWeights === 'boolean') {
      return net.networkMeta.usingWeights;
    } else {
      return false;
    }

  },
  GET_networkIsTraining(state, getters) {
    const coreStatus = getters.GET_networkCoreStatus;
    const statusList = ['Training', 'Validation', 'Paused'];
    return !!statusList.includes(coreStatus)
  },
  GET_anyNetworkIsTraining(state, getters) {
    const statusList = ['Training', 'Validation', 'Paused'];

    return state.workspaceContent.some(wc => {

      if (!wc.networkMeta ||
        !wc.networkMeta.coreStatus ||
        !wc.networkMeta.coreStatus.Status) { return; }

      if (statusList.includes(wc.networkMeta.coreStatus.Status)) {
        return true;
      }
    });
  },
  GET_viewType(state, getters) {
    return state.viewType;
  },
  GET_statisticsIsOpen(state, getters) {
    if (getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.openStatistics;
    }
  },
  GET_testIsOpen(state, getters) {
    if (getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.openTest;
    }
  },
  GET_statisticsOrTestIsOpen(state, getters) {
    if (getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.openStatistics || getters.GET_currentNetwork.networkMeta.openTest;
    }
  },
  GET_networkIsOpen(state, getters) {
    if (getters.GET_networkIsNotEmpty) {
      let openStatistics = getters.GET_currentNetwork.networkMeta.openStatistics;
      let openTest = getters.GET_currentNetwork.networkMeta.openTest;
      return !(openStatistics || openTest);
    }
  },
  GET_networkWaitGlobalEvent(state, getters) {
    if (getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.chartsRequest.waitGlobalEvent;
    }
  },
  GET_networkShowCharts(state, getters) {
    if (getters.GET_networkIsNotEmpty && getters.GET_currentNetwork) {
      return getters.GET_currentNetwork.networkMeta.chartsRequest.showCharts;
    }
  },
  GET_networkDoRequest(state, getters) {
    if (getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.chartsRequest.doRequest;
    }
  },
  GET_showStartTrainingSpinner(state) {
    return state.showStartTrainingSpinner
  },
  GET_enableHotKeyElement(state, getters, rootState) {
    return !state.isOpenElement && getters.GET_networkIsOpen && rootState.mod_events.isEnableCustomHotKey
  },
  GET_positionForCopyElement(state) {
    return state.positionForCopyElement;
  },
  GET_cursorInsideWorkspace(state) {
    return state.positionForCopyElement.cursorInsideWorkspace;
  },
  GET_selectedElement(state, getters) {
    const networkList = getters.GET_currentNetworkElementList;

    if (networkList === null) {
      return null;
    }
    const focusedElement = Object.values(networkList).filter(el => el.layerMeta.isSelected)
    if (focusedElement.length === 0 || focusedElement.length > 1) {
      return null;
    }
    return focusedElement[0];
  },
  GET_descendentIds: (state, getters, rootState, rootGetters) => (pivotLayer, withPivot) => {
    return rootGetters['mod_api/GET_descendentIds'](pivotLayer, withPivot);
  },
  GET_networksInCurrentProject(state, getters) {

    if (getters.GET_networkIsNotEmpty) {
      const currentProject = getters.GET_currentNetwork;
      if (!currentProject || !currentProject.apiMeta.project) { return []; }

      return state.workspaceContent.filter(wc => wc.apiMeta.project === currentProject.apiMeta.project);
    } else {
      return [];
    }
  },
  GET_models(state) {
    return state.workspaceContent;
  },
  GET_modelName: (state, getters) => (id) => {
    const model = getters.GET_networkByNetworkId(id);
    return model && model.networkName || `Model ${id}`;
  },
  GET_networkElmentPositions(state, getters) {
    const networkList = getters.GET_currentNetworkElementList;
    if (networkList === null) {
      return {};
    }
    let positions = {};
    Object.values(networkList).map(el => {
      positions[el.layerId] = el.layerMeta.position
    })
    return positions;
  },
  GET_copyOrCutNetworkSnapshot(state) {
    return state.copyOrCutNetworkSnapshot;
  },
  GET_modelTrainingSetting: (state, getters) => {
    const currentNetwork = getters.GET_currentNetwork;
    return currentNetwork.networkMeta.trainingSettings
  },
  GET_inputs: (state, getters) => {
    let net = deepCloneNetwork(getters.GET_currentNetworkElementList);

    return Object.values(net).filter(el => (el.layerType === 'IoInput'));
  },
  GET_inputsAndOutputs: (state, getters) => {
    let net = deepCloneNetwork(getters.GET_currentNetworkElementList);

    let Inputs = Object.values(net).filter(el => (el.layerType === 'IoInput'));
    let Output = Object.values(net).filter(el => (el.layerType === 'IoOutput'))[0];

    let componentsTabs = [];

    // make inputs tabs
    componentsTabs.push({
      btnId: Inputs.length > 1 ? 'Input' : Inputs[0].layerName,
      name: Inputs.length > 1 ? 'Input' : Inputs[0].layerName,
      layerId: Inputs[0].layerId,
      type: Inputs.length > 1 ? 'input' : 'component',  // input | component
      layerType: Inputs.length > 1 ? 'IoInput' : Inputs[0].layerType,
      btnInteractiveInfo: {
        title: Inputs.length > 1 ? 'Input' : Inputs[0].layerName,
        text: 'View the global'
      },
    });

    // make output overview tab
    componentsTabs.push({
      btnId: 'Overview',
      name: 'Overview',
      layerId: Output.layerId,
      type: 'component',  // default | component
      layerType: Output.layerType,
      btnInteractiveInfo: {
        title: 'Overview',
        text: 'Overview'
      },
    })
    // add performance tab for categorical output
    if (Output.layerSettings.DataType === 'categorical') {
      componentsTabs.push({
        btnId: 'Performance',
        name: 'Performance',
        layerId: Output.layerId,
        type: 'component',  // default | component
        layerType: Output.layerType,
        btnInteractiveInfo: {
          title: 'Performance',
          text: 'Performance'
        },
      });
    }
    // add global loss tab.
    componentsTabs.push({
      btnId: "Global Loss",
      btnInteractiveInfo: { title: "Global Loss", text: "Global Loss" },
      layerId: null,
      layerType: null,
      name: "Global Loss",
      type: "tab",
    });

    return componentsTabs;
  },
};

const mutations = {
  setFetchedPreviewsNetworksIds(state, networkId) {
    state.fetchedPreviewsNetworksIds.push(networkId)
  },
  SET_previewVariable(state, payload) {
    currentElement(payload.layerId).previewVariable = payload.previewVariableName
  },
  SET_previewVariableList(state, payload) {
    currentElement(payload.layerId).previewVariableList = payload.previewVariableList
  },
  setViewTypeMutation(state, value) {
    localStorage.setItem(LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY, value)
    state.viewType = value;
  },
  update_network_meta(state, { networkID, key, value }) {
    const modelIndex = state.workspaceContent.findIndex(network => network.networkID === networkID);
    if (modelIndex !== -1) {
      Vue.set(state.workspaceContent[modelIndex].networkMeta, key, value);

      const model = disassembleModel(state.workspaceContent[modelIndex]);
      rygg_updateModelMeta(model);
    }
  },
  cleanupUnnecessaryArrowsMutation(state, { getters }) {
    const networkList = getters.GET_currentNetworkElementList;

  },
  updateCheckpointPaths(state) {
    if (!state.workspaceContent[state.currentNetwork] ||
      !state.workspaceContent[state.currentNetwork].networkElementList) { return; }

    const projectPath = state.workspaceContent[state.currentNetwork].apiMeta.location;
    const networkList = state.workspaceContent[state.currentNetwork].networkElementList;

    for (const idx in networkList) {
      networkList[idx].checkpoint = [];
      networkList[idx].checkpoint.push(null);
      networkList[idx].checkpoint.push(projectPath);
    }
  },
  updateForwardBackwardConnectionsMutation(state, { payload, getters }) {
    const networkList = getters.GET_currentNetworkElementList
    Object.keys(payload).map(key => {
      const elId = key;
      Vue.set(networkList[elId], "forward_connections", payload[elId].forward_connections);
      Vue.set(networkList[elId], "backward_connections", payload[elId].backward_connections);
    })
  },
  setIsSettingInputFocused(state, value) {
    state.isSettingInputFocused = value;
  },
  update_model(state, { index, field, value }) {
    Vue.set(state.workspaceContent[index], [field], value);
  },
  set_model_saved_version_location(state, { getters, saved_version_location }) {
    getters.GET_currentNetwork.apiMeta.saved_version_location = saved_version_location;
  },
  replace_network_element_list(state, { newNetworkElementList, getters }) {
    Vue.set(state.workspaceContent[state.currentNetwork], 'networkElementList', newNetworkElementList);
  },
  set_model_location(state, { getters, location }) {
    getters.GET_currentNetwork.apiMeta.location = location;
  },
  add_model_from_local_data(state, model) {
    state.workspaceContent.push(model);
  },
  reset_network(state) {
    state.workspaceContent = [];
  },
  RESTORE_network(state, val) {
    state.workspaceContent = val.workspaceContent;
    state.currentNetwork = val.currentNetwork;
  },
  //---------------
  //  LOCALSTORAGE
  //---------------
  set_workspacesInLocalStorage(state) {
    if (!isLocalStorageAvailable()) { return; }
    try {
      let networkIDs = JSON.parse(localStorage.getItem('_network.ids')) || [];
      state.workspaceContent.forEach(network => {
        networkIDs.push(network.networkID);

        localStorage.setItem(`_network.${network.networkID}`, stringifyNetworkObjects(network));
      });
      networkIDs = networkIDs.filter(onlyUnique);

      localStorage.setItem('_network.ids', JSON.stringify(networkIDs.sort()));
    } catch (error) {
      // console.error('Error persisting networks to localStorage', error);
    }
    function onlyUnique(value, index, self) {
      return self.indexOf(value) === index;
    }
  },
  get_workspacesFromLocalStorage(state, currentProject) {
    // this function is invoked when the pageQuantum (workspace) component is created
    // the networks that were saved in the localStorage are hydrated
    let newWorkspaceContent = [];
    const activeNetworkIDs = localStorage.getItem('_network.ids') || [];
    const keys = Object.keys(localStorage)
      .filter(key =>
        key.startsWith('_network.') &&
        key !== '_network.ids' &&
        key !== '_network.meta')
      .sort();

    for (const key of keys) {
      const networkID = key.replace('_network.', '');
      // state.workspaceContent = [];
      // _network.<networkID> entries in localStorage are only cleared on load
      if (!activeNetworkIDs.includes(networkID)) {
        localStorage.removeItem(key);
        continue;
      }

      const networkIsLoaded = state.workspaceContent
        .some(networkInWorkspace => networkInWorkspace.networkID === networkID)

      if (true) {
        const network = JSON.parse(localStorage.getItem(key));

        // remove focus from previous focused network elements

        if (network.networkElementList)
          Object.keys(network.networkElementList).map(elKey => {
            // console.log(network.networkElementList[elKey]);
            // debugger;
            network.networkElementList[elKey].layerMeta.isSelected = false;
          });
      }
    }
  },
  set_lastActiveTabInLocalStorage(state, networkID) {
    if (!isLocalStorageAvailable()) { return; }

    localStorage.setItem('_network.meta', JSON.stringify({ 'lastActiveNetworkID': networkID }));

  },
  get_lastActiveTabFromLocalStorage(state) {
    // function for remembering the last active tab
    const networkMeta = JSON.parse(localStorage.getItem('_network.meta')) || {};

    const currentNetworkID = networkMeta.lastActiveNetworkID;
    const index = state.workspaceContent.findIndex((el) => el.networkID === currentNetworkID);

    state.currentNetwork = (index >= 0) ? index : 0;
  },
  //---------------
  //  NETWORK
  //---------------
  set_networkName(state, { getters, value }) {
    getters.GET_currentNetwork.networkName = value
  },
  set_networkRootFolder(state, { getters, value }) {
    getters.GET_currentNetwork.networkRootFolder = value
  },
  update_network(state, { networkId, newNetwork }) {
    const networkIndex = state.workspaceContent.findIndex(w => w.networkID == networkId);

    if (networkIndex > -1) {
      Vue.set(state.workspaceContent, networkIndex, newNetwork);

      const streamLinedNetwork = disassembleModel(newNetwork);
      rygg_saveModelJson(streamLinedNetwork)
    }
  },
  add_network(state, { newNetwork, dispatch, focusOnNetwork }) {
    let workspace = state.workspaceContent;

    const netIndex = findNetId(newNetwork, workspace);
    if (netIndex > -1) {
      workspace.splice(netIndex, 1, newNetwork);
      state.currentNetwork = netIndex;
    } else {

      // find position to insert 
      // (can be done with binary serach but no gains with < 10 models)
      let currIdx = 0
      while (currIdx < workspace.length &&
        workspace[currIdx].networkID < newNetwork.networkID) {
        currIdx += 1;
      }
      workspace.splice(currIdx, 0, deepCloneNetwork(newNetwork));
      state.currentNetwork = currIdx;
    }

    //-- Open last Network
    //-- Go to app page
    if (router.history.current.name !== 'app' && focusOnNetwork === true) {
      router.replace({ name: 'app' });
    }

    const streamLinedNetwork = disassembleModel(newNetwork);
    rygg_saveModelJson(streamLinedNetwork)

    function findNetId(newNet, netList) {
      let indexId = netList.findIndex((el) => el.networkID === newNet.networkID);
      return indexId;
    }
  },
  add_existingNetworkToWorkspace(state, { network }) {
    // This method is used for load the networks in to the workspace from the idb
    // We cannot use the normal 'add_network' call because it does a save, which
    // means that changes to networks will be overwritten on load (page refreshes)

    let workspace = state.workspaceContent;

    const netIndex = findNetId(network, workspace);
    if (netIndex > -1) {
      workspace.splice(netIndex, 1, network);
      // state.currentNetwork = netIndex;
    } else {
      // find position to insert 
      // (can be done with binary search but no gains with < 10 models) 
      let currIdx = 0
      while (currIdx < workspace.length &&
        workspace[currIdx].networkID < network.networkID) {
        currIdx += 1;
      }

      workspace.splice(currIdx, 0, deepCloneNetwork(network));
      // state.currentNetwork = currIdx;
    }

    function findNetId(newNet, netList) {
      let indexId = netList.findIndex((el) => el.networkID === newNet.networkID);
      return indexId;
    }
  },
  async delete_network(state, index) {

    const path = state.workspaceContent[index].apiMeta.location.replace('/', '\\');
    await rygg_deleteFolder(path)


    if (state.currentNetwork >= index) {
      const index = state.currentNetwork - 1;
      state.currentNetwork = index < 0 ? 0 : index
    }

    state.workspaceContent.splice(index, 1);
  },
  async delete_networkById(state, networkId) {
    const networkIndex = state.workspaceContent.findIndex(w => w.networkID == networkId);

    if (networkIndex < 0) { return; }

    const path = state.workspaceContent[networkIndex].apiMeta.location;
    state.workspaceContent.splice(networkIndex, 1);

    await rygg_deleteFolder(path)
  },
  async unregister_networkById(state, networkId) {
    const networkIndex = state.workspaceContent.findIndex(w => w.networkID == networkId);

    if (networkIndex < 0) { return; }

    state.workspaceContent.splice(networkIndex, 1);
  },
  //---------------
  //  LOADER FOR TRAINING
  //---------------
  SET_showStartTrainingSpinner(state, value) {
    state.showStartTrainingSpinner = value;
  },
  //---------------
  //  NETWORK META
  //---------------
  set_netMode(state, { getters, value }) {
    getters.GET_currentNetwork.networkMeta.netMode = value;
  },
  set_openStatistics(state, { dispatch, getters, value }) {

    if (!getters.GET_currentNetwork) { return; }

    getters.GET_currentNetwork.networkMeta.openStatistics = value;

    if (value) {
      dispatch('mod_statistics/STAT_defaultSelect', null, { root: true });
      //dispatch('mod_events/EVENT_chartResize', null, {root: true});
    }
  },
  set_openStatisticsByNetworkId(state, { dispatch, getters, networkId, value }) {
    // This is used for setting which networks have been trained.

    const network = getters.GET_networkByNetworkId(networkId);

    if (!network) { return; }

    network.networkMeta.openStatistics = value;

    if (value === true) {
      dispatch('mod_statistics/STAT_defaultSelect', null, { root: true });
      dispatch('SET_chartsRequestsIfNeeded', network.networkID)
    }
  },
  set_openTest(state, { dispatch, getters, value }) {

    if (!getters.GET_currentNetwork) { return; }

    if (value && getters.GET_statisticsIsOpen !== null) {
      getters.GET_currentNetwork.networkMeta.openStatistics = false;
    }
    if (value) {
      getters.GET_currentNetwork.networkMeta.openTest = false;
      dispatch('mod_statistics/STAT_defaultSelect', null, { root: true });
      getters.GET_currentNetwork.networkMeta.openTest = true
      //dispatch('mod_events/EVENT_chartResize', null, {root: true});
    }
    else getters.GET_currentNetwork.networkMeta.openTest = value;
  },
  set_openTestByNetworkId(state, { dispatch, getters, networkId, value }) {
    const network = getters.GET_networkByNetworkId(networkId);
    if (!network) { return; }

    if (!value) {
      network.networkMeta.openTest = null;
    } else if (network.networkMeta.openTest !== true) {
      network.networkMeta.openTest = false;
    }
  },
  SET_statisticsAndTestToClosed(state, { getters, networkId }) {
    const network = getters.GET_networkByNetworkId(networkId);
    if (!network) { return; }

    if (typeof network.networkMeta.openStatistics === 'boolean') {
      network.networkMeta.openStatistics = false;
    }

    if (typeof network.networkMeta.openTest === 'boolean') {
      network.networkMeta.openTest = false;
    }
  },
  set_layerTrainedStatus(state, { getters, networkId, layerId, value }) {

    const network = state.workspaceContent.find(wc => wc.networkID === networkId);
    if (!network) { return; }

    const element = network.networkElementList[layerId];
    if (!element) { return; }

    Vue.set(element, 'isTrained', value);
  },
  set_networkSnapshot(state, { dispatch, getters }) {
    const network = cloneDeep(getters.GET_currentNetwork);
    let zoomFrom = network.networkMeta.zoom;
    let zoomTo = getters.GET_currentNetwork.networkMeta.zoomSnapshot;
    let clonedNetworkElementList = network.networkElementList;

    Object.keys(clonedNetworkElementList).map(elId => {
      clonedNetworkElementList[elId].layerMeta.position.top = (clonedNetworkElementList[elId].layerMeta.position.top / zoomFrom) * zoomTo;
      clonedNetworkElementList[elId].layerMeta.position.left = (clonedNetworkElementList[elId].layerMeta.position.left / zoomFrom) * zoomTo;
    });

    if (!getters.GET_currentNetwork.networkSnapshots) {
      Vue.set(getters.GET_currentNetwork, 'networkSnapshots', []);
    }

    getters.GET_currentNetwork.networkSnapshots.splice(0, 1, clonedNetworkElementList);
  },
  set_statusNetworkCore(state, { getters, value }) {
    if (getters.GET_currentNetwork.networkMeta) {
      getters.GET_currentNetwork.networkMeta.coreStatus = value;
    }
  },
  set_statusNetworkCoreDynamically(state, { modelId, payload }) {
    const networkIndex = state.workspaceContent.findIndex(net => net.networkID === modelId);
    const payloadHaveValues = !!Object.keys(payload).length;
    if (networkIndex !== -1 && payloadHaveValues) {
      Vue.set(state.workspaceContent[networkIndex].networkMeta, 'coreStatus', { ...state.workspaceContent[networkIndex].networkMeta.coreStatus, ...payload });
    }
  },
  set_statusNetworkCoreStatus(state, { getters, value }) {
    if (getters.GET_currentNetwork.networkMeta && getters.GET_currentNetwork.networkMeta.coreStatus) {
      getters.GET_currentNetwork.networkMeta.coreStatus.Status = value;
    }
  },
  set_NetworkCoreError(state, { errorMessage, modelId, commit }) {
    let workspaceIndex = null;
    state.workspaceContent.map((workspace, index) => {
      if (parseInt(workspace.networkID) === modelId) {
        workspaceIndex = index;
      }
    })
    if (workspaceIndex !== null) {
      state.workspaceContent[workspaceIndex].networkMeta.coreError = {};
      state.workspaceContent[workspaceIndex].networkMeta.coreError.Status = 'Error';
      state.workspaceContent[workspaceIndex].networkMeta.coreError.errorMessage = errorMessage;
    }
  },
  set_statusNetworkCoreStatusProgressClear(state, { getters }) {
    if (getters.GET_currentNetwork.networkMeta.coreStatus && getters.GET_currentNetwork.networkMeta.coreStatus.Status.Progress) {
      getters.GET_currentNetwork.networkMeta.coreStatus.Status.Progress = 0;
    }
  },
  set_statusNetworkZoom(state, { getters, value }) {
    if (getters.GET_statisticsOrTestIsOpen) {
      // Using Vue.set because the zoomSnapshot seems to not be a part of 
      // the default network template anymore...
      Vue.set(getters.GET_currentNetwork.networkMeta, 'zoomSnapshot', value);
    } else {
      getters.GET_currentNetwork.networkMeta.zoom = value;
    }
  },
  set_charts_doRequest(state, { getters, networkIndex }) {
    networkIndex !== undefined && networkIndex !== null
      ? Vue.set(state.workspaceContent[networkIndex].networkMeta.chartsRequest, 'doRequest', state.workspaceContent[networkIndex].networkMeta.chartsRequest.doRequest + 1) //TODO проверить что счетчики идут паралельно в нескольких networks
      : Vue.set(getters.GET_currentNetwork.networkMeta.chartsRequest, 'doRequest', getters.GET_currentNetwork.networkMeta.chartsRequest.doRequest + 1);
  },
  set_charts_showCharts(state, { getters, networkIndex }) {
    networkIndex !== undefined && networkIndex !== null
      ? Vue.set(state.workspaceContent[networkIndex].networkMeta.chartsRequest, 'showCharts', state.workspaceContent[networkIndex].networkMeta.chartsRequest.showCharts + 1)
      : Vue.set(getters.GET_currentNetwork.networkMeta.chartsRequest, 'showCharts', getters.GET_currentNetwork.networkMeta.chartsRequest.showCharts + 1);
  },
  set_charts_timerID(state, { getters, timerId, networkIndex }) {
    networkIndex !== undefined && networkIndex !== null
      ? Vue.set(state.workspaceContent[networkIndex].networkMeta.chartsRequest, 'timerID', timerId)
      : Vue.set(getters.GET_currentNetwork.networkMeta.chartsRequest, 'timerID', timerId);
  },
  set_statusNetworkWaitGlobalEvent(state, { getters, value }) {
    Vue.set(getters.GET_currentNetwork.networkMeta.chartsRequest, 'waitGlobalEvent', value);
  },
  //---------------
  //  NETWORK ELEMENTS
  //---------------
  SET_CopyCursorPosition(state, position) {
    state.positionForCopyElement.cursor.x = position.x;
    state.positionForCopyElement.cursor.y = position.y;
  },
  SET_CopyElementsPosition(state, position) {
    state.positionForCopyElement.elementsPosition.push({ left: position.left, top: position.top });
  },
  SET_cursorInsideWorkspace(state, value) {
    state.positionForCopyElement.cursorInsideWorkspace = value
  },
  CLEAR_CopyElementsPosition(state) {
    state.positionForCopyElement.elementsPosition = [];
  },
  SET_elementName(state, value) {
    currentElement(value.id).layerName = value.setValue
  },
  add_element(state, { getters, dispatch, event, setChangeToWorkspaceHistory, triggeredByHotKey }) {
    let duplicatePositionIndent = 60;
    let cursorPosition = getters.GET_positionForCopyElement.cursor;
    let firstCopyPositionElement = getters.GET_positionForCopyElement.elementsPosition[0];
    let isCursorInsideWorkspace = getters.GET_cursorInsideWorkspace;
    let newEl = state.dragElement
      ? state.dragElement
      : createNetElement(event);

    let elementList = getters.GET_currentNetworkElementList;

    if (triggeredByHotKey && isCursorInsideWorkspace && firstCopyPositionElement) {
      // for copy/pasted components
      newEl.layerMeta.position.top = cursorPosition.y + event.offsetY - firstCopyPositionElement.top;
      newEl.layerMeta.position.left = cursorPosition.x + event.offsetX - firstCopyPositionElement.left;
    } else {
      // for toolbar
      newEl.layerMeta.position.top = event.offsetY;
      newEl.layerMeta.position.left = event.offsetX;
    }

    let depth = checkPosition(newEl, elementList);
    if (depth > 0) {
      newEl.layerMeta.position.top = newEl.layerMeta.position.top + (duplicatePositionIndent * depth);
      newEl.layerMeta.position.left = newEl.layerMeta.position.left + (duplicatePositionIndent * depth);
    }

    updateLayerName(newEl, elementList, 1);

    if (!elementList || elementList.length === 0) state.workspaceContent[state.currentNetwork].networkElementList = {};

    Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newEl.layerId, newEl);

    // updates checkpoints because of the refactoring done Sept 2020
    for (const idx in state.workspaceContent[state.currentNetwork].networkElementList) {
      const el = state.workspaceContent[state.currentNetwork].networkElementList[idx];
      el.checkpoint = [];
      el.checkpoint.push(null);
      el.checkpoint.push(state.workspaceContent[state.currentNetwork].apiMeta.location);
    }

    dispatch('SET_elementSelect', { id: newEl.layerId, resetOther: true, setValue: true });
    state.dragElement = null;

    if (setChangeToWorkspaceHistory)
      dispatch('mod_workspace-history/PUSH_newSnapshot', null, { root: true });

    // dispatch('mod_api/API_getBatchPreviewSample', {}, {root: true})

    function checkPosition(el, list) {
      let depth = 0;

      runChecking(el, list);
      return depth;

      function runChecking(el, list) {
        let top = el.layerMeta.position.top + (duplicatePositionIndent * depth);
        let left = el.layerMeta.position.left + (duplicatePositionIndent * depth);
        for (let existID in list) {
          let existEl = list[existID];
          let elTop = existEl.layerMeta.position.top;
          let elLeft = existEl.layerMeta.position.left;
          if (top === elTop && left === elLeft) {
            ++depth;
            runChecking(el, list);
            return
          }
        }
      }
    }
  },
  delete_element(state, { getters, dispatch }) {

    let arrSelect = cloneDeep(getters.GET_currentSelectedEl);

    // filter locked components to not be removed
    arrSelect = arrSelect.filter(el => !lockedComponentsNames.includes(el.componentName))

    if (!arrSelect.length) return;
    let arrSelectID = [];
    const copyOfNetwork = attachForwardAndBackwardConnectionsToNetwork(getters.GET_currentNetworkElementList);
    let net = { ...getters.GET_currentNetworkElementList };

    deleteElement(arrSelect);

    let descendantsIds = []
    for (let ix in arrSelectID) {
      const id = arrSelectID[ix];
      descendantsIds = [...descendantsIds, ...getters.GET_descendentIds(copyOfNetwork[id], false)]
    }
    descendantsIds = Array.from(new Set(descendantsIds));
    descendantsIds = descendantsIds.filter((item) => {
      return !arrSelectID.includes(item);
    })
    let getBatchPreviewPayload = {};
    for (let index in net) {
      const el = net[index];
      // getBatchPreviewPayload[ix] = null;
      if (descendantsIds.indexOf(el.layerId) !== -1) {
        getBatchPreviewPayload[index] = el.previewVariable;
      }
    }

    for (let el in net) {
      let element = net[el];
      element.connectionOut = element.connectionOut.filter((connect) => {
        return !arrSelectID.includes(connect)
      });
      element.connectionArrow = element.connectionArrow.filter((connect) => {
        return !arrSelectID.includes(connect)
      });
      element.connectionIn = element.connectionIn.filter((connect) => {
        return !arrSelectID.includes(connect)
      });

      if (element.layerNone && element.containerLayersList) {
        arrSelect.forEach(select => {
          element.layerNone = false;  // (close layersContainer) for remove elements from Layers
          delete element.containerLayersList[select.layerId];
          element.layerNone = true;
          const layerListLength = Object.keys(element.containerLayersList).length;

          if (layerListLength === 0) {
            if (net[el] && net[el].parentContainerID) {
              delete net[net[el].parentContainerID].containerLayersList[net[el].layerId]
            };
            delete net[el];
          }
        });
      }
    }
    for (let el in net) {
      if (net[el].layerNone && net[el].containerLayersList) {
        if (Object.keys(net[el].containerLayersList).length === 1) {
          const elementKeyId = Object.keys(net[el].containerLayersList)[0];
          if (net[el].parentContainerID) {
            // is last item and parent component is container
            if (net[net[el].parentContainerID]) {
              delete net[net[el].parentContainerID].containerLayersList[net[el].layerId];
              net[net[el].parentContainerID].containerLayersList[elementKeyId] = elementKeyId;
              delete net[el];
            } else {
              // if parent container was deleted on this iteration
              let parentId = copyOfNetwork[net[el].parentContainerID].parentContainerID;
              delete net[parentId].containerLayersList[net[el].layerId];
              net[parentId].containerLayersList[elementKeyId] = elementKeyId;
              delete net[el];
            }
          } else {
            // is last item and haven't parent container component
            delete net[elementKeyId].parentContainerID;
            delete net[el];
          }
        }
      }
    }

    // state.workspaceContent[state.currentNetwork].networkElementList = {...net};
    dispatch('ReplaceNetworkElementList', { ...net });
    dispatch('SET_isOpenElement', false);
    dispatch('mod_api/API_getBatchPreviewSample', getBatchPreviewPayload, { root: true })
    dispatch('mod_events/EVENT_calcArray', null, { root: true });
    function deleteElement(list) {
      list.forEach((el) => {
        if (el.componentName === 'LayerContainer') {
          deleteElement(Object.keys(el.containerLayersList).map(key => net[key]))
        }

        if (net[el.layerId].hasOwnProperty('outputs')) {
          let outputs = net[el.layerId].outputs;
          Object.keys(outputs).map(outputId => {
            for (let id in net) {
              let el = net[id];
              let elInputs = el.inputs;
              Object.keys(elInputs).map(inputId => {
                const input = elInputs[inputId];
                if (input.reference_var_id === outputId) {
                  input.reference_var_id = null;
                  input.reference_layer_id = null;
                }
              })
            }
          })
        }

        delete net[el.layerId];
        arrSelectID.push(el.layerId);
      });
    }
  },
  add_arrow(state, { dispatch, stopID }) {

    const startObject = state.startArrowID;    // outputDotId | outputLayerId | layerId
    const endObject = stopID;                  // inputDotId | inputLayerId | layerId


    if (startObject.layerId === endObject.layerId) return;

    const endEl = currentElement(endObject.layerId);


    // check if input already has connection
    if (endEl.inputs[endObject.inputDotId].reference_layer_id !== null) {
      dispatch('globalView/GP_infoPopup', 'This input already has a connection!', { root: true });
      return;
    }

    endEl.inputs[endObject.inputDotId].reference_var_id = startObject.outputDotId
    endEl.inputs[endObject.inputDotId].reference_layer_id = startObject.layerId


    // let findArrow = currentElement(startID).connectionOut.findIndex((element)=> element === stopID );
    // if(findArrow !== -1) {
    //   dispatch('globalView/GP_infoPopup', 'Connection already exists!', {root: true});
    //   return
    // }
    // if(currentElement(startID).componentName === 'LayerContainer'
    //   || currentElement(stopID).componentName === 'LayerContainer'
    // ) {
    //   dispatch('globalView/GP_infoPopup', 'Cannot create connection to Layer Container!', {root: true});
    //   return
    // }

    // currentElement(startID).connectionOut.push(stopID.toString()); //ID.toString need for the core
    // currentElement(startID).connectionArrow.push(stopID.toString());
    // currentElement(stopID).connectionIn.push(startID.toString());
    state.startArrowID = null;

    dispatch('mod_events/EVENT_calcArray', null, { root: true })
  },
  delete_arrow(state, { dispatch, arrow }) {
    let elStart = currentElement(arrow.startIds.layer);
    let elStop = currentElement(arrow.stopIds.layer);
    if (elStart.componentName === 'LayerContainer'
      || elStop.componentName === 'LayerContainer'
    ) {
      dispatch('globalView/GP_infoPopup', 'To remove the connection, please open the Layer Container', { root: true });
      return
    }

    // let newConnectionOut = currentElement(startID).connectionOut.filter((item)=> item !== stopID);
    // let newConnectionArrow = currentElement(startID).connectionArrow.filter((item)=> item !== stopID);
    // let newConnectionIn = currentElement(stopID).connectionIn.filter((item)=> item !== startID);

    // currentElement(startID).connectionOut = newConnectionOut;
    // currentElement(startID).connectionArrow = newConnectionArrow;
    elStop.inputs[arrow.stopIds.variable].reference_layer_id = null;
    elStop.inputs[arrow.stopIds.variable].reference_var_id = null;
    dispatch('mod_events/EVENT_calcArray', null, { root: true })
  },
  DELETE_copyProperty(state, id) {
    state.workspaceContent[state.currentNetwork].networkElementList[id].copyId = null;
    state.workspaceContent[state.currentNetwork].networkElementList[id].copyContainerElement = null;
  },

  /*-- NETWORK ELEMENTS SETTINGS --*/
  set_elementSettings(state, { dispatch, settings }) {
    if (!currentElement(settings.elId)) { return; }

    currentElement(settings.elId).layerSettings = settings.set;
    currentElement(settings.elId).layerCode = settings.code;
    currentElement(settings.elId).layerSettingsTabName = settings.tabName;
    currentElement(settings.elId).visited = settings.visited;
  },

  /*-- NETWORK ELEMENTS META --*/
  set_elementUnselect(state, { getters }) {
    for (let layer in getters.GET_currentNetworkElementList) {
      currentElement(layer).layerMeta.isSelected = false;
    }
  },
  set_elementSelect(state, { getters, value }) {
    if (value.resetOther) {
      for (let layer in getters.GET_currentNetworkElementList) {
        currentElement(layer).layerMeta.isSelected = false;
      }
    }
    let el = currentElement(value.id);
    if (el) {
      currentElement(value.id).layerMeta.isSelected = value.setValue;
    }
  },
  set_elementSelectAll(state, { getters }) {

    const net = getters.GET_currentNetworkElementList;

    let netWorkIdToOmit = [];
    omitIds(net);

    for (let layer in getters.GET_currentNetworkElementList) {
      if (netWorkIdToOmit.indexOf(layer) === -1) {
        currentElement(layer).layerMeta.isSelected = true;
      }
    }

    function omitIds(net) {
      Object.values(net).map(netEl => {
        if (netEl.layerType === 'Container' && !netEl.layerNone) {
          netWorkIdToOmit = [...netWorkIdToOmit, ...Object.keys(netEl.containerLayersList)];
        }
        if (netEl.layerType === 'Container' && netEl.layerNone) {
          netWorkIdToOmit = [...netWorkIdToOmit, netEl.layerId]
        }
      });
    }
  },
  set_elementMultiSelect(state, value) {
    if (currentElement(value.id).layerNone === false)
      currentElement(value.id).layerMeta.isSelected = value.setValue;
  },
  SET_elementLock(state, id) {
    let elMeta = currentElement(id).layerMeta;
    elMeta.isLock = !elMeta.isLock
  },
  SET_elementVisible(state, id) {
    let elMeta = currentElement(id).layerMeta;
    elMeta.isInvisible = !elMeta.isInvisible
  },
  SET_elementBgColor(state, value) {
    let elMeta = currentElement(value.id).layerMeta;
    elMeta.layerBgColor = value.color
  },
  SET_elementNone(state, { id, value }) {
    let el = currentElement(id);
    el.layerNone = value
  },
  change_elementPosition(state, { value, getters }) {
    // here should calculate how much change position and apply on all elements selected
    let elPosition = currentElement(value.id).layerMeta.position;
    const toTop = value.top - elPosition.top;
    const toLeft = value.left - elPosition.left;

    const selectedElIds = getters.GET_currentSelectedElIds;
    selectedElIds.map(id => {
      state.workspaceContent[state.currentNetwork].networkElementList[id].layerMeta.position.top += toTop;
      state.workspaceContent[state.currentNetwork].networkElementList[id].layerMeta.position.left += toLeft;
    });
  },
  change_singleElementPosition(state, { id, top, left }) {
    state.workspaceContent[state.currentNetwork].networkElementList[id].layerMeta.position.top = top;
    state.workspaceContent[state.currentNetwork].networkElementList[id].layerMeta.position.left = left;
  },
  change_singleElementInSnapshotPosition(state, { snapshotId = 0, id, top, left }) {

    if (!state.workspaceContent[state.currentNetwork] ||
      !state.workspaceContent[state.currentNetwork].networkSnapshots ||
      !state.workspaceContent[state.currentNetwork].networkSnapshots.length === 0 ||
      !state.workspaceContent[state.currentNetwork].networkSnapshots[snapshotId][id]) {
      return;
    }

    state.workspaceContent[state.currentNetwork].networkSnapshots[snapshotId][id].layerMeta.position.top = top;
    state.workspaceContent[state.currentNetwork].networkSnapshots[snapshotId][id].layerMeta.position.left = left;
  },
  change_groupContainerDiff(state, { id, top, left }) {
    state.workspaceContent[state.currentNetwork].networkElementList[id].layerMeta.containerDiff.top = top;
    state.workspaceContent[state.currentNetwork].networkElementList[id].layerMeta.containerDiff.left = left;
  },
  set_elementInputDim(state, value) {
    for (let element in value) {
      if (!currentElement(element)) { return; }

      currentElement(element).layerMeta.InputDim = value[element].inShape;
      currentElement(element).layerCodeError = value[element].Error
    }
  },
  set_elementOutputDim(state, { value }) {
    for (let element in value) {
      if (!currentElement(element)) { continue; }

      currentElement(element).layerMeta.OutputDim = value[element].Dim;
      currentElement(element).layerCodeError = value[element].Error
    }
  },
  SET_webLoadingDataFlag(state, value) {
    state.webLoadingDataFlag = value
  },

  //---------------
  //  NETWORK CONTAINER
  //---------------
  add_container(state, { getters, commit, dispatch }) {
    let arrSelect = getters.GET_currentSelectedEl;
    let isValid = true;
    let elementList = getters.GET_currentNetworkElementList;
    let containersArray = [];
    let parentContainerID = arrSelect.length ? arrSelect[0].parentContainerID : null;
    /* validations */
    if (arrSelect.length === 0) isValid = false;
    if (arrSelect.length === 1) {
      dispatch('globalView/GP_infoPopup', 'At least two elements are needed to create a group', { root: true });
      isValid = false;
    }
    if (!isValid) {
      dispatch('SET_elementUnselect');
      return;
    }

    // Check if the item is a part of the same container or outside any container
    const selectedItemsParentContainerId = arrSelect.every(net => net.parentContainerID === arrSelect[0].parentContainerID);
    // console.log(arrSelect.map(net => net.parentContainerID));
    if (selectedItemsParentContainerId) {
      if (arrSelect[0].parentContainerID !== undefined) {
        if (Object.keys(elementList[arrSelect[0].parentContainerID].containerLayersList).length === arrSelect.length) {
          dispatch('globalView/GP_infoPopup', 'Not all items inside a group can be grouped', { root: true });
          dispatch('SET_elementUnselect');
          return;
        }
      }

    } else {
      // Check if selected items are all items inside a group
      dispatch('globalView/GP_infoPopup', 'Only items belonging to the container can be grouped', { root: true });
      dispatch('SET_elementUnselect');
      return;
    }

    /* END validations */
    let newContainer = createClearContainer(arrSelect);
    updateLayerName(newContainer, elementList, 1);
    // creation of group inside another group
    if (parentContainerID) {
      Vue.set(state.workspaceContent[state.currentNetwork].networkElementList[parentContainerID].containerLayersList, newContainer.layerId, newContainer.layerId);
      Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newContainer.layerId, newContainer);
    } else {
      Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newContainer.layerId, newContainer);
    }

    commit('close_container', { container: newContainer, getters, dispatch });
    commit('set_elementUnselect', { getters });

    function createClearContainer(selectList) {
      let parentContainerId = selectList[0].parentContainerID
      arrSelect.forEach(element => {
        // remove parentContainerId from selected elements
        if (parentContainerId) {
          delete state.workspaceContent[state.currentNetwork].networkElementList[parentContainerId].containerLayersList[element.layerId]
        }
        // attach to new created Container
      });

      let fakeEvent = {
        timeStamp: generateID(),
        target: {
          dataset: {
            layer: 'Layer Container',
            type: 'Container',
            component: 'LayerContainer',
          },
          clientHeight: 0,
          clientWidth: 0
        }
      };
      let container = createNetElement(fakeEvent);
      container.containerLayersList = {};
      container.isShow = true;
      // add parentContainerID to new created container
      if (parentContainerID) {
        container.parentContainerID = parentContainerID
      }
      selectList.forEach((el) => {
        el.parentContainerID = container.layerId;
        container.containerLayersList[el.layerId] = el.layerId;
      });
      return container
    }
  },
  close_container(state, { container, getters, dispatch }) {
    let network = getters.GET_currentNetworkElementList;
    let layerCont = calcContainer(network[container.layerId], network);
    saveDifferentPosition(layerCont);

    for (let idEl in layerCont.containerLayersList) {
      network[idEl].layerNone = true;
    }
    network[container.layerId].layerNone = false;

    closeChildContainer(layerCont);

    dispatch('mod_events/EVENT_calcArray', null, { root: true });


    function closeChildContainer(container) {
      const layerListKeys = Object.keys(container.containerLayersList);
      layerListKeys.forEach(id => {
        const element = network[id];
        if (element.componentName === 'LayerContainer') {
          element.isShow = false;
          for (let idEl in element.containerLayersList) {
            const childElement = network[idEl];
            childElement.layerNone = true;
            if (childElement.componentName === 'LayerContainer') {
              childElement.isShow = false;
            }
          }
          closeChildContainer(element)
        }
      });
    }

    function calcContainer(container, net) {
      let el = network[container.layerId];
      let listInside = el.containerLayersList;
      let allIdEl = [];
      let allIdOut = [];
      let allIdIn = [];
      let allTop = [];
      let allLeft = [];

      for (let elID in listInside) {
        let item = network[elID];
        allIdEl.push(elID);
        allIdOut = [...allIdOut, ...new Set(item.connectionOut)];
        allIdIn = [...allIdIn, ...new Set(item.connectionIn)];
        allTop.push(item.layerMeta.position.top);
        allLeft.push(item.layerMeta.position.left);
      }

      el.layerMeta.position.top = calcPosition(allTop);
      el.layerMeta.position.left = calcPosition(allLeft);
      el.connectionOut = calcConnection(allIdOut, allIdEl);
      el.connectionArrow = [...new Set(el.connectionOut)];
      el.connectionIn = calcConnection(allIdIn, allIdEl);

      el.connectionIn.forEach((elNextId) => {
        if (!net[elNextId].connectionArrow.includes(el.layerId)) {
          net[elNextId].connectionArrow.push(el.layerId)
        }
        for (let elID in net) {
          let item = net[elID];
          if (item.componentName === 'LayerContainer') {
            let arrKeys = Object.keys(item.containerLayersList);
            if (arrKeys.includes(elNextId) && !item.connectionArrow.includes(el.layerId)) {
              item.connectionArrow.push(el.layerId)
            }
          }
        }
      });
      el.connectionOut.forEach((elNextId) => {
        for (let elID in net) {
          let item = net[elID];
          if (item.componentName === 'LayerContainer') {
            let arrKeys = Object.keys(item.containerLayersList);
            if (arrKeys.includes(elNextId) && !el.connectionArrow.includes(item.layerId)) {
              el.connectionArrow.push(item.layerId)
            }
          }
        }
      });
      return el;


      function calcConnection(arrConnectionId, arrInsideId) {
        return arrConnectionId.filter((id) => !arrInsideId.includes(id))
      }
      function calcPosition(arrIn) {
        const num = (Math.max(...arrIn) + Math.min(...arrIn)) / 2;
        return calcLayerPosition(num);
      }
    }
    function saveDifferentPosition(containerEl) {
      let listInside = containerEl.containerLayersList;
      let containerTop = containerEl.layerMeta.position.top;
      let containerLeft = containerEl.layerMeta.position.left;
      for (let elID in listInside) {
        let item = network[elID];
        let itemTop = item.layerMeta.position.top;
        let itemLeft = item.layerMeta.position.left;
        item.layerMeta.containerDiff.top = itemTop - containerTop;
        item.layerMeta.containerDiff.left = itemLeft - containerLeft;
      }
    }

  },
  open_container(state, { container, getters, dispatch, commit }) {
    let net = getters.GET_currentNetworkElementList;
    calcLayerPosition(container);

    for (let idEl in container.containerLayersList) {
      net[idEl].layerNone = false;
    }
    net[container.layerId].layerNone = true;

    showChildContainer(container);

    dispatch('mod_events/EVENT_calcArray', null, { root: true });
    dispatch('SET_isOpenElement', false);
    function showChildContainer(container) {
      const layerListKeys = Object.keys(container.containerLayersList);
      layerListKeys.forEach(id => {
        const element = net[id];
        if (element.componentName === 'LayerContainer') {
          element.isShow = true;
        }
      });

    }
    function calcLayerPosition(containerEl) {
      let listInside = containerEl.containerLayersList;
      let containerTop = containerEl.layerMeta.position.top;
      let containerLeft = containerEl.layerMeta.position.left;
      for (let elID in listInside) {
        let netEl = net[elID];
        // let item = listInside[elID];
        let diffTop = netEl.layerMeta.containerDiff.top;
        let diffLeft = netEl.layerMeta.containerDiff.left;
        // item.layerMeta.position.top = diffTop + containerTop;
        netEl.layerMeta.position.top = diffTop + containerTop;
        // item.layerMeta.position.left = diffLeft + containerLeft;
        netEl.layerMeta.position.left = diffLeft + containerLeft;
      }
    }
  },
  toggle_container(state, { val, container, dispatch, getters }) {
    val
      ? dispatch('CLOSE_container', container)
      : dispatch('OPEN_container', container);
    if (getters.GET_networkIsOpen) dispatch('SET_elementUnselect');
  },
  ungroup_container(state, { dispatch, getters, container: passedContainer }) {
    let net = { ...getters.GET_currentNetworkElementList };
    let linkNet = getters.GET_currentNetworkElementList;
    let selectedEl = getters.GET_currentSelectedEl[0];
    let container = selectedEl || passedContainer;
    if (!(container.layerType === 'Container')) {
      console.error("It's not a container");
      return;
    }
    dispatch('SET_elementUnselect');

    const parentContainerId = net[container.layerId].parentContainerID;
    const containerId = container.layerId;


    let childContainersIds = []
    let childElementsIds = [];
    selectChildContainers({ [container.layerId]: container.layerId });
    function selectChildContainers(elements) {
      for (let id in elements) {
        let element = linkNet[id];
        if (element.layerType === 'Container') {
          selectChildContainers(element.containerLayersList)
          childContainersIds.push(element.layerId)
        } else {
          childElementsIds.push(element.layerId)
        }
      }
    }



    if (parentContainerId) {
      delete linkNet[container.parentContainerID].containerLayersList[container.layerId];
    }

    for (let position in childContainersIds) {
      dispatch('OPEN_container', linkNet[childContainersIds[position]]);
    }


    for (let position in childElementsIds) {
      let el = linkNet[childElementsIds[position]];
      if (parentContainerId) {
        el.parentContainerID = parentContainerId;
        linkNet[parentContainerId].containerLayersList[childElementsIds[position]] = childElementsIds[position];
      } else {
        delete el.parentContainerID
      }
    }



    for (let idEl in linkNet) {
      let el = net[idEl];
      el.connectionArrow = el.connectionArrow.filter((arrow) => arrow !== container.layerId)
      // delete el.layerContainerID;
    }

    // for(let elId in container.containerLayersList) {
    //   net[elId].parentContainerID = container.parentContainerID;
    //   if(container.parentContainerID){
    //     debugger;
    //     net[container.parentContainerID].containerLayersList[elId] = elId;
    //   }
    // }
    for (let position in childContainersIds) {
      delete linkNet[childContainersIds[position]];
    };

    if (parentContainerId) {
      dispatch('CLOSE_container', linkNet[container.parentContainerID]);
      dispatch('OPEN_container', linkNet[container.parentContainerID]);
    }
    // state.workspaceContent[state.currentNetwork].networkElementList = linkNet;
    let newMockNet = deepCloneNetwork(linkNet);
    state.workspaceContent[state.currentNetwork].networkElementList = newMockNet;
  },
  //---------------
  //  OTHER
  //---------------
  set_currentNetwork(state, tabIndex) {
    state.currentNetwork = tabIndex;
  },
  set_currentModelIndex(state, tabIndex) {
    state.currentModelIndex = tabIndex;
  },
  set_currentModelIndexByNetworkId(state, networkId) {
    const idx = state.workspaceContent.findIndex(wc => wc.networkID == networkId);
    state.currentModelIndex = idx;
  },
  set_currentStatsIndex(state, tabIndex) {
    state.currentStatsIndex = tabIndex;
  },
  set_currentTestIndex(state, tabIndex) {
    state.currentTestIndex = tabIndex;
  },
  ADD_dragElement(state, event) {
    state.dragElement = createNetElement(event);
  },
  SET_startArrowID(state, value) {
    state.startArrowID = value
  },
  SET_preArrowStart(state, value) {
    state.preArrow.start = value;
    state.preArrow.stop = value;
    state.preArrow.show = true;
  },
  SET_preArrowStop(state, value) {
    state.preArrow.stop = value
  },
  CLEAR_preArrow(state) {
    state.preArrow = {
      show: false,
      start: { x: 0, y: 0 },
      stop: { x: 0, y: 0 },
    }
  },
  set_isOpenElement(state, value) {
    state.isOpenElement = value
  },
  set_historyStep(state, { value, dispatch }) {
    state.workspaceContent[state.currentNetwork].networkName = value.networkName;
    state.workspaceContent[state.currentNetwork].networkElementList = value.networkElementList;
  },
  markAllUnselectedMutation(state) {
    const networkElementList = state.workspaceContent[state.currentNetwork].networkElementList;
    Object.keys(networkElementList).map(key => {
      networkElementList[key].layerMeta.isSelected = false;
    });
  },
  updateDragBoxContainerMutation(state, value) {
    state.dragBoxContainer = {
      ...state.dragBoxContainer,
      ...value
    }
  },
  SET_NetworkChartDataMutation(state, { layerId, payload }) {

    if (!state.workspaceContent[state.currentNetwork] ||
      !state.workspaceContent[state.currentNetwork].networkElementList ||
      !state.workspaceContent[state.currentNetwork].networkElementList[layerId]) { return; }

    const el = state.workspaceContent[state.currentNetwork].networkElementList[layerId];

    if (el.hasOwnProperty('chartData')) {
      state.workspaceContent[state.currentNetwork].networkElementList[layerId]['chartData'] = payload;
    } else {
      state.workspaceContent[state.currentNetwork].networkElementList[layerId] = {
        ...state.workspaceContent[state.currentNetwork].networkElementList[layerId],
        chartData: {},
      };
      Vue.set(state.workspaceContent[state.currentNetwork].networkElementList[layerId], 'chartData', payload);
    }
  },
  SET_NetworkChartIdxMutation(state, { layerId, payload }) {

    if (!state.workspaceContent[state.currentNetwork] ||
      !state.workspaceContent[state.currentNetwork].networkElementList ||
      !state.workspaceContent[state.currentNetwork].networkElementList[layerId]) { return; }

    const el = state.workspaceContent[state.currentNetwork].networkElementList[layerId];

    Vue.set(state.workspaceContent[state.currentNetwork].networkElementList[layerId], 'chartIdx', payload);
  },
  //---------------
  // INPUT / OUTPUT variables handlers
  //---------------
  SET_outputVariableMutation(state, { ctx, payload }) {
    let el = currentElement(payload.layerId).outputs[payload.outputVariableId]
    el.reference_var = payload.variableName;
    el.name = payload.variableName;
  },
  ADD_outputVariableMutation(state, payload) {
    let el = currentElement(payload.layerId)
    Vue.set(el.outputs, generateID(), {
      reference_var: 'output',
      name: 'output'
    });
  },
  DELETE_outputVariableMutation(state, { payload, getters, dispatch }) {
    let el = currentElement(payload.layerId);
    let net = getters.GET_currentNetworkElementList;

    for (let elId in net) {
      let el = net[elId];
      let inputs = el.inputs;

      for (let inputId in inputs) {
        const reference_var_id = inputs[inputId].reference_var_id;
        if (reference_var_id === payload.outputVariableId) {
          inputs[inputId].reference_var_id = null;
          inputs[inputId].reference_layer_id = null;
        }
      }

    }
    dispatch('mod_events/EVENT_calcArray', null, { root: true });
    Vue.delete(el.outputs, [payload.outputVariableId]);
  },

  EDIT_inputVariableValue(state, { payload, dispatch }) {
    let el = currentElement(payload.layerId).inputs[payload.inputVariableId];
    el.name = payload.value;
  },
  ADD_inputVariableMutation(state, { payload, dispatch }) {
    let el = currentElement(payload.layerId)
    Vue.set(el.inputs, generateID(), {
      name: payload.name || "input",
      reference_var_id: payload.reference_var_id || null,
      reference_layer_id: payload.reference_layer_id || null,
    });
    dispatch('mod_events/EVENT_calcArray', null, { root: true });
  },
  DELETE_inputVariableMutation(state, { payload, dispatch }) {
    let el = currentElement(payload.layerId);
    dispatch('mod_events/EVENT_calcArray', null, { root: true });
    Vue.delete(el.inputs, [payload.inputVariableId]);
  },

  SET_unparsedModels(state, { payload }) {
    state.unparsedModels = payload.unparsedModels;
  },

  toggle_showModelPreviewsMutation(state, payload) {
    localStorage.setItem(LOCAL_STORAGE_WORKSPACE_SHOW_MODEL_PREVIEWS, payload);
    state.showModelPreviews = payload;
  },
  toggleModelWeightsState(state, { networkId, value }) {

    const network = state.workspaceContent.find(wc => wc.networkID === networkId);
    if (!network) { return; }

    Vue.set(network.networkMeta, 'usingWeights', value);
  },
  setChartComponentLoadingStateMutation(state, { descendants, value, getters, networkId }) {
    if (!getters.GET_networkByNetworkId(networkId)) { return; }
    const networkList = getters.GET_networkByNetworkId(networkId).networkElementList;

    descendants.forEach(componentId => {
      if (networkList[componentId] && networkList[componentId].chartDataIsLoading !== undefined) {
        if (value) { // is should increment
          networkList[componentId].chartDataIsLoading += 1
        } else if (networkList[componentId].chartDataIsLoading > 0) {
          networkList[componentId].chartDataIsLoading -= 1
        }
      } else {
        // is triggered when network component haven't this field
        if (value) {
          Vue.set(networkList[componentId], 'chartDataIsLoading', 1);
        }
      }
    })
  },
  setNetworkElementDefaultSettingMutation(state, { layerId, getters }) {
    const el = getters.GET_networkElementById(layerId)
    const initialSettings = el.layerSettings
    Vue.set(el, 'initialSettings', initialSettings);
  },
  resetNetworkElementSettingsMutation(state, { layerId, getters, dispatch }) {
    const el = getters.GET_networkElementById(layerId);
    el.layerSettings = el.initialSettings;
    el.visited = false;
    el.layerCode = null; // is set null for fetching new code of component

    dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', layerId, { root: true });
    dispatch('mod_events/EVENT_componentEvent_model_resetSettingClick', null, { root: true });
    dispatch('lockNetworkElementSettings', { layerId, value: false });
  },
  lockNetworkElementSettingsMutation(state, { getters, layerId, value }) {
    const el = getters.GET_networkElementById(layerId);
    Vue.set(el, 'isSettingsLocked', value);
  },
  SET_copyOrCutNetworkSnapshot(state, { getters }) {
    state.copyOrCutNetworkSnapshot = deepCloneNetwork(getters.GET_currentNetworkElementList);
  },
  set_trainingSettings(state, { currentNetwork, defaultTrainingSettings }) {
    let settings = deepCopy(defaultTrainingSettings);

    delete settings['OptimizerOptions'];
    delete settings['LossOptions'];
    Vue.set(currentNetwork.networkMeta, 'trainingSettings', settings);
  },
  setModelRunSettingsMutation(state, { name, value, currentNetwork }) {
    currentNetwork.networkMeta.trainingSettings[name] = value;
  },
};



const actions = {
  EDIT_inputVariableValueAction({ dispatch, commit }, payload) {
    commit('EDIT_inputVariableValue', { payload, dispatch });
  },
  SET_unparsedModels({ commit }, payload) {
    commit('SET_unparsedModels', { payload });
  },
  DELETE_outputVariableAction({ getters, commit, dispatch }, payload) {
    let net = getters.GET_currentNetworkElementList;

    let layerIdsWithReference = [];

    for (let elId in net) {
      let el = net[elId];
      let inputs = el.inputs;

      for (let inputId in inputs) {
        const reference_var_id = inputs[inputId].reference_var_id;
        if (reference_var_id === payload.outputVariableId) {
          layerIdsWithReference.push(elId);
        }
      }
    }

    commit('DELETE_outputVariableMutation', { payload, getters, dispatch });


    // if(layerIdsWithReference.length > 0) {
    //     for(let ix in layerIdsWithReference) {
    //       debugger;
    //         dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants_test', layerIdsWithReference[ix], { root: true });
    //     }
    //   }
    return layerIdsWithReference;
  },
  ADD_inputVariableAction({ dispatch, commit }, payload) {
    commit("ADD_inputVariableMutation", { payload, dispatch });
  },
  DELETE_inputVariableAction({ dispatch, commit }, payload) {
    commit('DELETE_inputVariableMutation', { payload, dispatch });
  },
  cleanupUnnecessaryArrowsAction({ getters }) {
    commit('cleanupUnnecessaryArrowsMutation', { getters })
  },
  updateForwardBackwardConnectionsAction({ commit, getters }, payload) {

    console.error("updateForwardBackwardConnectionsAction", payload);
    commit('updateForwardBackwardConnectionsMutation', { getters, payload })
  },
  //---------------
  //  NETWORK
  //---------------
  ReplaceNetworkElementList({ commit, getters }, newNetworkElementList) {
    commit('replace_network_element_list', { newNetworkElementList, getters });
  },
  ADD_network({ commit, dispatch }, { newNetwork, apiMeta = {}, focusOnNetwork = true } = {}) {

    return new Promise((resolve, reject) => {
      commit('add_network', { newNetwork, apiMeta, dispatch, focusOnNetwork });
      const lastNetworkID = state.workspaceContent[state.currentNetwork].networkID;

      if (focusOnNetwork) {
        commit('set_lastActiveTabInLocalStorage', lastNetworkID);
      }
      return resolve();
    });
  },
  UPDATE_currentNetwork({ commit, dispatch, getters }, newNetwork) {
    return new Promise((resolve) => {
      const currentNetworkId = getters.GET_currentNetworkId;
      commit('update_network', { networkId: currentNetworkId, newNetwork });

      return resolve();
    })
  },
  ADD_existingNetworkToWorkspace({ commit, dispatch }, { network } = {}) {
    if (!network) { return; }
    return new Promise(resolve => {
      commit('add_existingNetworkToWorkspace', { network });
      resolve();
    });
  },
  DELETE_networkById({ commit, dispatch }, networkId) {
    return new Promise(resolve => {

      const index = state.workspaceContent.findIndex(wc => wc.networkID == networkId);
      if (index === -1) { return; }

      // API_closeCore stops the process in the core
      dispatch('mod_api/API_closeCore', networkId, { root: true });

      if (index === state.currentNetwork) {

        if (state.workspaceContent.length === 1) {
          commit('set_lastActiveTabInLocalStorage', '');
        } else if (index === 0) {
          commit('set_lastActiveTabInLocalStorage', state.workspaceContent[index + 1].networkID);
        } else {
          commit('set_lastActiveTabInLocalStorage', state.workspaceContent[index - 1].networkID);
        }
      }
      const modelApiMeta = state.workspaceContent[index].apiMeta;
      // deleting in rygg
      dispatch('mod_project/deleteModel', modelApiMeta, { root: true });
      dispatch('mod_tracker/EVENT_modelDeletion', null, { root: true });
      commit('delete_networkById', networkId);
      dispatch('mod_datasets/deleteModel', networkId, { root: true });
      resolve();
    })
  },
  UNREGISTER_networkById({ commit, dispatch }, networkId) {
    return new Promise(resolve => {
      const index = state.workspaceContent.findIndex(wc => wc.networkID == networkId);
      if (index === -1) { return; }

      // API_closeCore stops the process in the core
      dispatch('mod_api/API_closeCore', networkId, { root: true });

      if (index === state.currentNetwork) {

        if (state.workspaceContent.length === 1) {
          commit('set_lastActiveTabInLocalStorage', '');
        } else if (index === 0) {
          commit('set_lastActiveTabInLocalStorage', state.workspaceContent[index + 1].networkID);
        } else {
          commit('set_lastActiveTabInLocalStorage', state.workspaceContent[index - 1].networkID);
        }
      }
      const modelApiMeta = state.workspaceContent[index].apiMeta;

      // deleting in rygg
      dispatch('mod_project/deleteModel', modelApiMeta, { root: true });
      dispatch('mod_datasets/unregisterModel', networkId, { root: true });
      commit('unregister_networkById', networkId);
      resolve();
    })
  },
  markAllUnselectedAction({ commit }) {
    commit('markAllUnselectedMutation');
  },
  setStatisticsAvailability({ getters, commit, dispatch, state }) {
    if (!getters.GET_networkIsNotEmpty) { return; }
    const networksInProject = getters.GET_networksInCurrentProject;

    const isTrainedPromises = [];

    for (const n of networksInProject) {
      const isTrainedPromise = dispatch('mod_api/API_checkTrainedNetwork', n.networkID, { root: true });

      isTrainedPromises.push(isTrainedPromise);
    }

    return Promise.all(isTrainedPromises)
      .then(results => {
        const setStatisticsPromises = [];

        for (const r of results) {
          if (r) {
            const setStatisticsPromise = dispatch('SET_openStatisticsByNetworkId',
              {
                networkId: r.receiver,
                value: r.result || null
              });

            setStatisticsPromises.push(setStatisticsPromise);
          }
        }

        if (Array.from(results).some((r) => r && r.result && r.result.content)) {
          dispatch('mod_empty-navigation/SET_emptyScreenMode', 0, { root: true })
        }

        return Promise.all(setStatisticsPromises)
          .then(() => {
            return results;
          })
      });

  },
  setCheckpointAvailability({ getters, commit, dispatch, state }) {

    if (!getters.GET_networkIsNotEmpty) { return; }

    // Calls the kernel and asks which of the networks have checkpoints.

    const networksInProject = getters.GET_networksInCurrentProject;
    const scanCheckpointPromises = [];

    for (const n of networksInProject) {
      const promise = dispatch('mod_api/API_scanCheckpoint', {
        networkId: n.networkID,
        path: n.apiMeta.location
      }, { root: true });

      scanCheckpointPromises.push(promise)
    }

    return Promise.all(scanCheckpointPromises)
      .then(results => {
        // for (const r of results) {
        //   r.networkName = networksInProject.find(n => n.networkID === r.networkId).networkName;
        // }

        const setTestPromises = [];

        for (const r of results) {
          // if (!r.hasCheckpoint) { continue; }

          const setTestPromise = dispatch('SET_openTestByNetworkId',
            {
              networkId: r.networkId,
              value: r.hasCheckpoint
            });

          setTestPromises.push(setTestPromise);
        }

        return Promise.all(setTestPromises)
          .then(() => {
            return results;
          })
      });
  },
  SET_chartsRequestsIfNeeded({ state, dispatch }, networkID) {
    // This function is used to determine if the page has been refreshed after the training
    // has started, but before it is completed.
    const network = state.workspaceContent.find(network => network.networkID === networkID);

    // console.group('SET_chartsRequestsIfNeeded');
    // console.log('stats tab', network.networkMeta.openStatistics);
    // console.log('test tab', network.networkMeta.openTest);
    // console.log('networkWaitGlobalEvent', network.networkMeta.chartsRequest.waitGlobalEvent);
    // console.groupEnd();

    // skip if:
    // network never trained before
    // if there's already a valid timerID
    if (!network ||
      network.networkMeta.openStatistics == null ||
      network.networkMeta.chartsRequest.timerID) { return; }

    // this check is only for the statistics tab
    dispatch('mod_api/API_checkNetworkRunning', networkID, { root: true })
      .then(({ content: isRunning }) => {
        if (isRunning && network.networkMeta.coreStatus && !['Stopped', 'Paused', 'Waiting', 'Finished'].includes(network.networkMeta.coreStatus.Status)) {
          //statistics still being computed and NOT paused
          dispatch('EVENT_startDoRequest', true);
        } else {
          dispatch('EVENT_onceDoRequest', true);
        }
      });
  },
  SET_currentNetwork({ commit }, index) {
    commit('set_currentNetwork', index);
    commit('set_lastActiveTabInLocalStorage', state.workspaceContent[index].networkID);
    return Promise.resolve();
  },
  SET_currentModelIndex({ commit }, index) {
    commit('set_currentModelIndex', index);
  },
  SET_currentModelIndexByNetworkId({ commit }, networkId) {
    return new Promise(resolve => {
      commit('set_currentModelIndexByNetworkId', networkId);
      resolve();
    });
  },
  SET_currentStatsIndex({ commit }, index) {
    commit('set_currentStatsIndex', index);
  },
  SET_currentTestIndex({ commit }, index) {
    commit('set_currentTestIndex', index);
  },

  SET_networkName({ commit, getters, dispatch }, value) {
    commit('set_networkName', { getters, value })
    let currentNetwork = JSON.parse(JSON.stringify(getters.GET_currentNetwork.apiMeta));
    currentNetwork.name = value;
    delete currentNetwork.saved_by;
    delete currentNetwork.saved_version_location;
    delete currentNetwork.created;
    delete currentNetwork.updated;
    dispatch("mod_project/updateModel", currentNetwork, { root: true });
  },
  SET_networkLocation({ commit, getters, dispatch }, value) {
    commit('set_model_location', { location: value, getters });
    let currentNetwork = JSON.parse(JSON.stringify(getters.GET_currentNetwork.apiMeta));
    currentNetwork.location = value;
    delete currentNetwork.saved_by;
    delete currentNetwork.saved_version_location;
    delete currentNetwork.created;
    delete currentNetwork.updated;
    dispatch("mod_project/updateModel", currentNetwork, { root: true });
  },
  SET_networkRootFolder({ commit, getters }, value) {
    commit('set_networkRootFolder', { getters, value })
  },
  SET_networkElementList({ commit, getters }, value) {
    commit('set_networkElementList', { getters, value })
  },
  SET_netMode({ commit, getters }, value) {
    commit('set_netMode', { getters, value })
  },
  SET_openStatistics({ commit, getters, dispatch }, value) {
    commit('set_openStatistics', { dispatch, getters, value })
  },
  SET_openStatisticsByNetworkId({ commit, getters, dispatch }, { networkId, value }) {
    commit('set_openStatisticsByNetworkId', { dispatch, getters, networkId, value })
  },
  SET_openTest({ commit, getters, dispatch }, value) {
    commit('set_openTest', { dispatch, getters, value })
  },
  SET_openTestByNetworkId({ commit, getters, dispatch }, { networkId, value }) {
    commit('set_openTestByNetworkId', { dispatch, getters, networkId, value })
  },
  SET_statisticsAndTestToClosed({ commit, getters }, { networkId }) {
    return new Promise(resolve => {
      commit('SET_statisticsAndTestToClosed', { getters, networkId });
      resolve();
    });
  },
  SET_networkSnapshot({ commit, getters, dispatch }) {
    return new Promise(resolve => {
      commit('set_networkSnapshot', { dispatch, getters });
      resolve();
    });
  },
  SET_statusNetworkCore({ commit, getters }, value) {
    commit('set_statusNetworkCore', { getters, value })
  },
  SET_layerTrainedStatus({ commit, getters }, { networkId, trainedLayers }) {

    if (!networkId || !trainedLayers) { return; }

    for (const layerId in trainedLayers) {
      commit('set_layerTrainedStatus', {
        getters,
        networkId,
        layerId,
        value: trainedLayers[layerId],
      });
    }
  },
  SET_statusNetworkCoreDynamically({ commit, getters, dispatch }, value) {
    const { modelId, ...payload } = value;
    commit('set_statusNetworkCoreDynamically', { getters, modelId, payload })
    dispatch('saveModelAction', modelId);
  },
  SET_statusNetworkCoreStatus({ commit, getters }, value) {
    commit('set_statusNetworkCoreStatus', { getters, value })
  },
  SET_statusNetworkCoreStatusProgressClear({ commit, getters }) {
    commit('set_statusNetworkCoreStatusProgressClear', { getters })
  },
  SET_statusNetworkZoom({ commit, getters }, value) {
    commit('set_statusNetworkZoom', { getters, value });
  },
  SET_statusNetworkWaitGlobalEvent({ commit, getters }, value) {
    commit('set_statusNetworkWaitGlobalEvent', { getters, value })
  },
  RESET_network({ commit }) {
    commit('reset_network')
  },
  CHECK_requestInterval({ dispatch, commit, rootState, getters, state }, time) {
    const timeRequest = time + 500;
    const isLongRequest = timeRequest > rootState.globalView.timeIntervalDoRequest;
    if (isLongRequest) {
      const currentMeta = getters.GET_currentNetwork.networkMeta.chartsRequest;
      clearInterval(currentMeta.timerID);
      dispatch('globalView/SET_timeIntervalDoRequest', timeRequest, { root: true });
      dispatch('EVENT_startDoRequest', true);
    }
  },
  EVENT_startDoRequest({ dispatch, commit, rootState, getters, state }, isStart) {
    const currentMeta = getters.GET_currentNetwork.networkMeta;
    if (currentMeta === undefined) return;
    const timeInterval = rootState.globalView.timeIntervalDoRequest;

    dispatch('SET_statusNetworkWaitGlobalEvent', isStart);
    if (isStart) {
      const networkIndex = getters.GET_currentNetworkIndex;
      let timerId = setInterval(() => {
        dispatch('EVENT_chartsRequest', { networkIndex });
      }, timeInterval);
      commit('set_charts_timerID', { getters, timerId });
    }
    else {
      clearInterval(currentMeta.chartsRequest.timerID);
      commit('set_charts_timerID', { getters, timerId: null })
    }
  },
  EVENT_stopRequest({ state, getters, commit }, { networkId }) {
    const networkIndex = state.workspaceContent.findIndex(net => net.networkID === networkId);

    if (networkIndex !== -1) {
      const networkMeta = state.workspaceContent[networkIndex].networkMeta;

      if (networkMeta.chartsRequest.timerID) {
        clearInterval(networkMeta.chartsRequest.timerID);
        commit('set_charts_timerID', { getters, timerId: null, networkIndex });
      }
    }
  },
  EVENT_chartsRequest({ dispatch, commit, rootState, getters, state }, payload) {
    var networkIndex = payload && payload.networkIndex !== undefined ? payload.networkIndex : state.currentNetwork;
    commit('set_charts_showCharts', { getters, networkIndex });
    commit('set_charts_doRequest', { getters, networkIndex });
    dispatch('mod_api/API_getStatus', { networkIndex }, { root: true });
  },
  EVENT_onceDoRequest({ dispatch, commit, rootState, getters }, isStart) {
    commit('set_charts_doRequest', { getters });
    dispatch('mod_api/API_getStatus', null, { root: true });
  },
  UPDATE_MODE_ACTION(ctx, { index, field, value }) {
    ctx.commit('update_model', { index, field, value });
  },
  set_NetworkCoreErrorAction(ctx, { errorMessage, modelId }) {
    ctx.commit('set_NetworkCoreError', { errorMessage, modelId, commit: ctx.commit });
  },
  SET_model_saved_version_location({ commit, getters }, saved_version_location) {
    commit('set_model_saved_version_location', { saved_version_location, getters })
  },
  //---------------
  //  NETWORK ELEMENTS
  //---------------
  updateNetworkElementPositions({ getters, commit }, { zoom = 1 }) {

    let elementList;
    let changePositionFunctionName;
    const oldZoom = getters.GET_currentNetworkZoom;
    const newZoom = zoom; // assigned to new so it's easier to read later on

    // choosing the right element list and commit functions
    if (getters.GET_statisticsOrTestIsOpen) {
      // update snapshot
      elementList = getters.GET_currentNetworkSnapshotElementList;
      if (!elementList) { return; }

      changePositionFunctionName = 'change_singleElementInSnapshotPosition';

      getters
    } else {
      // update normal
      elementList = getters.GET_currentNetworkElementList;
      changePositionFunctionName = 'change_singleElementPosition';
    }

    // performing the actual position update
    for (var el in elementList) {
      const element = elementList[el];
      const x0 = element.layerMeta.position.left;
      const y0 = element.layerMeta.position.top;

      commit(changePositionFunctionName, {
        id: el,
        top: y0 / oldZoom * newZoom,
        left: x0 / oldZoom * newZoom
      })
    }
  },
  SET_elementSettings({ commit, dispatch }, { settings, pushOntoHistory = false }) {

    commit('set_elementSettings', { dispatch, settings, pushOntoHistory })

    if (pushOntoHistory) {
      dispatch('mod_workspace-history/PUSH_newSnapshot', null, { root: true });
    }
  },
  ADD_element({ commit, getters, dispatch }, { event, setChangeToWorkspaceHistory = true, triggeredByHotKey }) {
    commit('add_element', { getters, dispatch, event, setChangeToWorkspaceHistory, triggeredByHotKey });

    dispatch('mod_workspace-changes/updateUnsavedChanges', {
      networkId: getters.GET_currentNetworkId,
      value: true
    }, { root: true });
  },
  DELETE_element({ commit, getters, dispatch }) {
    if (getters.GET_networkIsOpen) {
      commit('delete_element', { getters, dispatch });
    }

    dispatch('mod_workspace-changes/updateUnsavedChanges', {
      networkId: getters.GET_currentNetworkId,
      value: true
    }, { root: true });
  },
  ADD_arrow({ commit, getters, dispatch }, stopID) {
    commit('add_arrow', { dispatch, stopID })

    dispatch('mod_workspace-changes/updateUnsavedChanges', {
      networkId: getters.GET_currentNetworkId,
      value: true
    }, { root: true });
  },
  DELETE_arrow({ commit, getters, dispatch }, arrow) {
    commit('delete_arrow', { dispatch, arrow })
    dispatch('mod_workspace-changes/updateUnsavedChanges', {
      networkId: getters.GET_currentNetworkId,
      value: true
    }, { root: true });
  },
  SET_elementUnselect({ commit, getters }) {
    commit('set_elementUnselect', { getters })
  },
  SET_elementSelect({ commit, getters }, value) {
    commit('set_elementSelect', { value, getters })
  },
  SET_elementSelectAll({ commit, getters }) {
    if (getters.GET_enableHotKeyElement) commit('set_elementSelectAll', { getters })
  },
  SET_elementMultiSelect({ commit }, value) {
    commit('set_elementMultiSelect', value)
  },
  SET_elementInputDim({ commit }, value) {
    commit('set_elementInputDim', value)
  },
  SET_elementOutputDim({ commit, getters }, value) {
    commit('set_elementOutputDim', { getters, value })
  },
  CHANGE_elementPosition({ commit, getters, dispatch }, value) {
    commit('change_elementPosition', { value, getters })
  },
  afterNetworkElementIsDragged({ dispatch, getters }) {
  },
  //---------------
  //  NETWORK CONTAINER
  //---------------
  ADD_container({ commit, getters, dispatch }, event) {
    if (getters.GET_networkIsOpen) commit('add_container', { getters, commit, dispatch });
  },
  OPEN_container({ commit, getters, dispatch }, container) {
    commit('open_container', { commit, container, getters, dispatch })
  },
  CLOSE_container({ commit, getters, dispatch }, container) {
    commit('close_container', { container, getters, dispatch })
  },
  TOGGLE_container({ commit, getters, dispatch }, { val, container }) {
    commit('toggle_container', { val, container, dispatch, getters })
  },
  UNGROUP_container({ commit, getters, dispatch }, container) {
    if (getters.GET_networkIsOpen) commit('ungroup_container', { commit, container, dispatch, getters })
  },
  //---------------
  //  OTHER
  //---------------
  SET_isOpenElement({ commit }, value) {
    commit('set_isOpenElement', value)
  },
  SET_historyStep({ commit, dispatch }, value) {
    commit('set_historyStep', { value, dispatch });
  },
  SET_NetworkChartData({ commit }, { layerId, payload }) {
    if (payload.series) {
      payload.series = payload.series.map(series => {
        if (series.type === "rgba") {
          series.data = JSON.stringify(series.data);
        }
        return series;
      });
    }

    commit('SET_NetworkChartDataMutation', { layerId, payload });
  },
  SET_NetworkChartIdx({ commit }, { layerId, payload }) {
    commit('SET_NetworkChartIdxMutation', { layerId, payload });
  },

  //---------------
  // INPUT / OUTPUT variables handlers
  //---------------
  SET_outputVariableAction(ctx, payload) {
    ctx.commit('SET_previewVariable', { previewVariableName: payload.variableName, layerId: payload.layerId });
    ctx.commit('SET_outputVariableMutation', { ctx, payload });
  },
  TOGGLE_showModelPreviews(ctx) {
    ctx.commit('toggle_showModelPreviewsMutation', !ctx.state.showModelPreviews)
  },
  toggleModelWeightsState({ commit, getters }) {
    commit('toggleModelWeightsState', {
      networkId: getters.GET_currentNetworkId,
      value: !getters.GET_currentNetworkModeWeightsState
    })
  },
  setViewType({ dispatch, commit }, value) {
    return new Promise((resolve, reject) => {

      const possibleValues = ['model', 'statistic'];
      const isValidValue = possibleValues.includes(value);
      if (!isValidValue) { console.error(`View type can't have ${value} it should have one of ['model', 'statistic'']`) }
      //  should save it to local storage
      switch (value) {
        case 'model':
          dispatch('globalView/hideSidebarAction', true, { root: true });
          break;
        case 'statistic':
          dispatch('globalView/hideSidebarAction', false, { root: true });
          break;
      }

      commit('setViewTypeMutation', value);
      resolve();
    });
  },
  setChartComponentLoadingState({ getters, commit }, { descendants, value, networkId }) {
    commit('setChartComponentLoadingStateMutation', { getters, descendants, value, networkId });
  },
  SET_zoomToFitMapInStatistics({ getters, commit, dispatch }, payload) {
    const el = document.getElementsByClassName('the-network-field')[0];
    const window = el.getElementsByClassName('info-section_main')[0];

    const { offsetWidth, scrollWidth, offsetHeight, scrollHeight } = window;

    const wCoefficient = scrollWidth / 100;
    const wPercent = offsetWidth / wCoefficient;

    const hCoefficient = scrollHeight / 100;
    const hPercent = offsetHeight / hCoefficient;

    const decreasePercent = Math.min(hPercent, wPercent);

    const zoom = (1 - ((100 - decreasePercent) / 100)).toFixed(2);

    const shouldZoomOut = zoom !== '1.00';

    if (shouldZoomOut) {
      dispatch('updateNetworkElementPositions', { zoom });
      dispatch('SET_statusNetworkZoom', zoom);
    }
  },
  setNetworkElementDefaultSetting({ commit, getters }, { layerId }) {
    commit('setNetworkElementDefaultSettingMutation', { layerId, getters });
  },
  resetNetworkElementSettings({ commit, getters, dispatch }, { layerId }) {
    commit('resetNetworkElementSettingsMutation', { layerId, getters, dispatch });
  },
  lockNetworkElementSettings({ commit, getters }, { layerId, value }) {
    commit('lockNetworkElementSettingsMutation', { layerId, getters, value });
  },
  copyOrCutNetworkSnapshotAction({ commit, getters }) {
    commit('SET_copyOrCutNetworkSnapshot', { getters })
  },
  checkForRunSettingsAction({ commit, getters }, payload) {
    let currentNetwork = getters.GET_currentNetwork;
    // it will be set only once
    if (!currentNetwork.networkMeta.hasOwnProperty('trainingSettings')) {
      commit('set_trainingSettings', { currentNetwork, defaultTrainingSettings })
    }

  },
  setModelRunSettingsAction({ commit, dispatch, getters }, payload) {
    const currentNetwork = getters.GET_currentNetwork;
    if (currentNetwork.networkMeta.trainingSettings.hasOwnProperty(payload.name)) {
      commit('setModelRunSettingsMutation', { currentNetwork, name: payload.name, value: payload.value })
    }
  },
  UPDATE_all_previews({ getters, dispatch }) {
    const fullNetworkElementList = getters['GET_currentNetworkElementList'];
    let payload = {};
    for (let id in fullNetworkElementList) {
      payload[id] = fullNetworkElementList[id].previewVariable;
    }

    return dispatch('mod_api/API_getBatchPreviewSample', payload, { root: true });
  },
  saveCurrentModelAction({ dispatch, getters }) {
    const currentNetwork = getters['GET_currentNetwork'];
    const streamLinedNetwork = disassembleModel(currentNetwork);

    dispatch('mod_events/EVENT_saveNetwork', null, { root: true });
    return rygg_saveModelJson(streamLinedNetwork)
      .then(_ => {
        dispatch('SET_networkSnapshot'); // snapshot for the network in stats/test views
      })
      .then(_ => {
      });
  },
  saveModelAction({ dispatch, state }, modelId) {
    const networkIndex = state.workspaceContent.findIndex(net => net.networkID === modelId);
    const network = state.workspaceContent[networkIndex];
    const streamLinedNetwork = disassembleModel(network);

    return rygg_saveModelJson(streamLinedNetwork)
      .then(_ => {
      });
  }
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions,
}

function updateLayerName(el, net, n) {
  const layerName = el.layerName;
  if (net !== null) {
    let netArr = Object.values(net);
    if (findValue(netArr, layerName + '_' + n).length) {
      n++;
      updateLayerName(el, net, n);
    } else {
      el.layerName = layerName + '_' + n;
    }
    function findValue(arr, value) {
      return arr.filter(object => object.layerName.toLowerCase() === value.toLowerCase());
    }
  } else {
    el.layerName = layerName + '_' + n;
  }
}

function currentElement(id) {
  if (!state.workspaceContent[state.currentNetwork]) { return; }

  return state.workspaceContent[state.currentNetwork].networkElementList[id];
}
const createNetElement = function (event) {
  return {
    layerId: event.id || generateID(),
    copyId: event.target.dataset.copyId || null,
    copyContainerElement: event.target.dataset.copyContainerElement || null,
    layerName: event.target.dataset.layer,
    layerType: event.target.dataset.type,
    layerSettings: event.layerSettings ? event.layerSettings : null,
    layerSettingsTabName: event.layerSettingsTabName || undefined,
    layerCode: event.layerCode || null,
    layerCodeError: null,
    layerNone: false,
    layerMeta: {
      isInvisible: false,
      isLock: false,
      isSelected: false,
      position: {
        top: event.target.clientHeight / 2,
        left: event.target.clientWidth / 2,
      },
      tutorialId: '',
      OutputDim: '',
      InputDim: '',
      layerContainerName: '',
      layerBgColor: '',
      containerDiff: {
        top: 0,
        left: 0,
      }
    },
    chartData: {},
    checkpoint: [],
    endPoints: [],
    componentName: event.target.dataset.component,
    connectionOut: [],
    connectionIn: [],
    connectionArrow: [],
    visited: false,
    inputs: getComponentInputs(event.target.dataset.component),
    outputs: getComponentOutputs(event.target.dataset.component),
    forward_connections: [],
    backward_connections: [],
    previewVariable: 'output',
    previewVariableList: [],
    isTrained: false,
    isSettingsLocked: event.isSettingsLocked || false,
  };
};

const componentsInputs = {
  DataData: [],
  DataEnvironment: [],
  DataRandom: [],

  ProcessReshape: ['input'],
  ProcessGrayscale: ['input'],
  ProcessOneHot: ['input'],
  ProcessRescale: ['input'],

  DeepLearningFC: ['input'],
  DeepLearningConv: ['input'],
  DeepLearningRecurrent: ['input'],

  MathMerge: ['input1', 'input2'],
  MathSwitch: ['input1', 'input2'],

  TrainNormal: ['predictions', 'labels'],
  TrainRegression: ['predictions', 'labels'],
  TrainReinforce: ['action'],
  TrainGan: ['input'],
  TrainDetector: ['predictions', 'labels'],
  LayerCustom: ['input'],

  LayerTfModel: ['input'],
  LayerObjectDetectionModel: ['input'],

  PreTrainedMobileNetV2: ['input'],
  PreTrainedResNet50: ['input'],
  PreTrainedVGG16: ['input'],
  PreTrainedInceptionV3: ['input'],
  UNet: ['input'],

  IoInput: [],
  IoOutput: ['input']
};


const componentsOutputs = {
  DataData: ['output'],
  DataEnvironment: ['output'],
  DataRandom: ['output'],

  ProcessReshape: ['output'],
  ProcessGrayscale: ['output'],
  ProcessOneHot: ['output'],
  ProcessRescale: ['output'],

  DeepLearningFC: ['output'],
  DeepLearningConv: ['output'],
  DeepLearningRecurrent: ['output'],

  MathMerge: ['output'],
  MathSwitch: ['output'],
  LayerCustom: ['output'],

  TrainNormal: [],
  TrainRegression: [],
  TrainReinforce: [],
  TrainGan: [],
  TrainDetector: [],

  LayerTfModel: ['output'],
  LayerObjectDetectionModel: ['output'],

  PreTrainedMobileNetV2: ['output'],
  PreTrainedVGG16: ['output'],
  PreTrainedInceptionV3: ['output'],
  PreTrainedResNet50: ['output'],
  UNet: ['output'],

  IoInput: ['output'],
  IoOutput: []
};


const getComponentInputs = (componentName) => {
  let inputs = {};
  const inputVariableArray = componentsInputs[componentName];
  if (inputVariableArray && inputVariableArray.length > 0) {
    inputVariableArray.map((inputName, index) => {
      let input = {
        name: inputName,
        reference_var_id: null,
        reference_layer_id: null,
        isDefault: true
      }
      inputs[Date.now().toString() + index] = input;
    })
  }
  return inputs;

}
const getComponentOutputs = (componentName) => {
  let outputs = {};
  const outputVariableArray = componentsOutputs[componentName];
  if (outputVariableArray && outputVariableArray.length > 0) {
    outputVariableArray.map((outputName, index) => {
      let output = {
        name: outputName,
        reference_var: outputName,
      }
      outputs[[Date.now().toString() + index]] = output;
    })
  }
  return outputs;
}
