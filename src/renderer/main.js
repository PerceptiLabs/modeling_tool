const configApp = {
  version: 'core_cloud', //'python'
  developMode: true
}

import Vue from 'vue'
import axios from 'axios'
import Vuebar from 'vuebar'
import Tooltip from 'vue-directive-tooltip';

import BaseCheckbox from '@/components/base/checkbox.vue'

import App from './App'
import router from './router'
import store from './store'

Vue.use(Vuebar)
Vue.use(Tooltip, {
  placement: 'right',
})

if (!process.env.IS_WEB) Vue.use(require('vue-electron'))
if(process.env.RUN_TARGET === 'core_local') {
  configApp.version = 'core_local'
}

Vue.http = Vue.prototype.$http = axios

Vue.config.productionTip = configApp.developMode;
Vue.config.performance = configApp.developMode;
Vue.config.versionApp = configApp.version;
//performance

Vue.component('base-checkbox', BaseCheckbox)

/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app')

//TODO delete vue-drag-resize, vue-directive-tooltip, python-shell
