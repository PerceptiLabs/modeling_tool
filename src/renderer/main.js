import Vue from 'vue'
import axios from 'axios'
import Vuebar from 'vuebar'
import ECharts from 'vue-echarts/components/ECharts'

import App from './App'
import router from './router'
import store from './store'

import configApp from '@/core/globalSettings.js'

import BaseCheckbox     from '@/components/base/checkbox.vue'
import BaseRadiobutton  from '@/components/base/radiobutton.vue'
import BaseSelect       from '@/components/base/select.vue'
import BaseRange        from '@/components/base/range.vue'

Vue.use(Vuebar);

if (!process.env.IS_WEB) Vue.use(require('vue-electron'));

Vue.http = Vue.prototype.$http = axios;

Vue.config.productionTip = configApp.developMode;
Vue.config.performance = configApp.developMode;

//import './core/directives'
//import './core/filters'

Vue.component('base-checkbox', BaseCheckbox);
Vue.component('base-radio', BaseRadiobutton);
Vue.component('base-select', BaseSelect);
Vue.component('base-range', BaseRange);
Vue.component('v-chart', ECharts);



/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app');

//TODO delete vuebar - заменить
