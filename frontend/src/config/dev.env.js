'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  HUBSPOT_ID: '"7122301.js"',
  GOOGLE_ANALYTICS_ID: '"UA-114940346-2"',
  FORCE_DEFAULT_PROJECT: '"true"',
  KEYCLOAK_BASE_URL: '"https://keycloak.dev.perceptilabs.com:8443/auth"',
  KEYCLOAK_REALM: '"vue-perceptilabs"',
  KEYCLOAK_CLIENT_ID: '"vue-perceptilabs-client-id"',
  GITHUB_CLIENT_ID: '"094271b0edb47c75dc24"',
  PL_FILE_SERVING_TOKEN: '"12312"',
  ENABLE_LOGROCKET: '"false"',
  LOGROCKET_APP_ID: '"l2mogl/modeling-tool"',
  ENABLE_DATAWIZARD: '"true"',
  INTERCOM_ID: '"ujvkp2qi"',
})
