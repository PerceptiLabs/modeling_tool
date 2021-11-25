import { sleep, calcLayerPosition }      from "@/core/helpers.js";
import { v4 as uuid} from 'uuid';
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

  return layer;
};


const setUpInputsAndOutputs = (layers) => {
  const InputOutputData = {};
    
    Object.keys(layers).map((key) => {
        InputOutputData[key] = {
            inputs: [],
            outputs: [],
        };
    });

    const res = {};
    for(let [k, v] of Object.entries(layers)) {
        const theKey = k;
        const backward_connections = v.backward_connections;
        backward_connections.forEach(f => {
          InputOutputData[f.src_id].outputs.push(f.src_var);
          InputOutputData[theKey].inputs.push(f.dst_var);
        })
    }
    
    for(let [k, v] of Object.entries(InputOutputData)) {
        res[k] = {};
        res[k].inputs = setupInput(v.inputs);
        res[k].outputs = setupOutput(v.outputs);
    }

  return res;
}

const setupInput = (inputVariableArray) => {
  let inputs = {};
  if(inputVariableArray && inputVariableArray.length > 0) {
    inputVariableArray.map((inputName) => {
      let input = {
        name: inputName,
        reference_var_id: null,
        reference_layer_id: null,
        isDefault: true
      }
      inputs[uuid()] = input;
    })
  }
  return inputs;
}

const setupOutput = (outputVariableArray) => {
  let outputs = {};
  if(outputVariableArray && outputVariableArray.length > 0) {
    outputVariableArray.map((outputName) => {
      let output = {
        name: outputName,
        reference_var: outputName,
      }
      outputs[uuid()] = output;
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
  const IO = setUpInputsAndOutputs(coreNetwork);

  for(let [k, v] of Object.entries(newLayers)) {
    newLayers[k].inputs = IO[k].inputs;
    newLayers[k].outputs = IO[k].outputs;
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

    newLayers[k].forward_connections = v['forward_connections'];
    newLayers[k].backward_connections = v['backward_connections'];    
    
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

