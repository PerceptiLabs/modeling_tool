import Vue from 'vue'
import Vuex from 'vuex'

import modules from './modules'
import wsHistory from './plugins/workspace-history'
import { isDevelopMode } from '@/core/constants';

Vue.use(Vuex);

export default new Vuex.Store({
  strict: isDevelopMode,
  modules,
  plugins: [wsHistory],
});
