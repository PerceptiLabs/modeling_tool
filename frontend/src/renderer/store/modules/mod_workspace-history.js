import { deepCloneNetwork }  from "@/core/helpers.js";

const namespaced = true;

const state = {
  history: {},
  maxSteps: 20,
  isEnableHistory: true,

};

const getters = {
  GET_isEnableHistory(state, getters, rootState, rootGetters) {
    return state.isEnableHistory && rootGetters['mod_workspace/GET_enableHotKeyElement']
  },
  GET_currentNetHistory(state, getters, rootState, rootGetters) {
    const currentNet = rootGetters['mod_workspace/GET_currentNetwork'];
    if(!!currentNet) return state.history[currentNet.networkID];
    else return null
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
  },
  to_prevStepHistory(state, {currentID, dispatch}) {
    let historyCurrNet = state.history[currentID];
    if(historyCurrNet.historyStep < historyCurrNet.historyNet.length - 1) {
      const numStep = ++state.history[currentID].historyStep;
      dispatch('mod_workspace/SET_historyStep', deepCloneNetwork(historyCurrNet.historyNet[numStep]), {root: true});
      dispatch('mod_events/EVENT_calcArray', null, {root: true});
    }
  },
  to_nextStepHistory(state, {currentID, dispatch}) {
    let historyCurrNet = state.history[currentID];
    if(historyCurrNet.historyStep) {
      const numStep = --state.history[currentID].historyStep;
      dispatch('mod_workspace/SET_historyStep', deepCloneNetwork(historyCurrNet.historyNet[numStep]), {root: true});
      dispatch('mod_events/EVENT_calcArray', null, {root: true});
    }
  },
  update_nextStepHistory(state, {id, value, commit}) {
    let historyCurrNet = state.history[id];
    historyCurrNet.historyNet.splice(0, historyCurrNet.historyStep);
    state.history[id].historyStep = 0;
    commit('push_newSnapshot', {id, value});
  },
};

const actions = {
  PUSH_newSnapshot({rootGetters, commit, dispatch, state}) {
    const currentNet = rootGetters['mod_workspace/GET_currentNetwork'];
    const currentId = rootGetters['mod_workspace/GET_currentNetworkId'];
    let historyNet = state.history[currentId];
    const newSnapshot = {
      networkName: currentNet.networkName,
      networkElementList: deepCloneNetwork(currentNet.networkElementList),
    };

    if(!historyNet) { dispatch('UPDATE_networkList') }
    if(historyNet.historyStep) {
      commit('update_nextStepHistory', {id: currentId, value: newSnapshot, commit});
    }
    else {
      commit('push_newSnapshot', {id: currentId, value: newSnapshot});
    }
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
          networkName: JSON.parse(JSON.stringify(net.networkName)),
          networkElementList: deepCloneNetwork(net.networkElementList),
        }],
      }
    }
  },
  SET_isEnableHistory({commit}, val) {
    commit('set_isEnableHistory', val)
  },
  TO_prevStepHistory({commit, getters, rootGetters, dispatch}) {
    if(getters.GET_isEnableHistory) {
      dispatch('SET_isEnableHistory', false);
      const currentID = rootGetters['mod_workspace/GET_currentNetworkId'];
      commit('to_prevStepHistory', {currentID, dispatch});
    }
  },
  TO_nextStepHistory({commit, getters, rootGetters, dispatch}) {
    if(getters.GET_isEnableHistory) {
      dispatch('SET_isEnableHistory', false);
      const currentID = rootGetters['mod_workspace/GET_currentNetworkId'];
      commit('to_nextStepHistory', {currentID, dispatch});
    }
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
