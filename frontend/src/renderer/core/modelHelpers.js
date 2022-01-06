import store from "@/store";
import { deepCloneNetwork } from "@/core/helpers";

export const connectComponentsWithArrow = (
  previousElementId,
  currentElementId,
) => {
  if (!previousElementId || !currentElementId) {
    return;
  }
  const previousElement = store.getters["mod_workspace/GET_networkElementById"](
    previousElementId,
  );
  const outputs = previousElement.outputs;
  const outputKey = Object.keys(outputs)[0];

  const currentElement = store.getters["mod_workspace/GET_networkElementById"](
    currentElementId,
  );

  const inputs = currentElement.inputs;
  let inputKey = null;
  Object.keys(inputs).map(key => {
    if (inputs[key].isDefault) {
      inputKey = key;
    }
  });

  if (!!inputKey && !!outputKey) {
    store.commit("mod_workspace/SET_startArrowID", {
      outputDotId: outputKey,
      outputLayerId: previousElement.layerId,
      layerId: previousElement.layerId,
    });
    store
      .dispatch("mod_workspace/ADD_arrow", {
        inputDotId: inputKey,
        inputLayerId: currentElement.layerId,
        layerId: currentElement.layerId,
      })
      .then(() => {
        store.dispatch(
          "mod_api/API_getBatchPreviewSampleForElementDescendants",
          currentElement.layerId,
        );
      });
  }
};

const testsValidationRules = {
  confusion_matrix: {
    inputs: ["numerical", "image", "categorical"],
    outputs: ["categorical"],
  },
  classification_metrics: {
    inputs: ["numerical", "image", "categorical"],
    outputs: ["categorical"],
  },
  segmentation_metrics: {
    inputs: ["image"],
    outputs: ["mask"],
  },
  outputs_visualization: {
    inputs: ["image"],
    outputs: ["mask"],
  },
};

export const isModelValidForTest = (model, testType) => {
  if (!Object.keys(testsValidationRules).includes(testType)) {
    throw new Error(`Test type: ${testType} is not valid`);
  }
  let networkList = [...Object.values(model.networkElementList)];

  const modelInputTypes = [
    ...networkList
      .filter(x => x.layerType === "IoInput")
      .map(x => x.layerSettings.DataType),
  ];
  const modelOutputTypes = [
    ...networkList
      .filter(x => x.layerType === "IoOutput")
      .map(x => x.layerSettings.DataType),
  ];

  let isInputsValid = modelInputTypes.some(x =>
    testsValidationRules[testType]["inputs"].includes(x),
  );
  let isOutputsValid = modelOutputTypes.some(x =>
    testsValidationRules[testType]["outputs"].includes(x),
  );

  return isInputsValid && isOutputsValid;
};

export const getModelDatasetPath = model => {
  return (
    model &&
    model.networkMeta &&
    Object.values(model.networkMeta.datasetSettings.featureSpecs)[0].csv_path
  );
};

export const isModelTrained = model => {
  const {
    networkMeta: { coreStatus: { Status: networkStatus } = {} },
  } = model;
  if (!networkStatus) {
    return false;
  }
  return (
    networkStatus === "Finished" ||
    networkStatus === "Testing" ||
    networkStatus === "Validation" ||
    networkStatus === "Stopped" ||
    model.networkMeta.coreStatus.Epoch > 0
  );
};

export const getForwardAndBackwardConnections = fullNetworkElementList => {
  let connections = {};
  let inputs = {};
  let outputs = {};
  let inputIds = [];
  let outputIds = [];

  Object.keys(fullNetworkElementList).map(networkId => {
    const el = fullNetworkElementList[networkId];
    inputs = {
      ...inputs,
      ...el.inputs,
    };
    outputs = {
      ...outputs,
      ...el.outputs,
    };
  });

  inputIds = Object.keys(inputs).map(key => key);
  outputIds = Object.keys(outputs).map(key => key);

  Object.keys(fullNetworkElementList).map(networkId => {
    connections[networkId] = {
      forward_connections: [],
      backward_connections: [],
    };
  });

  Object.keys(fullNetworkElementList).map(networkId => {
    const el = fullNetworkElementList[networkId];
    const elInputs = el.inputs;

    if (!el.inputs) {
      return;
    }

    Object.keys(elInputs).map(inputId => {
      let input = elInputs[inputId];
      if (input.reference_var_id !== null) {
        if (outputIds.indexOf(input.reference_var_id) !== -1) {
          // output of reference element
          let forward_connections_obj = {
            src_var: outputs[input.reference_var_id].name,
            dst_id: networkId,
            dst_var: input.name,
          };
          // input
          let backward_connections_obj = {
            src_id: input.reference_layer_id,
            src_var: outputs[input.reference_var_id].name,
            dst_var: input.name,
          };
          connections[networkId].backward_connections.push(
            backward_connections_obj,
          );
          connections[input.reference_layer_id].forward_connections.push(
            forward_connections_obj,
          );
        }
      }
    });
  });
  return connections;
};
export const attachForwardAndBackwardConnectionsToNetwork = function(net) {
  let ret = deepCloneNetwork(net);
  const payload = getForwardAndBackwardConnections(deepCloneNetwork(net));

  Object.keys(ret).map(key => {
    const elId = key;
    ret[elId].forward_connections = payload[elId].forward_connections;
    ret[elId].backward_connections = payload[elId].backward_connections;
  });
  return ret;
};
