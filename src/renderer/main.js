import Vue from 'vue'
import axios from 'axios'
import Vuebar from 'vuebar'
import Tooltip from 'vue-directive-tooltip';

import App from './App'
import router from './router'
import store from './store'

import configApp from '@/core/globalSettings.js'
import BaseCheckbox from '@/components/base/checkbox.vue'

Vue.use(Vuebar);
Vue.use(Tooltip, {
  placement: 'right',
});

if (!process.env.IS_WEB) Vue.use(require('vue-electron'));

Vue.http = Vue.prototype.$http = axios;

Vue.config.productionTip = configApp.developMode;
Vue.config.performance = configApp.developMode;

Vue.component('base-checkbox', BaseCheckbox);

//console.log(configApp);

/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app');

//TODO delete vue-directive-tooltip,
