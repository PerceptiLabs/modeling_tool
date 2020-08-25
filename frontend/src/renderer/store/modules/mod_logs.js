import Vue from 'vue';
import { hashString } from '@/core/helpers';

const namespaced = true;

const maxEntriesPerNetwork = 100;

const state = {
  kernelLogs: {}
};

const getters = {
    getKernelLogs: (state) => (networkId) => {
      return (networkId in state.kernelLogs) ? state.kernelLogs[networkId] : [];
    }
};

const mutations = {
  assureNetworkId(state, { networkId }) {
    if (!(networkId in state.kernelLogs)) {
      Vue.set(state.kernelLogs, networkId, []);
    }
  },
  addKernelLogs(state, { networkId, logs }) {

    for (const l of logs) {
      state.kernelLogs[networkId].push({
        id: `${networkId}_${(new Date()).getTime()}_${hashString(l)}`,
        message: l
      });
    }

    if (maxEntriesPerNetwork && state.kernelLogs[networkId].length > maxEntriesPerNetwork) {
      state.kernelLogs[networkId].splice(0, state.kernelLogs[networkId].length - maxEntriesPerNetwork);
    }
  },
};

const actions = {
    addLogsForNetwork({commit}, { networkId, logs }) {      
      if (!networkId) { return; }

      commit('assureNetworkId', { networkId });
      commit('addKernelLogs', { networkId, logs });
    },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
