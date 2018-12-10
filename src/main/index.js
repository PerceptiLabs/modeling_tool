'use strict';

import { app, BrowserWindow, Menu, ipcMain, dialog } from 'electron'
import ua               from 'universal-analytics'
import { autoUpdater }  from 'electron-updater'

let mainWindow;
//const visitor = ua('UA-129392553-1');
const visitor = ua('UA-114940346-1');
const UpdateUrl = 'https://electron-release-server.azurewebsites.net/updates';
const mainMenu = [
  {
    label: 'File',
    submenu: [
      {label: 'New',                  click() {mainWindow.webContents.send('newNetwork')}},
      {label: 'Open trained model',   click() {mainWindow.webContents.send('closeApp', 'whoooooooh!');  }},
      {label: 'Save trained model',   click() {  }},
      {label: 'Open untrained model', click() {mainWindow.webContents.send('openNetwork')}},
      {label: 'Save untrained model', click() {mainWindow.webContents.send('saveNetwork')}},
      {type: 'separator'},
      {role: 'quit'}
    ]
  },
  {
    label: 'Edit',
    submenu: [
      {role: 'undo'},
      {role: 'redo'},
      {type: 'separator'},
      {role: 'cut'},
      {role: 'copy'},
      {role: 'paste'},
      {role: 'delete', accelerator: 'Shift+Delete',},
      {role: 'selectall'},
    ]
  },
  {
    label: 'Settings',
    submenu: [
      {label: 'Hyperparameters', click() {mainWindow.webContents.send('asynchronous-reply', 'whoooooooh!')}},
    ]
  },
  {
    label: 'Help',
    submenu: [
      {label: 'Help',   click() { require('electron').shell.openExternal('https://www.perceptilabs.com/html/product.html#tutorials')}},
      {label: 'About',  click() { require('electron').shell.openExternal('https://www.perceptilabs.com/')}}
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
  //? `http://localhost:9080`
  ? `http://127.0.0.1:9080`
  : `file://${__dirname}/index.html`;

function createWindow () {

  /**
   * Initial window options
   */
  mainWindow = new BrowserWindow({
    height: 768,
    width: 1024,
    minHeight: 768,
    minWidth: 1024,
    backgroundColor: '#383F50',
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

  const menuCustom = Menu.buildFromTemplate(mainMenu);
  Menu.setApplicationMenu(menuCustom);


  ipcMain.on('acceptClose', (event, arg) => {
    if (process.platform !== 'darwin') {
      app.quit()
    }
  });

  visitor.pageview("/").send();

  mainWindow.on('closed', () => {
    // mainWindow.webContents.send('closeApp');
    // ipcMain.on('acceptClose', (event, arg) => {
    //   mainWindow = null
    // })
    mainWindow = null
  });
  /**
   * start auto update
   */
  autoUpdater.setFeedURL(UpdateUrl);
  //autoUpdater.checkForUpdates();
  autoUpdater.checkForUpdatesAndNotify();
  // if (process.env.NODE_ENV === 'production') {
  //   autoUpdater.checkForUpdates();
  // }
}

app.on('ready', createWindow);

app.on('before-quit', (event) => {
  //event.preventDefault();
  mainWindow.webContents.send('closeApp', 'before-quit');
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
  mainWindow.webContents.send('closeApp', 'window-all-closed');
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
// autoUpdater.requestHeaders = { "PRIVATE-TOKEN": "Personal access Token" };
// autoUpdater.autoDownload = true;

// autoUpdater.setFeedURL({
//   provider: "generic",
//   url: "https://gitlab.com/_example_repo_/-/jobs/artifacts/master/raw/dist?job=build"
// });

autoUpdater.on('checking-for-update', ()=> {
  console.log('Checking for update...');
  mainWindow.webContents.send('info', 'Checking for update...!');
});
autoUpdater.on('update-available', (info)=> {
  mainWindow.webContents.send('info', 'Update available.');
});
autoUpdater.on('update-not-available', (info)=> {
  mainWindow.webContents.send('info', 'Update not available.');
});
autoUpdater.on('error', (err)=> {
  mainWindow.webContents.send('info', 'Error in auto-updater. ' + err);
});
autoUpdater.on('download-progress', (progressObj)=> {
  let log_message = `Download speed: ${progressObj.bytesPerSecond} - Downloaded ${progressObj.percent}% = ${progressObj.transferred}/${progressObj.total}`;
  mainWindow.webContents.send('info', log_message);
});
autoUpdater.on('update-downloaded', (event, releaseNotes, releaseName) => {
  mainWindow.webContents.send('info', 'Update downloaded');

  const dialogOpts = {
    type: 'info',
    buttons: ['Restart', 'Later'],
    title: 'Application Update',
    message: process.platform === 'win32' ? releaseNotes : releaseName,
    detail: 'A new version has been downloaded. Restart the application to apply the updates.'
  };

  dialog.showMessageBox(dialogOpts, (response) => {
    if (response === 0) autoUpdater.quitAndInstall()
  })
  // setTimeout(function () {
  //   autoUpdater.quitAndInstall();
  // }, 500);
});




export default mainWindow
