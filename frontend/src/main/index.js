'use strict';

import { app, BrowserWindow,
  Menu, ipcMain, dialog} from 'electron'
import { autoUpdater }   from 'electron-updater'
import ua                from 'universal-analytics'

autoUpdater.autoDownload = false;

let mainWindow;

let visitor;
let loginPage = '/';

const theFirstInstance = app.requestSingleInstanceLock();

if (!theFirstInstance) app.quit();
else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus()
    }
  });
}

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
    height: 600,
    width: 800,
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
   * listeners for the action button
   */
  mainWindow.on('enter-full-screen', ()=> {
    mainWindow.webContents.send('show-mac-header', false);
  });
  mainWindow.on('leave-full-screen', ()=> {
    mainWindow.webContents.send('show-mac-header', true);
  });
  mainWindow.on('maximize', ()=> {
    mainWindow.webContents.send('show-restore-down-icon', true);
  });
  mainWindow.on('unmaximize', ()=> {
    mainWindow.webContents.send('show-restore-down-icon', false);
  });

  /**
   * add custom menu
   */
  ipcMain.on('app-menu', (event, menuJson) => {
    menuJson.forEach((menuItem)=> {
      if(menuItem.submenu.length) {
        menuItem.submenu.forEach((subMenuItem)=> {
          console.log(!subMenuItem.role);
          if(!subMenuItem.role) subMenuItem.click = ()=> {mainWindow.webContents.send(`menu-event-${subMenuItem.label}`)}
        })
      }
    });
    const menuCustom = Menu.buildFromTemplate(menuJson);
    Menu.setApplicationMenu(menuCustom);
  });
  /**
   * listeners for the renderer process
   */
  ipcMain.on('open-dialog', (event, options)=> {
    dialog.showOpenDialog(mainWindow, options, (files) => {
      mainWindow.webContents.send('open-dialog_path', files);
    })
  });
  ipcMain.on('open-save-dialog', (event, options)=> {
    dialog.showSaveDialog(mainWindow, options, (files) => {
      mainWindow.webContents.send('open-save-dialog_path', files);
    })
  });
  ipcMain.on('app-close', (event, pid)=> {
    closeApp(pid)
  });
  ipcMain.on('app-minimize', (event, arg)=> {
    if(process.platform === 'darwin') {
      mainWindow.isMaximized()
        ? mainWindow.unmaximize()
        : mainWindow.minimize()
    }
    else {
      mainWindow.minimize();
    }
  });
  ipcMain.on('app-maximize', (event, arg)=> {
    mainWindow.isMaximized()
      ? mainWindow.unmaximize()
      : mainWindow.maximize()
  });
  ipcMain.on('app-ready', (event)=> {
    mainWindow.maximize();
    mainWindow.checkForUpdates();
    mainWindow.webContents.send('get-app-version', app.getVersion());
  });
  ipcMain.on('check-update', (event)=> {
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
  ipcMain.on('change-route', (event, arg)=> {
    visitor = ua('UA-114940346-1', arg.id, {strictCidFormat: false});
    if (arg.path !== loginPage) visitor.pageview(arg.path).send();
  });

  /**
   * start auto update
   */
  mainWindow.checkForUpdates = function() {
    if(process.env.NODE_ENV !== 'development') {
      mainWindow.webContents.send('info', 'checkForUpdates');
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

/**
 * APP listeners
 */
app.on('ready', createWindow);

// app.on('window-all-closed', ()=> {
//   if (process.platform !== 'darwin') closeApp()
// });

app.on('activate', ()=> {
  if (mainWindow === null) createWindow()
});

function closeApp(pid) {
  if(pid) {
    mainWindow.hide();
    setTimeout(() => {
      try       { process.kill(pid) }
      catch (e) { console.log(e) }
      finally   { app.quit() }
    }, 3000)
  }
  else app.quit()
}
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
  console.log('error upload', err);
  console.log('error upload message', err.message);
  console.log('error upload stack', err.stack);
  mainWindow.webContents.send('update-error', err.message);
});
autoUpdater.on('download-progress', (progressObj)=> {
  mainWindow.webContents.send('update-downloading', progressObj.percent);
  mainWindow.setProgressBar(progressObj.percent / 100);
});
autoUpdater.on('update-downloaded', (event, info)=> {
  mainWindow.webContents.send('update-completed', info);
});

export default mainWindow
