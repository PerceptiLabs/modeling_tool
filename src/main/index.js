'use strict';

import { app, BrowserWindow, Menu, ipcMain, dialog }  from 'electron'
import { autoUpdater }                                from 'electron-updater'
// import { JSONStorage }                                from 'node-localstorage';
// import uuid                                           from 'uuid/v4';
import ua                                             from 'universal-analytics'

autoUpdater.autoDownload = false;

let mainWindow;
// const nodeStorage = new JSONStorage(app.getPath('userData'));
// const userId      = nodeStorage.getItem('userid') || uuid();
//const visitor     = ua('UA-114940346-1', {uid: userId});
let visitor;
let loginPage = '/';

const mainMenu = [
  {
    label: 'File',
    submenu: [
      {label: 'New',                                    click() {mainWindow.webContents.send('newNetwork')}},
      {label: 'Open trained model',   enabled: false,   click() {mainWindow.webContents.send('info', 'whoooooooh!');  }},
      {label: 'Save trained model',   enabled: false,   click() {  }},
      {label: 'Open untrained model',                   click() {mainWindow.webContents.send('openNetwork')}},
      {label: 'Save untrained model',                   click() {mainWindow.webContents.send('saveNetwork')}},
      {type: 'separator'},
      {label: 'Log out',                                click() {mainWindow.webContents.send('logOut')}},
      {label: 'Quit PersceptiLabs',                     click() {mainWindow.webContents.send('closeApp')}},
    ]
  },
  {
    label: 'Edit',
    submenu: [
      {role: 'undo', enabled: false},
      {role: 'redo', enabled: false},
      {type: 'separator', enabled: false},
      {role: 'cut', enabled: false},
      {role: 'copy', enabled: false},
      {role: 'paste', enabled: false},
      {role: 'delete', accelerator: 'Delete', enabled: false},
      {role: 'selectall', enabled: false},
    ]
  },
  {
    label: 'Settings',
    submenu: [
      {label: 'Hyperparameters', enabled: false, click() {mainWindow.webContents.send('asynchronous-reply', 'whoooooooh!')}},
    ]
  },
  {
    label: 'Help',
    submenu: [
      {label: 'Version ' + app.getVersion()},
      {label: 'Help',   click() { require('electron').shell.openExternal('https://www.perceptilabs.com/html/product.html#tutorials')}},
      {label: 'About',  click() { require('electron').shell.openExternal('https://www.perceptilabs.com/')}},
      {label: 'Check for updates',  click() {mainWindow.checkForUpdates()}},
    ]
  }
];


/**
 * Set `__static` path to static files in production
 * https://simulatedgreg.gitbooks.io/electron-vue/content/en/using-static-assets.html
 */
if (process.env.NODE_ENV !== 'development') {
  global.__static = require('path').join(__dirname, '/static').replace(/\\/g, '\\\\')
}


const winURL = process.env.NODE_ENV === 'development'
  ? `http://127.0.0.1:9080`
  : `file://${__dirname}/index.html`;

function createWindow () {
  /**
   * Initial window options
   */
  mainWindow = new BrowserWindow({
    frame: false,
    height: 768,
    width: 1024,
    minHeight: 600,
    minWidth: 800,
    useContentSize: true,
    webPreferences: {
      //contextIsolation: true,
      //nodeIntegration: false,
      webSecurity: false,
      //plugins: true,
    }
  });

  //mainWindow.webContents.openDevTools();
  mainWindow.loadURL(winURL);

  mainWindow.on('closed', () => {
    mainWindow = null
  });

  /**
   * add custom menu
   */
  if(process.platform === 'darwin') {
    const menuCustom = Menu.buildFromTemplate(mainMenu);
    Menu.setApplicationMenu(menuCustom);
  }

  /**
   * listeners for the renderer process
   */
  ipcMain.on('appClose', (event, arg) => {
    app.quit()
  });
  ipcMain.on('appMinimize', (event, arg) => {
    if(process.platform === 'darwin' && mainWindow.isFullScreen()) {
      mainWindow.setFullScreen(false);
      setTimeout(()=>{mainWindow.minimize();}, 1000)
    }
    else {
      mainWindow.isMinimized()
        ? mainWindow.restore()
        : mainWindow.minimize()
    }

  });
  ipcMain.on('appMaximize', (event, arg) => {
    if(process.platform === 'darwin') {
      mainWindow.isMaximized()
        ? mainWindow.setFullScreen(false)
        : mainWindow.setFullScreen(true)
    }
    else {
      mainWindow.isMaximized()
        ? mainWindow.unmaximize()
        : mainWindow.maximize()
    }
  });
  ipcMain.on('appReady', (event) => {
    mainWindow.checkForUpdates();
    mainWindow.webContents.send('getAppVersion', app.getVersion());
  });
  ipcMain.on('checkUpdate', (event, arg) => {
    mainWindow.checkForUpdates(arg);
    autoUpdater.on('update-not-available', (info)=> {
      mainWindow.webContents.send('update-not-finded', info);
    });
  });
  ipcMain.on('update-start', (info)=> {
    autoUpdater.downloadUpdate();
  });
  ipcMain.on('restart-app-after-update', (info)=> {
    autoUpdater.quitAndInstall();
  });
  

  /**
   * google analytics
   */
  ipcMain.on('changeRoute', (event, arg) => { 
    visitor = ua('UA-114940346-1', arg.id, {strictCidFormat: false})
    if (arg.path !== loginPage) visitor.pageview(arg.path).send();
  });
  /**
   * start auto update
   */
  mainWindow.checkForUpdates = function() {
    if (process.env.NODE_ENV !== 'development') {
      mainWindow.webContents.send('info', 'checkForUpdates');
      const UpdateUrl = 'https://uantumetdisks.blob.core.windows.net/updates-admin/';
      const UpdateOpt = {
        provider: 'generic',
        url: ''
      };
      switch (process.platform) {
        case 'win32':
          UpdateOpt.url = UpdateUrl + 'win/';
          break;
        case 'darwin':
          UpdateOpt.url = UpdateUrl + 'ios/';
          break;
        case 'linux':
          UpdateOpt.url = UpdateUrl + 'linux/';
          break;
      }
      autoUpdater.setFeedURL(UpdateOpt);
      autoUpdater.checkForUpdates();
    }
  }
}

app.on('ready', createWindow);

app.on('before-quit', (event) => {
  //event.preventDefault();
  //mainWindow.webContents.send('closeApp', 'before-quit');
});
// app.on('will-quit', (event) => {
//   //event.preventDefault();
//   mainWindow.webContents.send('closeApp', 'will-quit');
// });
// app.on('quit', (event) => {
//   //event.preventDefault();
//   mainWindow.webContents.send('closeApp', 'quit');
// });


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
});



/**
 * Auto Updater
 *
 * Uncomment the following code below and install `electron-updater` to
 * support auto updating. Code Signing with a valid certificate is required.
 * https://simulatedgreg.gitbooks.io/electron-vue/content/en/using-electron-builder.html#auto-updating
 */

autoUpdater.on('checking-for-update', (info)=> {
  //console.log('Checking for update...');
  mainWindow.webContents.send('info', {type: 'Checking for update...!', info});
});
autoUpdater.on('update-available', (info)=> {
  mainWindow.webContents.send('info', {type: 'Update available.', info});
  mainWindow.webContents.send('update-finded', info);
});

autoUpdater.on('error', (err)=> {
  mainWindow.webContents.send('info', 'Error in auto-updater. ' + err);
});
autoUpdater.on('download-progress', (progressObj)=> {
  mainWindow.webContents.send('percent-progress', progressObj.percent);
  let log_message = `Download speed: ${progressObj.bytesPerSecond}, Downloaded: ${progressObj.percent}%`;
  mainWindow.webContents.send('info', log_message);
  mainWindow.setProgressBar(progressObj.percent / 100);
});
autoUpdater.on('update-downloaded', (event, releaseNotes, releaseName) => {
  mainWindow.webContents.send('info', 'Update downloaded');
  mainWindow.webContents.send('download-completed');
});

export default mainWindow
