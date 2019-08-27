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
};ß