const isDevelopMode = process.env.NODE_ENV !== 'production';

const trainingElements  = ['TrainLoss', 'TrainOptimizer', 'TrainNormal', 'TrainRegression', 'TrainReinforce', 'TrainGan', 'TrainDetector'
  //'TrainGenetic',
  //'TrainDynamic'
];
const deepLearnElements = ['DeepLearningFC', 'DeepLearningConv', 'DeepLearningDeconv', 'DeepLearningRecurrent'];

const pathWebWorkers = './static/webworkers';

const baseUrlCloud  = 'https://perceptilabsamerica.azurewebsites.net/api/';
// const baseUrlCloud  = 'http://perceptilabs.trafficmanager.net/api/';
const baseUrlSite   = 'https://perceptilabs-website-dev.azurewebsites.net';

const widthElement = 60;
const workspaceGrid = 10;
export const shadowBoxDragIfMoreThenElementsSelected = 3;
const pathSlash = process.platform === 'win32' ? '\\' : '/';

const hideSidebarOnBreakpoint = 1280;
const sidebarNavCoefficientScaleCalculateFromHeight = 920;
const filePickerStorageKey = 'filePickerPathSource';
const localStorageGridKey = 'isGridEnabled';

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
