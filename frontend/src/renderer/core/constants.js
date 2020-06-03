const isDevelopMode = process.env.NODE_ENV !== 'production';

const trainingElements  = ['TrainLoss', 'TrainOptimizer', 'TrainNormal', 'TrainRegression', 'TrainReinforce', 'TrainGan', 'TrainDetector'
  //'TrainGenetic',
  //'TrainDynamic'
];
const deepLearnElements = ['DeepLearningFC', 'DeepLearningConv', 'DeepLearningDeconv', 'DeepLearningRecurrent'];

const pathWebWorkers = './static/webworkers';

// const baseUrlCloud  = 'http://perceptilabs.trafficmanager.net/api/';
const baseUrlCloud  = 'https://perceptilabsamerica.azurewebsites.net/api/';
// const baseUrlCloud  = 'http://localhost:8000/';
// const baseUrlSite   = 'https://perceptilabs-website-dev.azurewebsites.net';
const baseUrlSite   = 'https://perceptilabs.com';

const widthElement = 60;
const workspaceGrid = 10;
export const shadowBoxDragIfMoreThenElementsSelected = 3;
const pathSlash = process.platform === 'win32' ? '\\' : '/';

const hideSidebarOnBreakpoint = 1280;
const sidebarNavCoefficientScaleCalculateFromHeight = 920;
const filePickerStorageKey = 'filePickerPathSource';
const localStorageGridKey = 'isGridEnabled';

export const MODAL_PAGE_PROJECT = 'MODAL_PAGE_PROJECT';
export const MODAL_PAGE_SIGN_IN = 'MODAL_PAGE_SIGN_IN';
export const MODAL_PAGE_SIGN_UP = 'MODAL_PAGE_SIGN_UP';
export const MODAL_PAGE_RESTORE_ACCOUNT = 'MODAL_PAGE_RESTORE_ACCOUNT';
export const MODAL_PAGE_CREATE_MODEL = 'MODAL_PAGE_CREATE_MODEL';

export const PROJECT_DEFAULT_FOLDER = '/Users/antonbourosu/proj/'

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
