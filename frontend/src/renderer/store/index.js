import Vue from 'vue'
import Vuex from 'vuex'

import modules from './modules'
import wsHistory from './plugins/workspace-history'

Vue.use(Vuex);

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production',
  modules,
  plugins: [wsHistory]
})
