//import {shell, ipcRenderer }   from 'electron'
//import fs    from 'fs';
import store from '@/store'

import { workspaceGrid, pathSlash }   from '@/core/constants.js'

/*modal window*/
const openLoadDialog = function (options) {
/*  return new Promise((success, reject) => {
    ipcRenderer.on('open-dialog_path', (event, path) => {
      ipcRenderer.removeAllListeners('open-dialog_path');
      !!(path && path.length) ? success(path) : reject();
    });
    ipcRenderer.send('open-dialog', options);
  });*/
};

const openSaveDialog = function (options) {
/*  console.log('openSaveDialog', options);
  return new Promise((success, reject) => {
    ipcRenderer.on('open-save-dialog_path', (event, path) => {
      ipcRenderer.removeAllListeners('open-save-dialog_path');
      !!(path && path.length) ? success(path) : reject();
    });
    ipcRenderer.send('open-save-dialog', options);
  });*/
};

const loadPathFolder = function (customOptions) {
  const optionsDefault = {
    title:"Select folder",
    buttonLabel: "Select folder",
    properties: ['openDirectory']
  };
  let options = {...optionsDefault, ...customOptions};
  return openLoadDialog(options);
};


/*file actions*/
const filePCRead = function (path) {
  return new Promise((success, reject) => {
    fs.readFile(path, (err, data) => {
      return !!err ? reject(err) : success(data);
    })
  });
};

const filePCSave = function (fileName, fileContent) {
  return new Promise((success, reject) => {
    fs.writeFile(fileName, fileContent, (err, data) => {
      if(err) {
        store.dispatch('globalView/GP_errorPopup', `An error occurred creating the file ${err.message}`);
        return reject(err);
      }
      else return success(fileName)
    });
    return success(fileName)
  });
};

const projectPCSave = function (fileContent) {
  const projectPath = fileContent.networkRootFolder;
  if (!fs.existsSync(projectPath)){
    fs.mkdirSync(projectPath);
  }
  const jsonPath = projectPathModel(projectPath);
  return filePCSave(jsonPath, JSON.stringify(fileContent))
};

const projectPathModel = function (projectPath) {
  return `${projectPath}${pathSlash}model.json`
};

const folderPCDelete = function (path) {
  return new Promise((success, reject) => {
    if (!fs.existsSync(path)) success();
    const files = fs.readdirSync(path);
    if (files.length > 0) {
      files.forEach(function(filename) {
        if (fs.statSync(path + pathSlash + filename).isDirectory()) {
          folderPCDelete(path + pathSlash + filename)
        } else {
          fs.unlinkSync(path + pathSlash + filename)
        }
      });
    }
    fs.rmdirSync(path);
    success();
  });
};

/*encryption */
const encryptionData = function (data) {
  return JSON.stringify(data).split('').reverse().join('');
};
const decryptionData = function (data) {
  return JSON.stringify(data).split('').reverse().join('');
};

/*other*/
const generateID = function() {
  return Date.now().toString();
};

const calcLayerPosition = function (position) {
  const grid = workspaceGrid;
  return Math.round(position/grid)*grid
};

const throttleEv = function (func, ms) {
  var isThrottled = false,
    savedArgs,
    savedThis;
  let delay = ms || 33; //30Hz

  function wrapper() {

    if (isThrottled) {
      savedArgs = arguments;
      savedThis = this;
      return;
    }

    func.apply(this, arguments);

    isThrottled = true;

    setTimeout(function() {
      isThrottled = false;
      if (savedArgs) {
        wrapper.apply(savedThis, savedArgs);
        savedArgs = savedThis = null;
      }
    }, delay);
  }

  return wrapper;
};

const goToLink = function (url) {
  console.log(url);
  //shell.openExternal(url);
};

const deepCopy = function (object) {
  return JSON.parse(JSON.stringify(object))
};

const deepCloneNetwork = function (object) {
  return JSON.parse(JSON.stringify(
    object,
    (key, val)=> {
      if (key === 'calcAnchor') return undefined;
      else return val;
    },
    ' ')
  );
};

const isLocalStorageAvailable = function () {
  try {
      var storage = window['localStorage'],
          x = '__storage_test__';
      storage.setItem(x, x);
      storage.removeItem(x);
      return true;
  }
  catch(e) {
      return e instanceof DOMException && (
          // everything except Firefox
          e.code === 22 ||
          // Firefox
          e.code === 1014 ||
          // test name field too, because code might not be present
          // everything except Firefox
          e.name === 'QuotaExceededError' ||
          // Firefox
          e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
          // acknowledge QuotaExceededError only if there's something already stored
          storage && storage.length !== 0;
  }
}

const stringifyNetworkObjects = function (network) {
  return JSON.stringify(
    network,
    (key, val)=> {
      if (key === 'calcAnchor') return undefined;
      else return val;
    },
    ' ');
};

const isOsWindows = () => {
  const windowsUserAgent = [
    'Windows NT 10.0',
    'Windows NT 6.2',
    'Windows NT 6.1',
    'Windows NT 6.0',
    'Windows NT 5.1',
    'Windows NT 5.0',
  ];
  const userAgent = window.navigator.userAgent;
  return windowsUserAgent.map(windowsStr => userAgent.indexOf(windowsStr) !== -1).filter(itm => itm === true).length > 0;
};

export {
  openLoadDialog,
  openSaveDialog,
  loadPathFolder,
  filePCRead,
  filePCSave,
  projectPCSave,
  projectPathModel,
  folderPCDelete,
  encryptionData,
  decryptionData,
  generateID,
  calcLayerPosition,
  throttleEv,
  goToLink,
  deepCopy,
  deepCloneNetwork,
  isLocalStorageAvailable,
  stringifyNetworkObjects,
  isOsWindows,
}
