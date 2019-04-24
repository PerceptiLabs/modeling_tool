'use strict';

import Vue from 'vue'
//- Global plugins
import axios from 'axios'
import VeeValidate from 'vee-validate';
import VueShortKey from 'vue-shortkey';

import App from './App'
import router from './router'
import store from './store'

import configApp from '@/core/globalSettings.js'

//- Global components
import BaseCheckbox     from '@/components/base/checkbox.vue'
import BaseRadiobutton  from '@/components/base/radiobutton.vue'
import BaseSelect       from '@/components/base/select.vue'
import BaseRange        from '@/components/base/range.vue'

//- Global directives
import {mask} from 'vue-the-mask'

if (!process.env.IS_WEB) Vue.use(require('vue-electron'));

Vue.http = Vue.prototype.$http = axios;

Vue.config.productionTip = configApp.developMode;
Vue.config.performance = configApp.developMode;

//- Use plugin
Vue.use(VeeValidate);
Vue.use(VueShortKey);

//- Use directives
import './core/directives'
Vue.directive('mask', mask);

//- Use component
import '@/core/plugins/eCharts.js'
Vue.component('base-checkbox', BaseCheckbox);
Vue.component('base-radio', BaseRadiobutton);
Vue.component('base-select', BaseSelect);
Vue.component('base-range', BaseRange);


/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app');
