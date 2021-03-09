import store from '@/store';


export const connectComponentsWithArrow = (previousElemntId, currentElementId) => {
  if(!previousElemntId || !currentElementId) { 
    return;
  }
  const previousElement = store.getters['mod_workspace/GET_networkElementById'](previousElemntId);
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