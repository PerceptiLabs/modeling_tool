const configApp = {
  version: 'core_cloud', //'python'
  developMode: true,
};

//console.log(process.env);
Object.freeze(process);
console.log(process.env);
console.log(process.env.NODE_ENV);

configApp.version = process.env.BUILD_TARGET === 'core_local' ? 'core_local' : 'core_cloud';

configApp.developMode = process.env.NODE_ENV !== 'production' ? true : false;


//console.log(process.env.BUILD_TARGET);


export default configApp
