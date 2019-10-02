const namespaced = true;

const state = {
  history: {},
  maxSteps: 20,
  isEnableHistory: false,

};

const getters = {
  GET_isEnableHistory(state, rootGetters) {
    return state.isEnableHistory && rootGetters['mod_workspace/GET_networkIsOpen']
  },
  GET_currentNetHistory(state, rootGetters) {
    const currentNetId = rootGetters['mod_workspace/GET_currentNetwork'].networkID;
    return !!currentNetId
      ? state.history[currentNetId]
      : null
  },
};

const mutations = {
  push_newSnapshot(state, {id, value}) {
    let currentNet = state.history[id];
    if(currentNet.historyNet.length >= state.maxSteps) currentNet.historyNet.pop();
    currentNet.historyNet.unshift(value);
  },
  update_history(state, value) {
    state.history = value;
  },
  set_isEnableHistory(state, value) {
    state.isEnableHistory = value;
  }
};

const actions = {
  PUSH_newSnapshot({rootGetters, commit, dispatch, state}, newData) {
    const currentNet = rootGetters['mod_workspace/GET_currentNetwork'];
    const currentId = currentNet.networkID;
    let historyNet = state.history[currentId];
    const newSnapshot = {
      networkName: currentNet.networkName,
      networkElementList: currentNet.networkElementList,
      ...newData
    };

    if(!historyNet) { dispatch('UPDATE_networkList') }
    commit('push_newSnapshot', {id: currentId, value: newSnapshot});
  },
  UPDATE_networkList({rootGetters, rootState, commit, state}) {
    const wsList = rootState.mod_workspace.workspaceContent;
    const storeHistory = state.history;

    if(wsList.length === Object.keys(storeHistory).length) return;

    let newHistory = {};
    wsList.forEach((net)=> {
      newHistory[net.networkID] = storeHistory[net.networkID] || createNewHistory(net)
    });
    commit('update_history', newHistory);

    function createNewHistory(net) {
     return {
        historyStep: 0,
        historyNet: [{
          networkName: net.networkName,
          networkElementList: net.networkElementList
        }],
      }
    }
  },
  SET_isEnableHistory({commit}, val) {
    commit('set_isEnableHistory', val)
  },
  TO_prevStepHistory({commit}) {

  },
  TO_nextStepHistory({commit}) {
    commit('set_isEnableHistory')
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
