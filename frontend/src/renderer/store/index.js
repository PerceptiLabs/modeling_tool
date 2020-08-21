import Vue from 'vue'
import Vuex from 'vuex'

import modules from './modules'
import wsHistory from './plugins/workspace-history'
import wsForwardBackwardConnections from './plugins/workspace-forward-backward-connection'

Vue.use(Vuex);

export default new Vuex.Store({
  strict: false,
  modules,
  plugins: [wsHistory, wsForwardBackwardConnections]
})
