'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  HUBSPOT_ID: '"7122301.js"',
  GOOGLE_ANALYTICS_ID: '"UA-114940346-2"',
  FORCE_DEFAULT_PROJECT: '"false"'
})
