const isDevelopMode = process.env.NODE_ENV !== 'production' ? true : false;

const trainingElements  = ['TrainNormal', 'TrainReinforce', 'TrainGenetic', 'TrainDynamic'];
const deepLearnElements = ['DeepLearningFC', 'DeepLearningConv', 'DeepLearningDeconv', 'DeepLearningRecurrent'];

const pathWebWorkers = './static/webworkers';

const baseUrlCloud  = 'https://perceptilabs-dev.azurewebsites.net/api/';
const baseUrlSite   = 'https://perceptilabs-website-dev.azurewebsites.net';

const widthElement = 60;
const workspaceGrid = 10;

export {
  isDevelopMode,
  trainingElements,
  deepLearnElements,
  pathWebWorkers,
  widthElement,
  workspaceGrid,
  baseUrlCloud,
  baseUrlSite
}
