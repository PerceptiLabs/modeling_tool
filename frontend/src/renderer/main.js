'use strict';

import Vue from 'vue'
//- Global plugins
import * as Sentry from '@sentry/browser';
import * as Integrations from '@sentry/integrations';
import axios        from 'axios'
import VeeValidate  from 'vee-validate';
import VueHotkey    from 'v-hotkey'
import Keycloak from 'keycloak-js'

import App    from './App'
import router from './router'
import store  from './store'
import { isElectron, setAppTypeRootClasses } from "@/core/helpers";
import { isDevelopMode } from '@/core/constants.js'

//- Global components
import BaseCheckbox     from '@/components/base/checkbox.vue'
import BaseRadiobutton  from '@/components/base/radiobutton.vue'
import BaseSelect       from '@/components/base/select.vue'
import BaseRange        from '@/components/base/range.vue'
import PerfectScrollBar from 'vue2-perfect-scrollbar';

import 'vue2-perfect-scrollbar/dist/vue2-perfect-scrollbar.css'

//- Global directives
import {mask} from 'vue-the-mask' // page registration dont use now
import { parseJWT } from '@/core/helpers'
import Analytics from '@/core/analytics';
if(isElectron()) {
  Vue.use(require('vue-electron'));
} 

//Vue.http = Vue.prototype.$http = axios;
Vue.config.devtools = isDevelopMode;
Vue.config.productionTip = isDevelopMode;
Vue.config.performance = isDevelopMode;

// set the parent(html,body) platform class one of => [is-web, is-electron]
setAppTypeRootClasses();

//- Use plugin
if (!Vue.config.devtools) {
  Sentry.init({
    dsn: 'https://2497f27009b24990b4c0f3feeda4d37d@sentry.io/1833551',
    integrations: [new Integrations.Vue({Vue, attachProps: true})],
  });
}
Vue.use(VeeValidate);
Vue.use(VueHotkey);
Vue.use(PerfectScrollBar);
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

      
// analytics
Analytics.googleAnalytics.setup();
Analytics.googleAnalytics.trackUserId(store.getters['mod_user/GET_userID']);


function runApp(token, refreshToken){
  new Vue({
    components: { App },
    router,
    store,
    template: '<App/>'
  }).$mount('#app');


  let userProfile = parseJWT(token)
  userProfile.firstName = userProfile.given_name
  userProfile.lastName = userProfile.family_name

  store.dispatch('mod_user/SET_userProfile', userProfile, {root: true});
  store.dispatch('mod_user/SET_userToken', {
    accessToken: token,
    refreshToken: refreshToken,
  }, {root: true});

  localStorage.setItem('currentUser', token);
  localStorage.setItem("vue-token", token);
  localStorage.setItem("vue-refresh-token", refreshToken);
}

export let keycloak;
function login(){
  let initOptions = {
    url: `${process.env.KEYCLOACK_BASE_URL}/auth`, realm: `${process.env.KEYCLOACK_RELM}`, clientId: `${process.env.KEYCLOACK_CLIENT_ID}`, onLoad:'login-required'
  }
  keycloak = Keycloak(initOptions);

  keycloak.init({ onLoad: initOptions.onLoad }).then((auth) =>{

    if(!auth) {
      window.location.reload();
    }

    runApp(keycloak.token, keycloak.refreshToken);

    setInterval(() =>{
      keycloak.updateToken(1).success((refreshed)=>{
        if (refreshed) {
          console.log('Token refreshed'+ refreshed);
        }
      }).error(()=>{
        console.error('Failed to refresh token');
      });


    }, 6000)

  }).catch((e) =>{
    console.error("Authenticated Failed");
    console.error(e);
  });
}


// Allow running w/o login for a hard-coded user
// TODO: this will be removed after creating a local docker-based keycloak login realm
function demo(){
  const user = {
    given_name: "John",
    family_name: "Doe",
    email: "a@a.test",
    userId: 1,
  }

  const token = "placeholder." + window.btoa(JSON.stringify(user));
  const refreshToken = "placeholder_refreshToken";
  runApp(token, refreshToken);
}


if (process.env.NO_KC == 'true'){
  demo();
} else {
  login();
}
