import Vue from 'vue'
import Vuex from 'vuex'

import modules from './modules'
import wsHistory from './plugins/workspace-history'
import createLogger from "vuex/dist/logger";
Vue.use(Vuex);


const logger = createLogger({
  collapsed: true, // auto-expand logged mutations
  filter (mutation, stateBefore, stateAfter) {
    // returns `true` if a mutation should be logged
    // `mutation` is a `{ type, payload }`
    return mutation.type !== "aBlacklistedMutation"
  },
  transformer (state) {
    // transform the state before logging it.
    // for example return only a specific sub-tree
    let netList = state.mod_workspace.workspaceContent[state.mod_workspace.currentNetwork] &&  state.mod_workspace.workspaceContent[state.mod_workspace.currentNetwork].networkElementList;
    let data = {}; 
    if(netList) {
      Object.values(netList).map(el => {
        if(el.layerType === 'Container') {
          data[el.layerId] = el.containerLayersList;
        }
      })
    }
    
    return data;
    // return state.mod_workspace.workspaceContent[state.mod_workspace.currentNetwork] &&  state.mod_workspace.workspaceContent[state.mod_workspace.currentNetwork].networkElementList
  },
  mutationTransformer (mutation) {
    // mutations are logged in the format of `{ type, payload }`
    // we can format it any way we want.
    return mutation.type
  },
  logger: console, // implementation of the `console` API, default `console`
});

const devPlugins = [];
if(process.env.NODE_ENV !== 'production') {
  devPlugins.push(logger);
}

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production',
  modules,
  plugins: [wsHistory, ...devPlugins]
})
