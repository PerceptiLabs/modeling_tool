import { sleep, calcLayerPosition }      from "@/core/helpers.js";
import cloneDeep      from 'lodash.clonedeep';

import IoInputSetting   from '@/components/network-elements/elements/io-input/set-io-input.vue';

const DEFAULT_LAYER_TEMPLATE = {
  layerId: null,
  copyId: null,
  copyContainerElement: null,
  layerName: null,
  layerType: null,
  layerSettings: null,
  layerSettingsTabName: null,
  layerCode: null,
  layerCodeError: null,
  layerNone: false,
  layerMeta: {
    isInvisible: false,
    isLock: false,
    isSelected: false,
    position: {
      top: 0,
      left: 0,
    },
    tutorialId: '',
    OutputDim: '',
    InputDim: '',
    layerContainerName: '',
    layerBgColor: '',
    containerDiff: {
      top: 0,
      left: 0,
    }
  },
  chartData: {},
  checkpoint: [],
  endPoints: [],
  componentName: '',
  connectionOut: [],
  connectionIn: [],
  connectionArrow: [],
  visited: false,
  inputs: [],
  outputs: [],
  forward_connections: [],
  backward_connections: [],
  previewVariable: 'output',
  previewVariableList: [],
  isTrained: false,
  isSettingsLocked: false,
};


const getDefaultLayerTemplate = ({ 
  layerId = null,
  layerName = null,
  layerType = null,
  layerSettings = null,
  layerSettingsTabName = null,
  layerCode = null,
  positionTop = 0,
  positionLeft = 0,
  componentName = ''
  }) => {

  const layer = cloneDeep(DEFAULT_LAYER_TEMPLATE);

  layer.layerId = layerId;
  layer.layerName = layerName;
  layer.layerType = layerType;
  layer.layerSettings = layerSettings,
  layer.layerSettingsTabName = layerSettingsTabName,
  layer.layerCode = layerCode,
  layer.layerMeta.position.top = positionTop,
  layer.layerMeta.position.left = positionLeft,
  
  layer.componentName = componentName;

  layer.inputs = setupInput(componentName);
  layer.outputs = setupOutput(componentName);

  return layer;
};

const componentsInputs = {
  DataData: [],
  DataEnvironment: [],
  DataRandom: [],

  ProcessReshape: ['input'],
  ProcessGrayscale: ['input'],
  ProcessOneHot: ['input'],
  ProcessRescale: ['input'],

  DeepLearningFC: ['input'],
  DeepLearningConv: ['input'],
  DeepLearningDeconv: ['input'],
  DeepLearningRecurrent: ['input'],

  MathArgmax: ['input'],
  MathMerge: ['input1', 'input2'],
  MathSwitch: ['input1', 'input2'],

  TrainNormal: ['predictions', 'labels'],
  TrainRegression: ['predictions', 'labels'],
  TrainReinforce: ['action'],
  TrainGan: ['input'],
  TrainDetector: ['predictions', 'labels'],
  LayerCustom: ['input'],

  IoInput: [],
  IoOutput: ['input']
};

const componentsOutputs = {
  DataData: ['output'],
  DataEnvironment: ['output'],
  DataRandom: ['output'],

  ProcessReshape: ['output'],
  ProcessGrayscale: ['output'],
  ProcessOneHot: ['output'],
  ProcessRescale: ['output'],

  DeepLearningFC: ['output'],
  DeepLearningConv: ['output'],
  DeepLearningDeconv: ['output'],
  DeepLearningRecurrent: ['output'],

  MathArgmax: ['output'],
  MathMerge: ['output'],
  MathSwitch: ['output'],
  LayerCustom: ['output'],

  TrainNormal: [],
  TrainRegression: [],
  TrainReinforce: [],
  TrainGan: [],
  TrainDetector: [],

  IoInput: ['output'],
  IoOutput: []
};

const setupInput = (componentName) => {
  let inputs = {};
  const inputVariableArray = componentsInputs[componentName];
  if(inputVariableArray && inputVariableArray.length > 0) {
    inputVariableArray.map((inputName, index) => {
      let input = {
        name: inputName,
        reference_var_id: null,
        reference_layer_id: null,
        isDefault: true
      }
      inputs[Date.now().toString() + index] = input;
    })
  }
  return inputs;

}

const setupOutput = (componentName) => {
  let outputs = {};
  const outputVariableArray = componentsOutputs[componentName];
  if(outputVariableArray && outputVariableArray.length > 0) {
    outputVariableArray.map((outputName, index) => {
      let output = {
        name: outputName,
        reference_var: outputName,
      }
      outputs[[Date.now().toString() + index]] = output;
    })
  }
  return outputs;
}
const getMaxLeftPadding = (layerPositions) => {
  let maxLeftPadding = 0;
  Object.values(layerPositions).map(l => {
    if(l.x < maxLeftPadding) {
      maxLeftPadding = l.x
    }
  })
  return  Math.abs(maxLeftPadding)
}

const createLayers = async (coreNetwork, layerPositions) => {
  const newLayers = {};

  const maxLeftPadding = getMaxLeftPadding(layerPositions);
  
  // creating the layers
  for (const [k, v] of Object.entries(coreNetwork)) {
    const creationOptions = {
      layerId: k,
      layerName: v['Name'],
      layerType: v['Type'],
      componentName: v['Type'],
      layerSettings: v['Type'].startsWith('Io') ?  IoInputSetting.data().settings : null
    }
    if (layerPositions && layerPositions[k]) {
      creationOptions['positionTop'] = calcLayerPosition(layerPositions[k]['y'] + 60);
      creationOptions['positionLeft'] = calcLayerPosition(layerPositions[k]['x'] + 60 + maxLeftPadding);
    }

    const newLayer = getDefaultLayerTemplate(creationOptions);
    newLayers[k] = newLayer;

    // need new layerId
    await sleep(1);
  }

  return newLayers;
}

const setupSettings = (coreNetwork, layers) => {

  const newLayers = cloneDeep(layers);

  // Setting up the connections
  for (const [k, v] of Object.entries(coreNetwork)) {

    if (!newLayers[k]) { continue; }

    newLayers[k]['layerSettings'] = {
      ...newLayers[k]['layerSettings'],
      ...v['Properties']};
  }

  return newLayers;
}

const setupConnections = (coreNetwork, layers) => {

  const newLayers = cloneDeep(layers);

  // Makes the bottom search O(n^2) instead of O(n^3)
  const varIdMap = new Map();
  for (const [k, v] of Object.entries(layers)) {

    for (const [inputK, inputV] of Object.entries(v['inputs'])) {
      const mapKey = `${k}_inputs_${inputV['name']}`;
      varIdMap.set(mapKey, inputK);
    }

    for (const [outputK, outputV] of Object.entries(v['outputs'])) {
      const mapKey = `${k}_outputs_${outputV['name']}`;
      varIdMap.set(mapKey, outputK);
    }
  }


  // Setting up the connections
  for (const [k, v] of Object.entries(coreNetwork)) {

    // Example of input:
    //  forward_connections: Array(1)
    //    0: {dst_id: "2", dst_var: "input", src_var: "output"}

    for (const { dst_id, dst_var, src_var } of v['forward_connections']) {

      const targetInputs = newLayers[dst_id]['inputs'];
      const targetInput = Object.entries(targetInputs).find(([k,v]) => v['name'] == dst_var);

      if (!targetInput) { continue; }

      targetInput[1]['reference_layer_id'] = k;
      targetInput[1]['reference_var_id'] = varIdMap.get(`${k}_outputs_${src_var}`);
    }
  }

  return newLayers;
}

/**
 * This function creates layers and returns them ready for use in a network
 * @param coreNetwork - data structurs in accordance to the core model returned by the kernel
 * @param layerPositions - comes from the vis.js library (used in layer-positioning-helper.js)
 */
export const buildLayers = async (coreNetwork, layerPositions) => {

  let layers;

  layers = await createLayers(coreNetwork, layerPositions);
  layers = await setupSettings(coreNetwork, layers);
  layers = await setupConnections(coreNetwork, layers);
  
  return layers;
}

export default {
  buildLayers
}

