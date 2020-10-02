let shell = null;
let ipcRenderer = null;
let fs = null;

if(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1) {
  const electron = require('electron');
  const fileSystem = require('fs');
  shell = electron.shell;
  ipcRenderer = electron.ipcRenderer;
  fs = fileSystem;
}
import store from '@/store'

import {
  workspaceGrid,
  pathSlash,
  hideSidebarOnBreakpoint,
  sidebarNavCoefficientScaleCalculateFromHeight
} from '@/core/constants.js'

/*modal window*/
const openLoadDialog = function (options) {
  return new Promise((success, reject) => {
    ipcRenderer.on('open-dialog_path', (event, path) => {
      ipcRenderer.removeAllListeners('open-dialog_path');
      !!(path && path.length) ? success(path) : reject();
    });
    ipcRenderer.send('open-dialog', options);
  });
};

const openSaveDialog = function (options) {
  console.log('openSaveDialog', options);
  return new Promise((success, reject) => {
    ipcRenderer.on('open-save-dialog_path', (event, path) => {
      ipcRenderer.removeAllListeners('open-save-dialog_path');
      !!(path && path.length) ? success(path) : reject();
    });
    ipcRenderer.send('open-save-dialog', options);
  });
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
        store.dispatch('globalView/GP_errorPopup', `An error occurred while creating the file: ${err.message}`);
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

const getDefaultProjectPathForOs = function() {
  if (isOsWindows()) {
    return '~/Documents/PerceptiLabs'; //the path to MyDocuments is resolved in Kernel
  } else if (isOsMacintosh() || isOsLinux()) {
    return '~/Documents/PerceptiLabs';
  } 
}

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
  if(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1) {
    shell.openExternal(url);
  } else {
    let link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('target', '_blank');
    link.click();
  }
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
const isOsMacintosh = () => {
  return window.navigator.platform.indexOf('Mac') > -1
};

const isOsLinux = () => {
  return /Linux/.test(window.navigator.platform);
  
};

const isDesktopApp = () => {
  const userAgent = window.navigator.userAgent.toLowerCase();
  return (userAgent.indexOf(' electron/') > -1);
};

const shouldHideSidebar = () => {
  return document.documentElement.clientWidth <= hideSidebarOnBreakpoint;
};

const calculateSidebarScaleCoefficient = () => {
  const pageHeight = document.documentElement.clientHeight;
  if(pageHeight <= sidebarNavCoefficientScaleCalculateFromHeight) {
    document.documentElement.style.setProperty('--sidebar-scale-coefficient', (pageHeight / sidebarNavCoefficientScaleCalculateFromHeight).toString());
  } else {
    document.documentElement.style.setProperty('--sidebar-scale-coefficient', '1');
  }
};

const parseJWT = (jwt) => {
  if (!jwt) { return; }

  try {
    const payload = jwt.split('.')[1];
    if (payload) {
      return JSON.parse(window.atob(payload));
    }
  } catch (error) {
    console.error('parseJWT', error);
    return;
  }
};

const isElectron = () => {
  return navigator.userAgent.toLowerCase().indexOf(' electron/') > -1;
};
const isWeb = () => {
  return !(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1);
};

const setAppTypeRootClasses = () => {
  if(isWeb()) {
    document.body.classList.add('is-web');
    document.getElementsByTagName('html')[0].classList.add('is-web');
  } else {
    document.body.classList.add('is-electron');
    document.getElementsByTagName('html')[0].classList.add('is-electron');
  }
};

const fixFilepathSeparator = function fileUrl(filepath) {
  if (!filepath) { return filepath; }

  if (filepath.startsWith('\\\\')) {
    // if it's a network share, we have to keep the \\\\
    return '\\\\' + filepath.substring(2).replace(/\\/g, '/');
  }

  return filepath.replace(/\\/g, '/');
};

const debounce = function(callback, waitInMs) {

  let timerHandle;

  return function() {
    clearInterval(timerHandle);
    timerHandle = setTimeout(() => {

      callback.apply(this, arguments);

    }, waitInMs);
  }
}


const promiseWithTimeout = function (timeout, promise) {
  const timeoutPromise = new Promise((resolve, reject) => {
    const timerHandle = setTimeout(
      () => resolve(),
      timeout);
  });
  
  return Promise.race([
    promise,
    timeoutPromise
  ]);
}

const layerBgColor = function (componentName) {
  let className = '';
  switch (componentName) {
    case 'DataData':
    case 'DataEnvironment':
    case 'DataRandom':
      className = 'net-color-data';
      break;
    case 'DeepLearningFC':
    case 'DeepLearningConv':
    case 'DeepLearningDeconv':
    case 'DeepLearningRecurrent':
      className = 'net-color-learn-deep';
      break;
    case 'ProcessCrop':
    case 'ProcessEmbed':
    case 'ProcessGrayscale':
    case 'ProcessOneHot':
    case 'ProcessReshape':
    case 'ProcessRescale':
      className = 'net-color-process';
      break;
    case 'TrainNormal':
    case 'TrainGenetic':
    case 'TrainDynamic':
    case 'TrainReinforce':
    case 'TrainLoss':
    case 'TrainOptimizer':
    case 'TrainDetector':
    case 'TrainGan':
    case 'TrainGan':
    case 'TrainRegression':
      className = 'net-color-train';
      break;
    case 'MathArgmax':
    case 'MathMerge':
    case 'MathSplit':
    case 'MathSoftmax':
    case 'MathSwitch':
      className = 'net-color-math';
      break;
    case 'ClassicMLDbscans':
    case 'ClassicMLKMeans':
    case 'ClassicMLKNN':
    case 'ClassicMLRandomForest':
    case 'ClassicMLSVM':
      className = 'net-color-learn-class';
      break;
    case 'LayerContainer':
      className = 'net-color-layercontainer';
      break;
    case 'LayerCustom':
      className = 'net-color-custom';
      break;
  }
  return [className];
}

const layerBgColorTransparent = function (componentName) {
  let className = '';
  switch (componentName) {
    case 'DataData':
    case 'DataEnvironment':
      className = 'net-element-data';
      break;
    case 'DeepLearningFC':
    case 'DeepLearningConv':
    case 'DeepLearningDeconv':
    case 'DeepLearningRecurrent':
      className = 'net-element-learn-deep';
      break;
    case 'ProcessCrop':
    case 'ProcessEmbed':
    case 'ProcessGrayscale':
    case 'ProcessOneHot':
    case 'ProcessReshape':
    case 'ProcessRescale':
      className = 'net-element-process';
      break;
    case 'TrainNormal':
    case 'TrainGenetic':
    case 'TrainDynamic':
    case 'TrainReinforce':
    case 'TrainLoss':
    case 'TrainOptimizer':
    case 'TrainDetector':
      className = 'net-element-train';
      break;
    case 'MathArgmax':
    case 'MathMerge':
    case 'MathSplit':
    case 'MathSoftmax':
      className = 'net-element-math';
      break;
    case 'ClassicMLDbscans':
    case 'ClassicMLKMeans':
    case 'ClassicMLKNN':
    case 'ClassicMLRandomForest':
    case 'ClassicMLSVM':
      className = 'net-element-learn-class';
      break;
    case 'LayerContainer':
      className = 'net-element-layercontainer';
      break;
  }
  return [className];
}

const hashObject = function(inputObject) {
  const concatValues = Object.values(inputObject)
  .map(eo => eo.toString())
  .join('');

  return hashString(concatValues || '');
}

const hashString = s => s.split('').reduce((a,b) => (((a << 5) - a) + b.charCodeAt(0))|0, 0);

const createCoreNetwork = (network, currentNetworkUsingWeights = false) => {
  if (!network) { return null; }

  let layers = {};
  for(let layer in network.networkElementList) {
    const el = network.networkElementList[layer];
    if(el.componentName === 'LayerContainer') continue;

    /*prepare checkpoint*/
    const checkpointPath = {
      'load_checkpoint': true, // always true during testing
      'path': ''
    };

    if(el.checkpoint.length >= 2) {
      checkpointPath.path = el.checkpoint[1]
      
      if (checkpointPath.path.slice(-1) !== '/') {
        checkpointPath.path += '/';
      } else if (checkpointPath.path.slice(-1) !== '\\') {
        checkpointPath.path += '\\';
      }

      checkpointPath.path += 'checkpoint';
    } else {
      checkpointPath.path = network.apiMeta.location + '/checkpoint'
    }

    /*prepare elements*/
    layers[el.layerId] = {
      Name: el.layerName,
      Type: el.componentName,
      checkpoint: checkpointPath,
      endPoints: el.endPoints,
      Properties: el.layerSettings,
      Code: el.layerCode,
      backward_connections: el.backward_connections,
      forward_connections: el.forward_connections,
      visited: el.visited,
      previewVariable: el.previewVariable
    };

  }
  return layers;
}

const objectToQueryParams = (reqData) => {
  return  Object.keys(reqData).map(function(key) {
      return key + '=' + reqData[key];
    }).join('&');
}

export {
  openLoadDialog,
  openSaveDialog,
  loadPathFolder,
  filePCRead,
  filePCSave,
  projectPCSave,
  projectPathModel,
  folderPCDelete,
  getDefaultProjectPathForOs,
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
  fixFilepathSeparator,
  promiseWithTimeout,
  isOsWindows,
  isDesktopApp,
  shouldHideSidebar,
  calculateSidebarScaleCoefficient,
  parseJWT,
  isOsMacintosh,
  isElectron,
  isWeb,
  setAppTypeRootClasses,
  debounce,
  layerBgColor,
  layerBgColorTransparent,
  hashObject,
  hashString,
  createCoreNetwork,
  objectToQueryParams
}
