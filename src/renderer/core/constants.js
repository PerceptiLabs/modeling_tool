const trainingElements =  ['TrainNormal', 'TrainNormalData', 'TrainReinforce', 'TrainGenetic', 'TrainDynamic'];
const deepLearnElements = ['DeepLearningFC', 'DeepLearningConv', 'DeepLearningDeconv', 'DeepLearningRecurrent'];

const pathWebWorkers = './static/webworkers';
const pathBasicTemplate = './static/basic-template';
const pathCore = './static/core';
const chartSpinner = {
  text: 'Loading…',
  color: '#6b8ff7',
  textColor: '#fff',
  maskColor: 'transparent'
};

export {trainingElements, deepLearnElements, pathWebWorkers, pathBasicTemplate,pathCore, chartSpinner}
