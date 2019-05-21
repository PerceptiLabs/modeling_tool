import {remote} from "electron";
import fs from 'fs';
import configApp from '@/core/globalSettings.js'

// const findIndexId = function (arr, ID) {
//   return arr.findIndex(function(item) {return item.layerId == ID});
// };

const openLoadDialog = function (options) {
  return new Promise((success, reject) => {
    let dialog = remote.dialog;
    dialog.showOpenDialog(options, (files) => {
      if (files !== undefined) {
        success(files)
      }
      else reject();
    })
  })
};

const loadPathFolder = function (customOptions) {
  const optionsDefault = {
    title:"Load folder",
    properties: ['openDirectory']
  };
  let options = optionsDefault || customOptions;
  return openLoadDialog(options);
};

const loadNetwork = function (pathArr) {
  return readFilePromiseNative(pathArr[0])
    .then((data) => {
      let net = JSON.parse(data.toString());
      this.$store.dispatch('mod_workspace/ADD_network', {'network': net.network, 'ctx': this});
    }
  );
  function readFilePromiseNative(path) {
    return new Promise((success, reject) => {
      fs.readFile(path, (err, data) => {
        if (err) {
          console.log(err);
          return reject();
        }
        return success(data);
      })
    });
  };
};

const generateID = function() {
  return Date.now().toString();
};

const calcLayerPosition = function (position) {
  const grid = configApp.workspaceGrid;
  return Math.round(position/grid)*grid
};

const throttleEv = function (func, ms) {
  var isThrottled = false,
    savedArgs,
    savedThis;
  let delay = 33 || ms; //30Hz
  function wrapper() {

    if (isThrottled) { // (2)
      savedArgs = arguments;
      savedThis = this;
      return;
    }

    func.apply(this, arguments); // (1)

    isThrottled = true;

    setTimeout(function() {
      isThrottled = false; // (3)
      if (savedArgs) {
        wrapper.apply(savedThis, savedArgs);
        savedArgs = savedThis = null;
      }
    }, delay);
  }

  return wrapper;
};

export {openLoadDialog, loadNetwork, generateID, loadPathFolder, calcLayerPosition, throttleEv}