'use strict'
require('./check-versions')()

// Add the env file as process.env
const isDocker = process.argv[2] === "docker";
const envFile = isDocker ?
  '../config/docker.env':
  '../config/prod.env';

process.env.NODE_ENV = 'production'

const ora = require('ora')
const rm = require('rimraf')
const path = require('path')
const chalk = require('chalk')
const webpack = require('webpack')
const config = require('../config')
const webpackConfig = require('./webpack.prod.conf')

function add_process_env(envFile){
  const fs = require('fs')
  const packageJson = fs.readFileSync('./package.json')
  const version = JSON.parse(packageJson).version || 0
  const envs = Object.assign(require(envFile), {'PACKAGE_VERSION': `"${version}"`})

  // http://vuejs.github.io/vue-loader/en/workflow/production.html
  webpackConfig.plugins.unshift(
    new webpack.DefinePlugin({
    'process.env': envs
  })
  );
}

add_process_env(envFile);

const msg = isDocker ?
  'building for docker...' :
  'building for production...';
const spinner = ora(msg);
spinner.start()

rm(path.join(config.build.assetsRoot, config.build.assetsSubDirectory), err => {
  if (err) throw err
  webpack(webpackConfig, (err, stats) => {
    spinner.stop()
    if (err) throw err
    process.stdout.write(stats.toString({
      colors: true,
      modules: false,
      children: false, // If you are using ts-loader, setting this to true will make TypeScript errors show up during build.
      chunks: false,
      chunkModules: false
    }) + '\n\n')

    if (stats.hasErrors()) {
      console.log(chalk.red('  Build failed with errors.\n'))
      process.exit(1)
    }

    console.log(chalk.cyan('  Build complete.\n'))
    console.log(chalk.yellow(
      '  Tip: built files are meant to be served over an HTTP server.\n' +
      '  Opening index.html over file:// won\'t work.\n'
    ))
  })
})
