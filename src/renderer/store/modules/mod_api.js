import configApp from '@/core/globalSettings.js'

import { namespacedCloud, stateCloud, mutationsCloud, actionsCloud } from '@/store/api/mod_cloudAPI.js'
import { namespacedLocal, stateLocal, mutationsLocal, actionsLocal } from '@/store/api/mod_localAPI.js'

const cloudExport = {
  namespaced: namespacedCloud,
  state: stateCloud,
  mutations: mutationsCloud,
  actions: actionsCloud
};
const localExport = {
  namespaced: namespacedLocal,
  state: stateLocal,
  mutations: mutationsLocal,
  actions: actionsLocal
};

export default configApp.version === 'core_cloud' ?  cloudExport : localExport;
