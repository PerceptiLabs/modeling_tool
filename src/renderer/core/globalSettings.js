const configApp = {
  developMode: true,
  workspaceGrid: 10
};

//configApp.version = process.env.BUILD_TARGET === 'core_local' ? 'core_local' : 'core_cloud';

configApp.developMode = process.env.NODE_ENV !== 'production' ? true : false;




export default configApp
