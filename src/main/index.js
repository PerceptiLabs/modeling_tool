'use strict';

import { app, BrowserWindow, Menu, ipcMain, dialog }  from 'electron'
import { autoUpdater }                                from 'electron-updater'
import ua                                             from 'universal-analytics'

autoUpdater.autoDownload = false;

let mainWindow;

let visitor;
let loginPage = '/';

//accelerator: process.platform === 'darwin' ? 'Alt+Command+I' : 'Ctrl+Shift+I',

// const mainMenu = [
//   {
//     label: 'File',
//     submenu: [
//       {label: 'Home',                                     enabled: true,  click() {mainWindow.webContents.send('info', 'whoooooooh!');  }},
//       {label: 'New',        accelerator: 'Ctrl+N',        enabled: true,  click() {mainWindow.webContents.send('newNetwork')}},
//       {label: 'Open',       accelerator: 'Ctrl+O',        enabled: true,  click() {mainWindow.webContents.send('openNetwork')}},
//       {label: 'Save',       accelerator: 'Ctrl+S',        enabled: true,  click() {mainWindow.webContents.send('saveNetwork')}},
//       {label: 'Save as...', accelerator: 'Ctrl+Shift+S',  enabled: true,  click() {mainWindow.webContents.send('saveNetwork')}},
//       {type: 'separator'},
//       {label: 'Log out',    accelerator: 'Ctrl+F4',       enabled: true,  click() {mainWindow.webContents.send('logOut')}},
//       {label: 'Exit',       accelerator: 'ALT+F4',                        click() {mainWindow.webContents.send('closeApp')}},
//     ]
//   },
//   {
//     label: 'Edit',
//     submenu: [
//       {label: 'Undo',                         enabled: false},
//       {label: 'Redo',                         enabled: false},
//       {type: 'separator'},
//       {label: 'Cut',                          enabled: false},
//       {label: 'Copy',                         enabled: false},
//       {label: 'Paste',                        enabled: false},
//       {label: 'Delete',                       enabled: false},
//       {label: 'Select all',                   enabled: false},
//     ]
//   },
//   {
//     label: 'Operations ',
//     submenu: [
//       {
//         label: 'Data',
//         submenu: [
//           {label: 'Data',                     enabled: false},
//           {label: 'Data Environment',         enabled: false},
//         ]
//       },
//       {
//         label: 'Process ',
//         submenu: [
//           {label: 'Reshape',                  enabled: false},
//           {label: 'Word embedding',           enabled: false},
//           {label: 'Grayscale',                enabled: false},
//           {label: 'One hot',                  enabled: false},
//           {label: 'Crop',                     enabled: false},
//         ]
//       },
//       {
//         label: 'Deep learning',
//         submenu: [
//           {label: 'Fully connected',          enabled: false},
//           {label: 'Convolution',              enabled: false},
//           {label: 'Deconvolution',            enabled: false},
//           {label: 'Recurrent',                enabled: false}
//         ]
//       },
//       {
//         label: 'Math',
//         submenu: [
//           {label: 'Argmax',                   enabled: false},
//           {label: 'Merge',                    enabled: false},
//           {label: 'Split',                    enabled: false},
//           {label: 'Softmax',                  enabled: false}
//         ]
//       },
//       {
//         label: 'Training',
//         submenu: [
//           {label: 'Normal',                   enabled: false},
//           {label: 'Normal+Data',              enabled: false},
//           {label: 'Reinforcement learning',   enabled: false},
//           {label: 'Genetic algorithm',        enabled: false},
//           {label: 'Dynamic routing',          enabled: false}
//         ]
//       },
//       {
//         label: 'Classic machine learning',
//         submenu: [
//           {label: 'K means clustering',       enabled: false},
//           {label: 'DBSCAN',                   enabled: false},
//           {label: 'kNN',                      enabled: false},
//           {label: 'Random forrest',           enabled: false},
//           {label: 'Support vector machine',   enabled: false}
//         ]
//       },
//       {
//         label: 'Custom'
//       },
//     ]
//   },
//   {
//     label: 'Window',
//     submenu: [
//       {label: 'Edit profile',                 enabled: false},
//       {label: 'History',                      enabled: false}
//     ]
//   },
//   {
//     label: 'Settings',
//     submenu: [
//       {label: 'Hyperparameters',              enabled: false}
//     ]
//   },
//   {
//     label: 'Help',
//     submenu: [
//       {label: 'Help',                                                 click() { require('electron').shell.openExternal('https://www.perceptilabs.com/html/product.html#tutorials')}},
//       {label: 'About',                                                click() { require('electron').shell.openExternal('https://www.perceptilabs.com/')}},
//       {label: 'Tutorial mode',                enabled: true,  },
//       {label: 'Check for updates',                                    click() {mainWindow.checkForUpdates()}},
//       {type: 'separator'},
//       {label: 'Version ' + app.getVersion()},
//     ]
//   }
// ];


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
    frame: !!(process.platform === 'darwin'),
    height: 768,
    width: 1024,
    minHeight: 600,
    minWidth: 800,
    useContentSize: true,
    titleBarStyle: "hidden",
    webPreferences: {
      devTools: true, // false close devtool
      //contextIsolation: true,
      nodeIntegration: true,
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
  ipcMain.on('app-menu', (event, menuJson) => {
    menuJson.forEach((menuItem)=> {
      if(menuItem.submenu.length) {
        menuItem.submenu.forEach((subMenuItem)=> {
          subMenuItem.click = ()=> {mainWindow.webContents.send('menu-event', subMenuItem.id);  }
        })
      }
    });
    const menuCustom = Menu.buildFromTemplate(menuJson);
    Menu.setApplicationMenu(menuCustom);
  });
  /**
   * listeners for the renderer process
   */
  ipcMain.on('app-close', (event, arg) => {
    app.quit()
  });
  ipcMain.on('app-minimize', (event, arg) => {
    if(process.platform === 'darwin' && mainWindow.isFullScreen()) {
      //mainWindow.frame = false;
      mainWindow.setFullScreen(false);
      setTimeout(()=>{mainWindow.minimize();}, 1000)
    }
    else {
      mainWindow.isMinimized()
        ? mainWindow.restore()
        : mainWindow.minimize()
    }

  });
  ipcMain.on('app-maximize', (event, arg) => {
    if(process.platform === 'darwin') {
      //mainWindow.frame = true;
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
  ipcMain.on('app-ready', (event) => {
    mainWindow.checkForUpdates();
    mainWindow.webContents.send('getAppVersion', app.getVersion());
  });
  ipcMain.on('check-update', (event) => {
    mainWindow.checkForUpdates();
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
  ipcMain.on('change-route', (event, arg) => {
    visitor = ua('UA-114940346-1', arg.id, {strictCidFormat: false})
    if (arg.path !== loginPage) visitor.pageview(arg.path).send();
  });
  /**
   * start auto update
   */
  mainWindow.checkForUpdates = function() {
    if(process.env.NODE_ENV !== 'development') {
      //mainWindow.webContents.send('info', 'checkForUpdates');
      const UpdateUrl = 'https://uantumetdisks.blob.core.windows.net/updates-admin/';
      const UpdateOpt = {
        provider: 'generic',
        url: ''
      };
      switch (process.platform) {
        case 'win32':
          UpdateOpt.url = UpdateUrl + 'winDev/';
          break;
        case 'darwin':
          UpdateOpt.url = UpdateUrl + 'iosDev/';
          break;
        case 'linux':
          UpdateOpt.url = UpdateUrl + 'linuxDev/';
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
  mainWindow.webContents.send('checking-for-update', info);
});
autoUpdater.on('update-not-available', (info)=> {
  mainWindow.webContents.send('update-not-available', info);
});
autoUpdater.on('update-available', (info)=> {
  mainWindow.webContents.send('update-available', info);
});
autoUpdater.on('error', (err)=> {
  mainWindow.webContents.send('update-error', err);
});
autoUpdater.on('download-progress', (progressObj)=> {
  mainWindow.webContents.send('update-downloading', progressObj.percent);
  mainWindow.setProgressBar(progressObj.percent / 100);
});
autoUpdater.on('update-downloaded', (event, info) => {
  mainWindow.webContents.send('update-completed', info);
});

export default mainWindow
