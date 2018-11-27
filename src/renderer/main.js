import Vue from 'vue'
//- Global plugins
import axios from 'axios'
import Vuebar from 'vuebar'
import Tooltip from 'vue-directive-tooltip';

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
import VeeValidate from 'vee-validate';

Vue.use(Vuebar);
Vue.use(Tooltip, {
  delay: 0,
  placement: 'right',
});
Vue.use(VeeValidate);


if (!process.env.IS_WEB) Vue.use(require('vue-electron'));

Vue.http = Vue.prototype.$http = axios;

Vue.config.productionTip = configApp.developMode;
Vue.config.performance = configApp.developMode;

//import './core/directives'
Vue.directive('mask', mask);

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

//TODO delete vuebar - заменить v-tooltip - delete
