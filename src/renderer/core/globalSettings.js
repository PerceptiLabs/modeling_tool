const configApp = {
  //version: 'core_cloud', //'python'
  developMode: true,
};

//configApp.version = process.env.BUILD_TARGET === 'core_local' ? 'core_local' : 'core_cloud';

configApp.developMode = process.env.NODE_ENV !== 'production' ? true : false;




export default configApp
