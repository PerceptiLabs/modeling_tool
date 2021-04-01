import {deepCloneNetwork, isEnvDataWizardEnabled} from "@/core/helpers";
import { lockedComponentsNames } from "@/core/constants";

const namespaced = true;

const state = {
  buffer: null,
  clipBoardNetworkList: {}
};

const mutations = {
  set_buffer(state, value) {
    state.buffer = value
  },
  set_clipBoardNetworkList(state, value) {
    state.clipBoardNetworkList = deepCloneNetwork(value);
  }
};

const actions = {
  SET_buffer({commit}, payload) {
    commit('set_buffer', filterLockedComponents(payload))
  },
  CLEAR_buffer({commit}) {
    commit('set_buffer', null)
  },
  SET_clipBoardNetworkList({commit}, value) {
    commit('set_clipBoardNetworkList', value)
  },
  CLEAR_clipBoardNetworkList({commit}, value) {
    commit('set_clipBoardNetworkList', {})
  }
};

function filterLockedComponents(payload) {
  if(isEnvDataWizardEnabled()) {
    payload = payload.filter(el => !lockedComponentsNames.includes(el.target.dataset.component))  
  }
  return payload
}
export default {
  namespaced,
  state,
  mutations,
  actions
}
