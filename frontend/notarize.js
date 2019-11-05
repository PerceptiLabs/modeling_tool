const notarize = require('electron-notarize').notarize;
process.env.CSC_LINK = '../perceptilabs.p12'
process.env.CSC_KEY_PASSWORD = 'com.perceptilabs.app'
process.env.appleId = 'stetsenko.ant1@gmail.com'
process.env.appleASP = 'gvcc-xynd-weyn-uhym'
console.log('Notarize');
//xcrun altool --notarize-app --primary-bundle-id "perceptilabs.0.1.2" --username "stetsenko.ant1@gmail.com" --password "tpms-dyrp-wfbj-xvay" --asc-provider "com.perceptilabs.app" --file PerceptiLabs-0.1.2-mac.zip
//xcrun altool --notarization-info 4567209d-fc37-4cc7-bee0-a5ceee3ea748 -u "stetsenko.ant1@gmail.com"


// process.env.CSC_LINK = '../perceptilabs.p12'
// process.env.CSC_KEY_PASSWORD = 'com.perceptilabs.app'
// process.env.appleId = 'stetsenko.ant1@gmail.com'
// process.env.appleASP = 'tpms-dyrp-wfbj-xvay'
// module.exports = async (context)=> {
//     const { electronPlatformName } = context;
//     if (electronPlatformName === 'darwin') {
//         try {
//             console.log('Try notarize app');
//             await notarize({
//               appBundleId: 'com.perceptilabs.app',
//               appPath: './build/mac/PerceptiLabs.app',
//               appleId: process.env.appleId,
//               appleIdPassword: process.env.appleASP,
//             });
//             console.log('Success notarize');
//         } catch (err) {
//             console.log('Notarize app', err);
//         }
//   }

// };
async function nota(context) {
    console.log(process.env);
    //const { electronPlatformName } = context;
    if (electronPlatformName === 'darwin') {
        try {
            console.log('Try notarize app');
            await notarize({
              appBundleId: 'com.perceptilabs.app',
              appPath: './build/mac/PerceptiLabs.app',
              appleId: process.env.appleId,
              appleIdPassword: process.env.appleASP,
            });
            console.log('Success notarize');
        } catch (err) {
            console.log('Notarize app', err);
        }
    }
};
nota();