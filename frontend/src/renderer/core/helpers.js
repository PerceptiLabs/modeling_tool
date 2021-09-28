import cloneDeep from 'lodash.clonedeep';
import isJS from 'is_js';
import {
  workspaceGrid,
  pathSlash,
  hideSidebarOnBreakpoint,
  sidebarNavCoefficientScaleCalculateFromHeight
} from '@/core/constants.js'



const projectPathModel = function (projectPath) {
  return `${projectPath}${pathSlash}model.json`
};


const getDefaultProjectPathForOs = function() {
  return '~/Documents/PerceptiLabs'; //the path to MyDocuments is resolved in Kernel
};

const checkpointDirFromProject = function(projectPath) {
    return `${projectPath}/checkpoint`;
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

const calcLayerPosition = function (position, zoomScaleCoefficient = 1) {
  const grid = workspaceGrid * zoomScaleCoefficient;
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
  let link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('target', '_blank');
  link.setAttribute('rel', 'noopener noreferrer');
  link.click();
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
    case 'IoInput':
      className = 'net-color-data';
      break;
    case 'DeepLearningFC':
    case 'DeepLearningConv':
    case 'DeepLearningRecurrent':
    case 'PreTrainedResNet50':
    case 'PreTrainedVGG16':
    case 'PreTrainedMobileNetV2':
    case 'PreTrainedInceptionV3':
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
    case 'TrainRegression':
    case 'IoOutput':
      className = 'net-color-train';
      break;
    case 'MathArgmax':
    case 'MathMerge':
    case 'MathSplit':
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
    case 'DeepLearningRecurrent':
    case 'PreTrainedResNet50':
    case 'PreTrainedVGG16':
    case 'PreTrainedInceptionV3':
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

const removeChartData = (inputNetwork) => {

  let network = cloneDeep(inputNetwork);
  
  network = cleanNetworkElementListChartData(network);
  network = cleanNetworkSnapshotsChartData(network);
  if (network.networkMeta && network.networkMeta.chartsRequest)
    network.networkMeta.chartsRequest.timerID = null;
  return network;


  function cleanNetworkElementListChartData(net) {
    if (!net || !net['networkElementList']) { return net; }

    for (const key of Object.keys(net['networkElementList'])) {
      const layerObject = net['networkElementList'][key];
      if (!layerObject.hasOwnProperty('chartData')) { continue; }
  
      layerObject['chartData'] = {};
    }
    return net
  }

  function cleanNetworkSnapshotsChartData(net) {
    if (!net || !net['networkSnapshots']) { return net; }
    
    const networkHaveSnapshots = net.networkSnapshots && net.networkSnapshots.length > 0;

    if(networkHaveSnapshots) {
      for (const key of Object.keys(net['networkSnapshots'][0])) {
        const layerObject = net['networkSnapshots'][0][key];
        if (!layerObject.hasOwnProperty('chartData')) { continue; }
    
        layerObject['chartData'] = {};
      }
    }
   
    return net
  }
}

const removeNetworkSnapshots = (inputNetwork) => {
  if (!inputNetwork || !inputNetwork['networkSnapshots']) { return inputNetwork; }

  const network = cloneDeep(inputNetwork);
  delete network['networkSnapshots'];

  return network;
}
const setCookie = (name,value,days) => {
  let expires = "";
  if (days) {
      const date = new Date();
      date.setTime(date.getTime() + (days*24*60*60*1000));
      expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}
const getCookie = (name) => {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for(let i=0;i < ca.length;i++) {
      let c = ca[i];
      while (c.charAt(0)==' ') c = c.substring(1,c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

const eraseCookie = (name) => {   
  document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

export const arrayIncludeOrOmit = (array, value) => {
  const ix = array.indexOf(value);
  (ix !== -1) ? array.splice(ix, 1) : array.push(value);
  return array;
}
const sleep = m => new Promise(r => setTimeout(r, m));

export const isEnvDataWizardEnabled = () => {
  return process.env.ENABLE_DATAWIZARD === 'true';
}

export const isPublicDatasetEnabled = () => {
  return process.env.ENABLE_PUBLIC_DATASET === 'true';
}

export const isServingEnabled = () => {
  return process.env.ENABLE_SERVING === 'true';
};

export const getFirstElementFromObject = (data) => {
  if(!data) throw new Error('No object passed');
  return data[Object.keys(data)[0]];
};

export const removeKeysFromObject = (obj, removeKeys) => {
  return Object.keys(obj).reduce((acc, key) => ( removeKeys.includes(key) ? acc : {...acc, [key]: obj[key]} ), {});
}

export const isEmptyObject = (obj) => {
  return !obj || Object.keys(obj).length === 0;
}

export const isBrowserChromeOrFirefox = () => {
  return  (isJS.chrome() || isJS.firefox()) && navigator.userAgent.indexOf('Edg/') === -1;
}

export {
  projectPathModel,
  getDefaultProjectPathForOs,
  checkpointDirFromProject,  
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
  objectToQueryParams,
  removeChartData,
  removeNetworkSnapshots,
  setCookie,
  getCookie,
  eraseCookie,
  sleep
}
