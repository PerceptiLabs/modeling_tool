"use strict";

import Vue from "vue";
//- Global plugins
import * as Sentry from "@sentry/browser";
import * as Integrations from "@sentry/integrations";
import VeeValidate from "vee-validate";
import VueHotkey from "v-hotkey";
import Keycloak from "keycloak-js";
import LogRocket from "logrocket";

import App from "./App";
import NoInternetConnection from "@/pages/NoInternetConnection.vue";
import router from "./router";
import store from "./store";
import { setCookie, getCookie } from "@/core/helpers";
import { isDevelopMode } from "@/core/constants.js";
import { LOCAL_STORAGE_CURRENT_USER } from "@/core/constants";

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
import { parseJWT } from "@/core/helpers";
import Analytics from "@/core/analytics";
import { keyCloak } from "@/core/apiKeyCloak.js";

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
import { renderingKernel } from "@/core/apiRenderingKernel";
import { isNoKeyCloakEnabled } from "@/core/helpers";

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

function runApp(token, refreshToken) {
  new Vue({
    components: { App },
    router,
    store,
    template: "<App/>",
  }).$mount("#app");

  setCookie("loggedInUser", token, 365 * 10);

  let userProfile = parseJWT(token);
  userProfile.firstName = userProfile.given_name;
  userProfile.lastName = userProfile.family_name;

  Sentry.setUser({
    email: userProfile.email,
  });

  store.dispatch("mod_user/SET_userProfile", userProfile, { root: true });
  setTokens(store, token, refreshToken);

  if (process.env.ENABLE_LOGROCKET) {
    LogRocket.identify(userProfile.sub, {
      name: `${userProfile.firstName} ${userProfile.lastName}`,
      email: userProfile.email,
    });
    LogRocket.getSessionURL(sessionURL => {
      Sentry.setExtra("logrocket-url", sessionURL);
    });
  }

  userflow.init(process.env.USERFLOW_KEY);
  userflow.identify(userProfile.sub, {
    name: `${userProfile.firstName} ${userProfile.lastName}`,
    email: userProfile.email,
  });
}

function setTokens(store, token, refreshToken) {
  store.dispatch(
    "mod_user/SET_userToken",
    {
      accessToken: token,
      refreshToken: refreshToken,
    },
    { root: true },
  );

  localStorage.setItem(LOCAL_STORAGE_CURRENT_USER, token);
  localStorage.setItem("vue-token", token);
  localStorage.setItem("vue-refresh-token", refreshToken);
}

export let keycloak;
async function login() {
  let url = await keyCloak.url();
  let initOptions = {
    url: `${url}`,
    realm: `${process.env.KEYCLOAK_REALM}`,
    clientId: `${process.env.KEYCLOAK_CLIENT_ID}`,
    onLoad: "login-required",
    checkLoginIframe: false, // only true when onLoad is set to 'check-sso', causes errors when offline
  };
  keycloak = Keycloak(initOptions);
  keycloak
    .init({
      onLoad: initOptions.onLoad,
      checkLoginIframe: initOptions.checkLoginIframe,
    })
    .then(auth => {
      if (!auth) {
        window.location.reload();
      }

      runApp(keycloak.token, keycloak.refreshToken);

      // Set user email
      const { email } = parseJWT(keycloak.token);
      renderingKernel.set_user(email);

      setInterval(() => {
        keycloak
          .updateToken(1)
          .success(refreshed => {
            if (refreshed) {
              setTokens(store, keycloak.token, keycloak.refreshToken);
            }
          })
          .error(() => {
            console.error("Failed to refresh token");
          });
      }, 6000);
    })
    .catch(e => {
      console.error("Authenticated Failed");
      console.error(e);
    });
}

// Allow running w/o login for a hard-coded user when the frontend is built with NO_KC set to 'true'
function demo() {
  const user = {
    given_name: "Demo",
    family_name: "User",
    email: "modeler@perceptilabs.test",
    userId: 1,
  };

  const token = "placeholder." + window.btoa(JSON.stringify(user));
  const refreshToken = "placeholder_refreshToken";
  runApp(token, refreshToken);
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
  try {
    const loggedInUser = getCookie("loggedInUser");
    const isKeycloakReachable = await keyCloak.isReachable();

    if (isNoKeyCloakEnabled()) {
      demo();
    } else if (isKeycloakReachable) {
      login();
    } else if (loggedInUser && !isKeycloakReachable) {
      runApp(loggedInUser, "placeholder");
    } else {
      renderNoInternetConnectionPage();
    }
  } catch (err) {
    demo();
    console.error(err);
  }
})();
