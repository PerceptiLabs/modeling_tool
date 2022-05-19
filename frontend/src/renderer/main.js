"use strict";

import Vue from "vue";
//- Global plugins
import * as Sentry from "@sentry/browser";
import * as Integrations from "@sentry/integrations";
import VeeValidate from "vee-validate";
import VueHotkey from "v-hotkey";
import LogRocket from "logrocket";

import App from "./App";
import NoInternetConnection from "@/pages/NoInternetConnection.vue";
import router from "./router";
import store from "./store";
import { isDevelopMode } from "@/core/constants.js";
import AuthService from "@/core/auth";

//- Global components
import BaseCheckbox from "@/components/base/checkbox.vue";
import BaseRadiobutton from "@/components/base/radiobutton.vue";
import BaseSelect from "@/components/base/select.vue";
import BaseSwitch from "@/components/base/switch.vue";
import BaseRange from "@/components/base/range.vue";
import BaseToggleButton from "@/components/base/toggle.vue";
import BaseToggleExpandButton from "@/components/base/toggle-expand.vue";
import BaseButton from "@/components/base/base-button.vue";
import PerfectScrollBar from "vue2-perfect-scrollbar";

import "vue2-perfect-scrollbar/dist/vue2-perfect-scrollbar.css";

//- Global directives
import Analytics from "@/core/analytics";

//Vue.http = Vue.prototype.$http = axios;
Vue.config.devtools = isDevelopMode;
Vue.config.productionTip = isDevelopMode;
Vue.config.performance = isDevelopMode;
if (isDevelopMode) {
  Vue.config.errorHandler = function(err, vm, info) {
    console.error(err, info);
  };
}

if (process.env.ENABLE_LOGROCKET) {
  LogRocket.init(process.env.LOGROCKET_APP_ID);
}

//- Use plugin
if (process.env.SENTRY_ENABLED === "true") {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.SENTRY_ENV,
    integrations: [
      new Integrations.Vue({
        Vue,
        attachProps: true,
        attachStacktrace: true,
      }),
    ],
    release: process.env.PACKAGE_VERSION,
  });
}
Vue.use(VeeValidate);
Vue.use(VueHotkey);
Vue.use(PerfectScrollBar);
//- Use directives
import "./core/directives";

//- Use filters
import "./core/filters";

//- Use component
import "@/core/plugins/eCharts.js";
import "@/core/plugins/intercom.js";
import userflow from "userflow.js";

Vue.component("base-checkbox", BaseCheckbox);
Vue.component("base-radio", BaseRadiobutton);
Vue.component("base-select", BaseSelect);
Vue.component("base-switch", BaseSwitch);
Vue.component("base-range", BaseRange);
Vue.component("base-toggle", BaseToggleButton);
Vue.component("base-toggle-expand", BaseToggleExpandButton);
Vue.component("base-button", BaseButton);

// analytics
Analytics.googleAnalytics.setup();
Analytics.googleAnalytics.trackUserId(store.getters["mod_user/GET_userID"]);

async function runApp(appState) {
  const user = await AuthService.getProfile();

  Sentry.setUser({
    email: user.email,
  });

  if (process.env.ENABLE_LOGROCKET) {
    LogRocket.identify(user.sub, {
      name: user.name,
      email: user.email,
    });
    LogRocket.getSessionURL(sessionURL => {
      Sentry.setExtra("logrocket-url", sessionURL);
    });
  }

  userflow.init(process.env.USERFLOW_KEY);
  userflow.identify(user.sub, {
    name: user.name,
    email: user.email,
  });

  new Vue({
    components: { App },
    router,
    store,
    template: "<App/>",
  }).$mount("#app");

  router.push(
    appState && appState.targetUrl
      ? appState.targetUrl
      : window.location.pathname,
  );
  store.dispatch("mod_user/SET_userProfile", user, { root: true });
}

function renderNoInternetConnectionPage() {
  new Vue({
    components: { NoInternetConnection },
    router,
    store,
    template: "<NoInternetConnection/>",
  }).$mount("#app");
}

(async function main() {
  await AuthService.init();

  if (await AuthService.isReachable()) {
    const appState = await AuthService.login();
    await runApp(appState);
  } else {
    renderNoInternetConnectionPage();
  }
})();
