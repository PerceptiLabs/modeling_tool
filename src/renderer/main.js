import Vue from 'vue'
import axios from 'axios'

import BaseCheckbox from '@/components/base/checkbox.vue'

import App from './App'
import router from './router'
import store from './store'

if (!process.env.IS_WEB) Vue.use(require('vue-electron'))
Vue.http = Vue.prototype.$http = axios
Vue.config.productionTip = true

Vue.component('base-checkbox', BaseCheckbox)

/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app')
