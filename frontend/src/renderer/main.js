'use strict';

import Vue from 'vue'
//- Global plugins
import * as Sentry from '@sentry/browser';
import * as Integrations from '@sentry/integrations';
import axios        from 'axios'
import VeeValidate  from 'vee-validate';
import VueHotkey    from 'v-hotkey'

import App    from './App'
import router from './router'
import store  from './store'

import { isDevelopMode } from '@/core/constants.js'

//- Global components
import BaseCheckbox     from '@/components/base/checkbox.vue'
import BaseRadiobutton  from '@/components/base/radiobutton.vue'
import BaseSelect       from '@/components/base/select.vue'
import BaseRange        from '@/components/base/range.vue'

//- Global directives
import {mask} from 'vue-the-mask' // page registration dont use now

//if (!process.env.IS_WEB) Vue.use(require('vue-electron'));

//Vue.http = Vue.prototype.$http = axios;

Vue.config.productionTip = isDevelopMode;
Vue.config.performance = isDevelopMode;

//- Use plugin
if (!Vue.config.devtools) {
  Sentry.init({
    dsn: 'https://2497f27009b24990b4c0f3feeda4d37d@sentry.io/1833551',
    integrations: [new Integrations.Vue({Vue, attachProps: true})],
  });
}
Vue.use(VeeValidate);
Vue.use(VueHotkey);

//- Use directives
import './core/directives'
Vue.directive('mask', mask);

//- Use filters
import './core/filters'

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
