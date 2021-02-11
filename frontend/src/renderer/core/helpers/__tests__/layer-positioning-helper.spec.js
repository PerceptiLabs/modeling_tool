import { DataSet, Network } from "vis-network/standalone";

import { convertModelRecommendationToVisNodeEdgeList } from '../layer-positioning-helper.js';

global.window.crypto = {
  getRandomValues: jest.fn()
    .mockImplementation(require("polyfill-crypto.getrandomvalues"))
    .mockName("getRandomValuesPolyfill"),
};

const inputData = {
  "0": {
    "Name": "_IoInput_0",
    "Type": "IoInput",
    "Code": null,
    "visited": false,
    "previewVariable": "",
    "getPreview": false,
    "endPoints": [],
    "checkpoint": {
      "path": null,
      "load_checkpoint": true
    },
    "backward_connections": [],
    "forward_connections": [
      {
        "dst_id": "1",
        "dst_var": "input",
        "src_var": "output"
      }
    ],
    "Properties": {
      "FeatureName": "input_column",
      "FilePath": "/Users/davidh/Documents/datasets/csv/data.csv"
    }
  },
  "1": {
    "Name": "_DeepLearningFC_1",
    "Type": "DeepLearningFC",
    "Code": null,
    "visited": false,
    "previewVariable": "",
    "getPreview": false,
    "endPoints": [],
    "checkpoint": {
      "path": null,
      "load_checkpoint": true
    },
    "backward_connections": [
      {
        "src_id": "0",
        "src_var": "output",
        "dst_var": "input"
      }
    ],
    "forward_connections": [
      {
        "dst_id": "2",
        "dst_var": "input",
        "src_var": "output"
      }
    ],
    "Properties": {
      "Dropout": false,
      "Keep_prob": 0,
      "Neurons": 1,
      "Activation_function": "None",
      "Batch_norm": false
    }
  },
  "2": {
    "Name": "_IoOutput_2",
    "Type": "IoOutput",
    "Code": null,
    "visited": false,
    "previewVariable": "",
    "getPreview": false,
    "endPoints": [],
    "checkpoint": {
      "path": null,
      "load_checkpoint": true
    },
    "backward_connections": [
      {
        "src_id": "1",
        "src_var": "output",
        "dst_var": "input"
      }
    ],
    "forward_connections": [],
    "Properties": {
      "FeatureName": "output_column\n",
      "FilePath": "/Users/davidh/Documents/datasets/csv/data.csv"
    }
  }
}

describe('convertModelRecommendationToVisNodeEdgeList should', () => {

  test('returns truthy on no input', async() => {
    const actual = convertModelRecommendationToVisNodeEdgeList(null);

    expect(actual).not.toBeFalsy();
  });

  test('returns truthy on valid input', async() => {
    const input = {
      "0": {
        "Name": "_IoInput_0",
        "Type": "IoInput",
        "Code": null,
        "visited": false,
        "previewVariable": "",
        "getPreview": false,
        "endPoints": [],
        "checkpoint": {
          "path": null,
          "load_checkpoint": true
        },
        "backward_connections": [],
        "forward_connections": [],
        "Properties": {
          "FeatureName": "input_column",
          "FilePath": "filepath1"
        }
      }
    }
    const actual = convertModelRecommendationToVisNodeEdgeList(input);

    expect(actual).not.toBeFalsy();
  });

  test('returns single node on valid input', async() => {

    const actual = convertModelRecommendationToVisNodeEdgeList({"0": inputData["0"]});

    const expected = new DataSet([
      { id: '0', label: '_IoInput_0' },
    ]);

    expect(actual.nodes.getIds()).toEqual(expected.getIds());
  });

  test('returns multi nodes on valid input', async() => {
    
    const actual = convertModelRecommendationToVisNodeEdgeList(inputData);

    const expected = new DataSet([
      { id: '0', label: '_IoInput_0' },
      { id: '1', label: '_DeepLearningFC_1' },
      { id: '2', label: '_IoOutput_2' }
    ]);

    expect(actual.nodes.getIds()).toEqual(expected.getIds());
  });

  test('returns edges on valid input', async() => {

    const actual = convertModelRecommendationToVisNodeEdgeList(inputData);

    const expected = new DataSet([
      { id:`edge_0_1`, from: '0', to: '1' },
      { id:`edge_1_2`, from: '1', to: '2' }
    ]);

    expect(actual.edges.getIds()).toEqual(expected.getIds());
  });
});

