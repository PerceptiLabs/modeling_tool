import cloneDeep from 'lodash.clonedeep';
import { hashObject, generateID } from "@/core/helpers";

const namespaced = true;

const state = {
  workspaceNotifications: [],
  toasts: []
};

const getters = {
  getNotificationWindowState: (state) => (networkId) => {
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    
    if (!network) { return false; }

    return network.isNotificationWindowOpen;
  },
  getToasts: (state) => (networkId) => {
    return state.toasts.filter(t => t.networkId === networkId);
  },
  getErrors: (state) => (networkId) => {
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    
    if (!network) { return []; }

    return network.errors;
  },
  getWarnings: (state) => (networkId) => {
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    
    if (!network) { return []; }

    return network.warnings;
  },
  getSelectedId: (state) => (networkId) => {
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    
    if (!network) { return []; }

    return network.selectedId;
  },
};

const mutations = {
  assureWorkspace(state, { networkId }) {
    if (!networkId) { return; }

    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    if (network) { return; }

    const defaultEntry = {
      networkId: networkId,
      isNotificationWindowOpen: false,
      selectedId: '', // which row is selected
      errors: [],
      warnings: []
    };
    state.workspaceNotifications.push(cloneDeep(defaultEntry));
  },
  addErrorNotification(state, { id, networkId, errorObject }) {

    if (!networkId) { return; }
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);

    if (!network.errors.some(e => e.id === id)) {
      network.errors.push({
        id: id,
        ...errorObject
      });
    }
  },
  addWarningNotification(state, { id, networkId, warningObject }) {
    if (!networkId) { return; }
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);

    if (!network.warnings.some(e => e.id === id)) {
      network.warnings.push({
        id: id,
        ...warningObject
      });
    }
  },
  addToastObject(state, { id, networkId, toastType, message }) {
    if (state.toasts.some(t => t.id === id)) { return; }

    state.toasts.push({
      id: id,
      networkId: networkId,
      type: toastType,
      message: message
    });
  },
  removeToastObject(state, { id }) {    
    const toastIdx = state.toasts.findIndex(t => t.id === id);

    if (~toastIdx) { 
      state.toasts.splice(toastIdx, 1); 
    }    
  },
  removeErrorsExcept(state, { networkId, errorObjects }) {
    if (!networkId || !errorObjects) { return; }
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);

    const errorHashes = [];
    for (const eo of errorObjects) {
      errorHashes.push(hashObject(eo))
    }

    network.errors = network.errors
      .filter(n => errorHashes.includes(n.id));
  },
  setWindowState(state, { networkId, value }) {
    if (!networkId) { return; }
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);

    network.isNotificationWindowOpen = !!value;
  },
  setSelectedId(state, { networkId, selectedId }) {
    
    const notificationObj = state.workspaceNotifications.find(wn => wn.networkId === networkId);

    notificationObj.selectedId = selectedId;
  }
};

const actions = {
  addError({ commit, dispatch}, { networkId, errorObject = null }) {

    if (errorObject == null) {
      errorObject = {
        Message: 'test test test',
        RandomString: generateID()
      };
    }

    const id = hashObject(errorObject);

    commit('assureWorkspace', { networkId });
    commit('addErrorNotification', { id, networkId, errorObject: cloneDeep(errorObject) });

    dispatch('addToast', { id, networkId, toastType: 'error', message: errorObject.Message });
  },
  addWarning({ commit, dispatch }, { networkId, warningObject = null }) {

    if (warningObject == null) {
      warningObject = {
        Message: 'test test test',
        RandomString: generateID()
      };
    }

    const id = hashObject(warningObject);

    commit('assureWorkspace', { networkId });
    commit('addWarningNotification', { id, networkId, warningObject: cloneDeep(warningObject) });
    
    dispatch('addToast', { id, networkId, toastType: 'warning', message: warningObject.Message });
  },
  addToast({ commit }, { id = null, networkId, toastType, message, toastLifespanMs = 10000}) {
    
    if (!id) {
      id = generateID();
    }
    commit('addToastObject', { id, networkId, toastType, message });

    (function(id) {
      setTimeout(function() {
        commit('removeToastObject', { id });
      }, toastLifespanMs);
    })(id);
  },
  setNotifications({ commit, dispatch }, { networkId, kernelResponses }) {
    commit('assureWorkspace', { networkId });
    const errorObjects = Object.entries(kernelResponses)
      .filter(([k,v]) => v.Error !== null)
      .map(([k,v]) => ({
        layerId: k,
        ...v.Error
      }));

    for (const eo of errorObjects) {
      dispatch('addError', {
        networkId,
        errorObject: eo
      });
    }

    commit('removeErrorsExcept', { networkId, errorObjects });    
  },
  setNotificationWindowState({ commit }, { networkId, value, selectedId = '' }) {

    commit('assureWorkspace', { networkId });
    commit('setWindowState', { networkId, value });
    commit('setSelectedId', { networkId, selectedId });
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
