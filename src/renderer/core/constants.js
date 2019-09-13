const isDevelopMode = process.env.NODE_ENV !== 'production';
const isDebugMode = !!process.env.IS_DEBUG_MODE;

const trainingElements  = ['TrainNormal', 'TrainReinforce', 'TrainGenetic', 'TrainDynamic'];
const deepLearnElements = ['DeepLearningFC', 'DeepLearningConv', 'DeepLearningDeconv', 'DeepLearningRecurrent'];

const pathWebWorkers = './static/webworkers';

const baseUrlCloud  = 'https://perceptilabsdev.azurewebsites.net/api/';
const baseUrlSite   = 'https://perceptilabs-website-dev.azurewebsites.net';

const widthElement = 60;
const workspaceGrid = 10;

export {
  isDevelopMode,
  isDebugMode,
  trainingElements,
  deepLearnElements,
  pathWebWorkers,
  widthElement,
  workspaceGrid,
  baseUrlCloud,
  baseUrlSite
}
