import store from '@/store';
import {deepCloneNetwork} from "@/core/helpers";


export const connectComponentsWithArrow = (previousElementId, currentElementId) => {
  if(!previousElementId || !currentElementId) { 
    return;
  }
  const previousElement = store.getters['mod_workspace/GET_networkElementById'](previousElementId);
  const outputs = previousElement.outputs;
  const outputKey = Object.keys(outputs)[0];
  
  const currentElement = store.getters['mod_workspace/GET_networkElementById'](currentElementId);

  const inputs = currentElement.inputs;
  let inputKey = null;
  Object.keys(inputs).map(key => {
    if(inputs[key].isDefault) {
      inputKey = key;
    }
  })

  if(!!inputKey && !!outputKey) {
    store.commit('mod_workspace/SET_startArrowID', {
    outputDotId: outputKey,
    outputLayerId: previousElement.layerId,
    layerId: previousElement.layerId,
    });
    store.dispatch('mod_workspace/ADD_arrow', {
      inputDotId: inputKey,
      inputLayerId: currentElement.layerId,
      layerId: currentElement.layerId,
    }).then(() => {
      store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', currentElement.layerId);
    });
  }
}



const testsValidationRules = {
  'confusion_matrix': {
    'inputs': ['numerical', 'image', 'categorical'],
    'outputs': ['categorical'],
  },
  'classification_metrics': {
    'inputs': ['numerical', 'image', 'categorical'],
    'outputs': ['categorical'],
  },
  'segmentation_metrics': {
    'inputs': ['image'],
    'outputs': ['image'],
  },
  'outputs_visualization': {
    'inputs': ['image'],
    'outputs': ['image'],
  }
};

export const isModelValidForTest = (model, testType) => {
  if(!Object.keys(testsValidationRules).includes(testType)) {
    throw new Error(`Test type: ${testType} is not valid`)
  }
  let networkList = [...Object.values(model.networkElementList)];
  
  const modelInputTypes = [...networkList.filter(x => x.layerType === 'IoInput').map(x => x.layerSettings.DataType)];
  const modelOutputTypes = [...networkList.filter(x => x.layerType === 'IoOutput').map(x => x.layerSettings.DataType)];

  let isInputsValid = modelInputTypes.some(x => testsValidationRules[testType]['inputs'].includes(x));
  let isOutputsValid = modelOutputTypes.some(x => testsValidationRules[testType]['outputs'].includes(x)); 

  return isInputsValid && isOutputsValid
}

export const isModelTrained = (model) => {
  const networkStatus = model.networkMeta.coreStatus.Status;
  return networkStatus === 'Finished' || networkStatus === 'Testing' || networkStatus === 'Validation' || networkStatus === 'Stopped' || model.networkMeta.coreStatus.Epoch > 0;
}