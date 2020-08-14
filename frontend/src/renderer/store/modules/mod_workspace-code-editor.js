import cloneDeep from 'lodash.clonedeep';
import { generateID } from "@/core/helpers";

const namespaced = true;

const state = {
  isInFocus: false,
  workspaceCodeEditors: []
};

const getters = {
  getCodeWindowState: (state) => (networkId) => {
    const network = state.workspaceCodeEditors.find(wn => wn.networkId === networkId);
    
    if (!network) { return false; }

    return network.isCodeWindowOpen;
  },
  getElement: (state) => (networkId) => {
    const network = state.workspaceCodeEditors.find(wn => wn.networkId === networkId);
    
    if (!network) { return []; }

    return network.element;
  },
  getHasUnsavedChanges: (state) => (networkId) => {
    const network = state.workspaceCodeEditors.find(wn => wn.networkId === networkId);
    
    if (!network) { return false; }

    return network.hasUnsavedChanges;
  },
};

const mutations = {
  assureWorkspace(state, { networkId }) {
    if (!networkId) { return; }

    const network = state.workspaceCodeEditors.find(wn => wn.networkId === networkId);
    if (network) { return; }

    const defaultEntry = {
      networkId: networkId,
      isCodeWindowOpen: false,
      element: null,
      hasUnsavedChanges: false
    };
    state.workspaceCodeEditors.push(cloneDeep(defaultEntry));
  },
  setIsInFocusState(state, value) {
    state.isInFocus = value;
  },
  setElement(state, { networkId, element }) {

    if (!networkId) { return; }
    const network = state.workspaceCodeEditors.find(wn => wn.networkId === networkId);

    network.element = element;
  },
  setWindowState(state, { networkId, value }) {
    if (!networkId) { return; }
    const network = state.workspaceCodeEditors.find(wn => wn.networkId === networkId);

    network.isCodeWindowOpen = !!value;
  },
  setHasUnsavedChanges(state, { networkId, hasUnsavedChanges }) {

    if (!networkId) { return; }
    const network = state.workspaceCodeEditors.find(wn => wn.networkId === networkId);

    network.hasUnsavedChanges = hasUnsavedChanges;
  },
};

const actions = {
  openEditor({ commit }, { networkId, element }) {
    commit('assureWorkspace', { networkId });
    commit('setElement', { networkId, element });
    commit('setHasUnsavedChanges', { networkId, hasUnsavedChanges: false });
    commit('setWindowState', { networkId, value: true });
  },
  closeEditor({ commit }, { networkId }) {
    commit('assureWorkspace', { networkId });
    commit('setHasUnsavedChanges', { networkId, hasUnsavedChanges: false });
    commit('setWindowState', { networkId, value: false });
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
