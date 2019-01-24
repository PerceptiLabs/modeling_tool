'use strict'

process.env.BABEL_ENV = 'main'

const path = require('path')
const { dependencies } = require('../package.json')
const webpack = require('webpack')

const CopyWebpackPlugin = require('copy-webpack-plugin')

const BabiliWebpackPlugin = require('babili-webpack-plugin')

let usePlagin = [new webpack.NoEmitOnErrorsPlugin()];
// if(process.env.BUILD_TARGET === 'core_local') {
//   usePlagin = [
//     new webpack.NoEmitOnErrorsPlugin(),
//     new CopyWebpackPlugin([
//       {from:'core_local',to:'core_local'}
//     ]),
//   ]
// }
// else usePlagin = [new webpack.NoEmitOnErrorsPlugin()]

let mainConfig = {
  entry: {
    main: path.join(__dirname, '../src/main/index.js')
  },
  externals: [
    ...Object.keys(dependencies || {})
  ],
  module: {
    rules: [
      {
        test: /\.(js)$/,
        enforce: 'pre',
        exclude: /node_modules/,
        // use: {
        //   loader: 'eslint-loader',
        //   options: {
        //     formatter: require('eslint-friendly-formatter')
        //   }
        // }
      },
      {
        test: /\.js$/,
        use: 'babel-loader',
        exclude: /node_modules/
      },
      {
        test: /\.node$/,
        use: 'node-loader'
      }
    ]
  },
  node: {
    __dirname: process.env.NODE_ENV !== 'production',
    __filename: process.env.NODE_ENV !== 'production'
  },
  output: {
    filename: '[name].js',
    libraryTarget: 'commonjs2',
    path: path.join(__dirname, '../dist/electron')
  },
  plugins: usePlagin,
  resolve: {
    extensions: ['.js', '.json', '.node']
  },
  target: 'electron-main'
}

/**
 * Adjust mainConfig for development settings
 */
if (process.env.NODE_ENV !== 'production') {
  mainConfig.plugins.push(
    new webpack.DefinePlugin({
      '__static': `"${path.join(__dirname, '../static').replace(/\\/g, '\\\\')}"`
    })
  )
}

/**
 * Adjust mainConfig for production settings
 */
if (process.env.NODE_ENV === 'production') {
  mainConfig.plugins.push(
    new BabiliWebpackPlugin(),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': '"production"'
    })
  )
  // if(process.env.BUILD_TARGET === 'core_local') {
  //
  // }
  // else {
  //   mainConfig.plugins.push(
  //     new BabiliWebpackPlugin(),
  //     new webpack.DefinePlugin({
  //       'process.env.NODE_ENV': '"production"',
  //       'process.env.BUILD_TARGET': '"core_cloud"'
  //     })
  //   )
  // }
}

module.exports = mainConfig
