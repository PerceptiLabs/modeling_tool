const notarize = require('electron-notarize').notarize;

module.exports = async (context) => {
    const { electronPlatformName } = context;
    if (electronPlatformName === 'darwin') {
        try {
            console.log('Try notarize app');
            await notarize({
              appBundleId: 'com.perceptilabs.app',
              appPath: './dist/mac/PerceptiLabs.app',
              appleId: process.env.appleId,
              appleIdPassword: process.env.appleASP,
            });
            console.log('Success notarize');
        } catch (err) {
            console.log(err);
        }
  }
};


// require('dotenv').config();
// const { notarize } = require('electron-notarize');

// exports.default = async function notarizing(context) {
//   const { electronPlatformName, appOutDir } = context;  
//   if (electronPlatformName !== 'darwin') {
//     return;
//   }

//   const appName = context.packager.appInfo.productFilename;

//   return await notarize({
//     appBundleId: 'com.perceptilabs.app',
//               appPath: './dist/mac/PerceptiLabs.app',
//               appleId: process.env.appleId,
//               appleIdPassword: process.env.appleASP,
//   });
// };