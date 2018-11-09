import Vue from 'vue'
import Vuex from 'vuex'

import modules from './modules'

Vue.use(Vuex);

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production',
  modules,
  actions: {
    NET_trainingStart(context) {
      console.log(context);
      // commit('SET_appMode', 'training');
      // commit('HIDE_allGlobalPopups');
      // rootGetters['mod_workspace/currentNetwork'].networkStatistics = true;
    },
  }
})
