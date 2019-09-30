const namespaced = true;

const state = {
  history: null
};

const mutations = {
  push_newSnapshot(state, {id, value}) {
    state.history[id].push(value);
  },
  update_history(state, value) {
    state.history = value;
  }
};

const actions = {
  PUSH_newSnapshot({rootGetters, rootState, commit}) {
    const currentNet = rootGetters['mod_workspace/GET_currentNetwork'];
    const currentId = currentNet.networkID;
    commit('push_newSnapshot', {id: currentId, value: currentNet})
  },
  UPDATE_networkList({rootGetters, rootState, commit}) {
    const wsList = rootState.mod_workspace.workspaceContent;
    const currentId = rootGetters['mod_workspace/GET_currentNetwork'].networkID;
    let newHistory = {};
    wsList.forEach((net)=> {
      newHistory[net.networkID] = []
    });
    commit('update_history', newHistory)
    //const currentId = rootGetters['mod_workspace/GET_currentNetworkElementList'];
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
