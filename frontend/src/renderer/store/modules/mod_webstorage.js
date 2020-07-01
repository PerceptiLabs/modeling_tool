import idb from '@/core/helpers/idb-helper.js';
import { deepCloneNetwork } from '@/core/helpers.js';

const namespaced = true;

const state = {};

const getters = {};

const mutations = {};

const actions = {
  async saveNetwork(ctx, network) {
    if (!network || !network.networkID) { return; }
    
    await idb.saveModel(deepCloneNetwork(network));
  },
  async updateIds(ctx) {

    
    const workspaces = ctx.rootState.mod_workspace.workspaceContent || [];
    let networkIDs = workspaces.map(ws => ws.networkID);

    networkIDs = networkIDs.filter(onlyUnique);
    await idb.setIds(networkIDs);

    function onlyUnique(value, index, self) { 
      return self.indexOf(value) === index;
    }
  },
  async updateWorkspaces(ctx) {

    let networkIDs = [];

    const workspaces = ctx.rootState.mod_workspace.workspaceContent || [];
    for(const ws of workspaces) {
      networkIDs.push(ws.networkID);
      await idb.saveModel(deepCloneNetwork(ws));
    };

    networkIDs = networkIDs.filter(onlyUnique);
    await idb.setIds(networkIDs);

    function onlyUnique(value, index, self) { 
      return self.indexOf(value) === index;
    }
  },
  async loadWorkspaces(ctx) {
    let networkIdsToLoad = await idb.getIds() || [];
    networkIdsToLoad = networkIdsToLoad.sort((a,b) => a - b)
    const networks = await idb.getModels(networkIdsToLoad);
    
    for(const network of networks) {

      // remove focus from previous focused network elements
      if(network.networkElementList) {
        Object.keys(network.networkElementList).map(elKey => {
          network.networkElementList[elKey].layerMeta.isSelected = false;
        });
      }

      // clears the handle of the setInterval function
      // this value is used to determine if a new setInterval call should be made
      network.networkMeta.chartsRequest.timerID = null;

      ctx.dispatch('mod_workspace/ADD_existingNetworkToWorkspace', { network }, {root: true});

    }
  },
  async deleteAllIds(ctx) {
    await idb.deleteAllIds();
  },
  async cleanup(ctx) {
    await idb.deleteAllIds();
    await idb.deleteAllModels();
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
