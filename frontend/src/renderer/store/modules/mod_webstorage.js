import idb from '@/core/helpers/idb-helper.js';
import cloneDeep from 'lodash.clonedeep';
import { doesFileExist as fileserver_doesFileExist } from '@/core/apiFileserver';

const namespaced = true;

const state = {};

const getters = {};

const mutations = {};

const actions = {
  async saveNetwork(ctx, network) {
    if (!network || !network.networkID) { return; }
    
    await idb.saveModel(cloneDeep(network));
  },
  async deleteNetwork(ctx, networkId) {
    if (!networkId) { return; }
    
    await idb.deleteModel(networkId.toString());
  },
  async deleteId(ctx, id) {
    await idb.deleteId(id);
  },
  async deleteIds(ctx, ids) {

    for (const id of ids) {
      await idb.deleteId(id);
    }
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
      await idb.saveModel(cloneDeep(ws));
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

    return new Promise(async (resolve) => {
      for(const network of networks) {
        const doesFileExist = await fileserver_doesFileExist(network.apiMeta.location + '/model.json');
        if(!doesFileExist) {
           ctx.dispatch('deleteId', network.apiMeta.model_id);
           ctx.dispatch('deleteNetwork', network.apiMeta.model_id);
           return 0;
        }
        // remove focus from previous focused network elements
        if(network.networkElementList) {
          Object.keys(network.networkElementList).map(elKey => {
            network.networkElementList[elKey].layerMeta.isSelected = false;
          });
        }
        // it's for reseting loading spinner of component chart
        if(network.networkElementList) {
          Object.keys(network.networkElementList).forEach(networkElementId => {
            network.networkElementList[networkElementId].chartDataIsLoading = 0;
          })
        }

        network.chartDataIsLoading = 0;
        if(network.networkMeta) {
          network.networkMeta.openStatistics = null;
          network.networkMeta.openTest = null;

          if (network.networkMeta.chartsRequest) {
            // clears the handle of the setInterval function
            // this value is used to determine if a new setInterval call should be made
            network.networkMeta.chartsRequest.timerID = null;
            network.networkMeta.chartsRequest.waitGlobalEvent = false;
          }
        }

        ctx.dispatch('mod_workspace/ADD_existingNetworkToWorkspace', { network }, {root: true});

      }
      resolve();
    });
  },
  async deleteAllIds(ctx) {
    await idb.deleteAllIds();
  },
  async cleanup(ctx) {
    await idb.deleteAllIds();
    await idb.deleteAllModels();
  },
  async saveTestStatistic(ctx, payload) {
    return await idb.saveTestStatistic(payload);
  },
  async getTestStatistic(ctx) {
    return await idb.getTestStatistic();
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
