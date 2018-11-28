'use strict';

import { app, BrowserWindow, Menu, ipcMain } from 'electron'
import ua from 'universal-analytics'
var visitor = ua('UA-129392553-1');

let mainWindow;
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
  mainWindow.webContents.openDevTools();
  mainWindow.loadURL(winURL);

  const menuCustom = Menu.buildFromTemplate(mainMenu);
  Menu.setApplicationMenu(menuCustom);


  ipcMain.on('acceptClose', (event, arg) => {
    if (process.platform !== 'darwin') {
      app.quit()
    }
  })

  visitor.pageview("/").send();

  mainWindow.on('closed', () => {
    // mainWindow.webContents.send('closeApp');
    // ipcMain.on('acceptClose', (event, arg) => {
    //   mainWindow = null
    // })
    mainWindow = null
  })
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

/*
import { autoUpdater } from 'electron-updater'

autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall()
})

app.on('ready', () => {
  if (process.env.NODE_ENV === 'production') autoUpdater.checkForUpdates()
})
 */
export default mainWindow
