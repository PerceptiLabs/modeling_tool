const isDevelopMode = process.env.NODE_ENV !== 'production';

const trainingElements  = ['TrainNormal', 'TrainRegression', 'TrainReinforce', 'TrainGan', 'TrainDetector'
  //'TrainGenetic',
  //'TrainDynamic',
  //'TrainLoss', 
  //'TrainOptimizer', 
];
const deepLearnElements = ['DeepLearningFC', 'DeepLearningConv', 'DeepLearningDeconv', 'DeepLearningRecurrent'];

const pathWebWorkers = './static/webworkers';

// const baseUrlCloud  = 'http://perceptilabs.trafficmanager.net/api/';
const baseUrlCloud  = 'https://perceptilabsamerica.azurewebsites.net/api/';
// const baseUrlCloud  = 'http://localhost:8000/';
// const baseUrlSite   = 'https://perceptilabs-website-dev.azurewebsites.net';
const baseUrlSite   = 'https://perceptilabs.com';

export const FILE_SERVER_BASE_URL = 'http://localhost:8011'

export const GITHUB_AYTHORIZE_URL = `https://github.com/login/oauth/authorize?scope=public_repo,read:user&client_id=${process.env.GITHUB_CLIENT_ID}`;
export const GITHUB_GET_TOKEN_BY_CODE_URL = 'https://ghsk.azurewebsites.net'

const widthElement = 60;
const workspaceGrid = 20;
export const shadowBoxDragIfMoreThenElementsSelected = 3;
const pathSlash = process.platform === 'win32' ? '\\' : '/';

const hideSidebarOnBreakpoint = 1280;
const sidebarNavCoefficientScaleCalculateFromHeight = 920;
const filePickerStorageKey = 'filePickerPathSource';
const localStorageGridKey = 'isGridEnabled';

export const MODAL_PAGE_PROJECT = 'MODAL_PAGE_PROJECT';
export const MODAL_PAGE_SIGN_IN = 'MODAL_PAGE_SIGN_IN';
export const MODAL_PAGE_SIGN_UP = 'MODAL_PAGE_SIGN_UP';
export const MODAL_PAGE_WHATS_NEW = 'MODAL_PAGE_WHATS_NEW';
export const MODAL_PAGE_RESTORE_ACCOUNT = 'MODAL_PAGE_RESTORE_ACCOUNT';
export const MODAL_PAGE_CREATE_MODEL = 'MODAL_PAGE_CREATE_MODEL';

export const PROJECT_DEFAULT_FOLDER = '/Users/antonbourosu/proj/'


export const TRACKER_SCREENNAME_PROJECTS = 'Projects';
export const TRACKER_SCREENNAME_WORKSPACE = 'Workspace';
export const TRACKER_SCREENNAME_WORKSPACE_TRAINING = 'Workspace-Training';
export const TRACKER_SCREENNAME_STATISTICS = 'Statistics';
export const TRACKER_SCREENNAME_STATISTICS_TRAINING = 'Statistics-Training';
export const TRACKER_SCREENNAME_TEST = 'Test';
export const TRACKER_SCREENNAME_TEST_TRAINING = 'Test-Training';

export const LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY  = 'mod_workspace_view_type'
export const LOCAL_STORAGE_WORKSPACE_SHOW_MODEL_PREVIEWS  = 'show_model_previews'

export {
  isDevelopMode,
  trainingElements,
  deepLearnElements,
  pathWebWorkers,
  widthElement,
  workspaceGrid,
  baseUrlCloud,
  baseUrlSite,
  pathSlash,
  hideSidebarOnBreakpoint,
  sidebarNavCoefficientScaleCalculateFromHeight,
  filePickerStorageKey,
  localStorageGridKey,
}
