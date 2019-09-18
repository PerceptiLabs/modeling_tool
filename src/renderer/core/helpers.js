import {shell, ipcRenderer }   from 'electron'
import fs    from 'fs';
import store from '@/store'

import { workspaceGrid }   from '@/core/constants.js'

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
  //console.log('openSaveDialog', options);
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
    title:"Load folder",
    properties: ['openDirectory']
  };
  let options = {...optionsDefault, ...customOptions};
  //console.log(options);
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
      else {
        store.dispatch('globalView/GP_infoPopup', 'The file has been successfully saved');
        return success(fileName)
      }
    });
  });
};
const projectPCSave = function (projectPathArr, fileContent) {
  const projectPath = projectPathArr[0];
  if (!fs.existsSync(projectPath)){
    fs.mkdirSync(projectPath);
  }
  const jsonPath = `${projectPath}\\${fileContent.networkID}.json`;
  return filePCSave(jsonPath, JSON.stringify(fileContent))
};
const folderPCDelete = function (path) {
  return new Promise((success, reject) => {
    if (!fs.existsSync(path)) success();

    const files = fs.readdirSync(path);
    if (files.length > 0) {
      files.forEach(function(filename) {
        if (fs.statSync(path + "/" + filename).isDirectory()) {
          removeDir(path + "/" + filename)
        } else {
          fs.unlinkSync(path + "/" + filename)
        }
      });
    }
    fs.rmdir(path, (err)=> {
      if(err) reject(err);
      else success()
    });
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
  let delay = 33 || ms; //30Hz
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
  //console.log(url);
  shell.openExternal(url);
};

export {
  openLoadDialog,
  openSaveDialog,
  loadPathFolder,
  filePCRead,
  filePCSave,
  projectPCSave,
  folderPCDelete,
  encryptionData,
  decryptionData,
  generateID,
  calcLayerPosition,
  throttleEv,
  goToLink
}
