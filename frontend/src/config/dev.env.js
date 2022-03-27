"use strict";
const merge = require("webpack-merge");
const prodEnv = require("./prod.env");

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  HUBSPOT_ID: '"7122301.js"',
  GOOGLE_ANALYTICS_ID: '"UA-114940346-2"',
  FORCE_DEFAULT_PROJECT: '"true"',
  KEYCLOAK_BASE_URL: '"https://keycloak.dev.perceptilabs.com:8443/auth"',
  KEYCLOAK_REALM: '"vue-perceptilabs"',
  KEYCLOAK_CLIENT_ID: '"vue-perceptilabs-client-id"',
  GITHUB_CLIENT_ID: '"094271b0edb47c75dc24"',
  SENTRY_DSN:
    '"https://a926ebcbc2a0463ab728fe06ebd750a8@o283802.ingest.sentry.io/6061754"',
  SENTRY_ENABLED: '"false"',
  SENTRY_ENV: '"dev"',
  PL_FILE_SERVING_TOKEN: '"12312"',
  ENABLE_LOGROCKET: '"false"',
  LOGROCKET_APP_ID: '"l2mogl/modeling-tool"',
  INTERCOM_ID: '"ujvkp2qi"',
  USERFLOW_KEY: '"ct_bf6v3bkourdtfo2jgkimvr4pfi"',
  ENABLE_PUBLIC_DATASET: '"true"',
  ENABLE_BILLING_LINK: '"true"',
  ENABLE_SERVING: '"true"',
  ENABLE_FOLDER_LOADING: '"true"',
  NO_KC: '"false"',
  AUTH_METHOD: '"Auth0"', // Auth0, KeyCloak
  AUTH0_DOMAIN: '"dev-ymwf5efb.us.auth0.com"',
  AUTH0_CLIENT_ID: '"AcXo2McPteR0CkzXZyIym9OrCMg3SvgP"',
});
