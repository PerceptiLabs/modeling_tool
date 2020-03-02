'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  HUBSPOT_SCRIPT: '"//js.hs-scripts.com/7122301.js"'
})
