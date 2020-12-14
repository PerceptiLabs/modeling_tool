import Vue from 'vue';
import cloneDeep from 'lodash.clonedeep';
import { hashObject, generateID } from "@/core/helpers";
import { rygg } from '@/core/apiRygg.js';

const namespaced = true;

const state = {
  workspaceNotifications: [],
  toasts: [],
  pipy_version_available: false,
  toastTimers: {}
};

const getters = {
  getPiPyShowNotification: (state) => {
    return state.pipy_version_available;
  },
  getNotificationWindowState: (state) => (networkId) => {
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    
    if (!network) { return false; }

    return network.isNotificationWindowOpen;
  },
  getNotificationWindowSelectedTab: (state) => (networkId) => {
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    
    if (!network) { return false; }

    return network.selectedTab;
  },
  getToasts: (state) => (networkId) => {
    let numErrors = 0;
    let numWarnings = 0;

    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);

    if (network && network.errors) {
      numErrors = network.errors.length;
    }
    if (network && network.warnings) {
      numWarnings = network.warnings.length;
    }

    let errors = 
      state.toasts.filter(t => 
        t.networkId === networkId && 
        t.type === 'error');

    let warnings = 
      state.toasts.filter(t => 
        t.networkId === networkId && 
        t.type === 'warning');


    const result = []

    if (errors && errors.length) {
      result.push({ 
        networkId,
        type: 'error',
        count: numErrors,
        message: `There are ${ numErrors } unhandled ${ numErrors ? 'errors': 'error'}`
      });
    }

    if (warnings && warnings.length) {
      result.push({ 
        networkId,
        type: 'warning', 
        count: numWarnings,
        message: `There are ${ numWarnings } unhandled ${ numWarnings ? 'warnings': 'warning'}`
      });
    }

    return result;
  },
  getHasErrors: (state) => (networkId) => {
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    
    if (!network) { return []; }

    return network.errors && network.errors.length > 0;
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
      selectedTab: '', // ErrorInfoPanel | ConsoleInfoPanel
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
  removeToastObjectsForNetwork(state, { networkId }) {    
    if (!networkId) { return; }

    Vue.set(state, 'toasts', state.toasts.filter(t => t.networkId !== networkId));
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
  setWindowState(state, { networkId, value, selectedTab }) {
    if (!networkId) { return; }
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    network.isNotificationWindowOpen = !!value;
    network.selectedTab = selectedTab;
  },
  setSelectedId(state, { networkId, selectedId }) {
    
    const notificationObj = state.workspaceNotifications.find(wn => wn.networkId === networkId);

    notificationObj.selectedId = selectedId;
  },
  setShowPiPyNotification(state, { value }) {
    state.pipy_version_available = value;
  },
  clearToastTimer(state, { networkId }) {
    if (!state.toastTimers[networkId]) { return; }

    clearTimeout(state.toastTimers[networkId]);
  },
  setToastTimer(state, { networkId, toastTimer }) {
    Vue.set(state.toastTimers, networkId, toastTimer);
  },
  setSelectedTabMutation(state, { tabName, networkId }) {
    if (!networkId) { return; }
    const network = state.workspaceNotifications.find(wn => wn.networkId === networkId);
    network.selectedTab = tabName;
  }
};

const actions = {
  addError({ commit, dispatch}, { networkId, errorObject = null, addToast = false }) {

    if (errorObject == null) {
      errorObject = {
        Message: 'test test test',
        RandomString: generateID()
      };
    }

    const id = hashObject(errorObject);

    commit('assureWorkspace', { networkId });
    commit('addErrorNotification', { id, networkId, errorObject: cloneDeep(errorObject) });

    if (addToast) { 
      dispatch('addToast', { id, networkId, toastType: 'error', message: errorObject.Message });
    }
  },
  addWarning({ commit, dispatch }, { networkId, warningObject = null, addToast = false }) {

    if (warningObject == null) {
      warningObject = {
        Message: 'test test test',
        RandomString: generateID()
      };
    }

    const id = hashObject(warningObject);

    commit('assureWorkspace', { networkId });
    commit('addWarningNotification', { id, networkId, warningObject: cloneDeep(warningObject) });
    
    if (addToast) { 
      dispatch('addToast', { id, networkId, toastType: 'warning', message: warningObject.Message });
    }
  },
  addToast({ commit, dispatch }, { id = null, networkId, toastType, message }) {
    
    if (!id) {
      id = generateID();
    }
    commit('addToastObject', { id, networkId, toastType, message });

    dispatch('upsertToastTimeout', { networkId });
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

    dispatch('addToast', { networkId, toastType: 'error' });
    
    commit('removeErrorsExcept', { networkId, errorObjects });    
  },
  setNotificationWindowState({ commit }, { networkId, value, selectedTab = 'ErrorInfoPanel', selectedId = '' }) {
    commit('assureWorkspace', { networkId });
    commit('setWindowState', { networkId, value, selectedTab });
    commit('setSelectedId', { networkId, selectedId });
  },
  getPyPiUpdate({ commit }) {
    return rygg.get(`/app/updates_available/`)
      .then((res) => {
        if (res.data.newer_versions.length > 0) {
          commit('setShowPiPyNotification', {value: true});
        }

        return res;
      })
      .catch((error)=> {
        console.error(error); 
      })      
  },
  upsertToastTimeout({ commit }, { networkId, toastLifespanMs = 10000 }) {
    
    commit('clearToastTimer', { networkId });

    const toastTimer = setTimeout(function() {
      commit('clearToastTimer', { networkId });
      commit('removeToastObjectsForNetwork', { networkId });
    }, toastLifespanMs);

    commit('setToastTimer', { networkId, toastTimer });
  },
  setSelectedTabAction({ commit }, { tabName, networkId }) {
    commit('setSelectedTabMutation', { tabName, networkId });
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
