import { DataSet, Network } from "vis-network/standalone";


const createNodes = (modelRecommendation) => {
  if (!modelRecommendation) { return new DataSet(); }

  const dataSetInput = Object.entries(modelRecommendation)
    .map(([k, v]) => {
      return { id: k, label: v.Name }
    });
    
  return new DataSet(dataSetInput);
}

const createEdges = (modelRecommendation) => {
  if (!modelRecommendation) { return new DataSet(); }

  const dataSetInput = Object.entries(modelRecommendation)
    .filter(([k, v]) => v['forward_connections'].length > 0)
    .map(([k, v]) => {
      return v['forward_connections'].map(fc => {
        const from = k;
        const to =  fc['dst_id'];        

        return { id:`edge_${from}_${to}`, from, to }
      });
    })
    .reduce((acc, curr) => acc.concat(curr), []);
  
  return new DataSet(dataSetInput);
}

/**
 * Fetches the default options.
 */
export const getDefaultOptions = () => {

  // Options can be found here:
  // https://visjs.github.io/vis-network/docs/network/#options

  return ({
    layout: {
        randomSeed: undefined,
        improvedLayout:true,
        clusterThreshold: 150,
        hierarchical: {
            enabled:true,
            levelSeparation: 200,
            direction: 'LR',        // UD, DU, LR, RL
            sortMethod: 'directed',  // hubsize, directed
            shakeTowards: 'leaves'  // roots, leaves
        }
    }
  });
}

/**
 * Converts what gets returned from the kernel to a format that vis.js understands
 */
export const convertModelRecommendationToVisNodeEdgeList = (modelRecommendation) => {

  const data = {
    nodes: createNodes(modelRecommendation),
    edges: createEdges(modelRecommendation)
  };
  
  return data;
}

/**
 * Creates a vis.js network.
 * 
 * @param visNodeEdgeList - so the network knows what to place
 */
export const createVisNetwork = (visNodeEdgeList) => {

  // Currently placing all the nodes in an unrendered div.
  // Future work would be to specify the exact size of the network field,
  // instead of the entire view window.

  const networkContainer = document.createElement("div");
  networkContainer.style.height = "100vh";
  networkContainer.style.width = "100vw";
  
  const defaultOptions = Object.assign({}, getDefaultOptions());

  const network  = new Network(
    networkContainer,
    visNodeEdgeList,
    defaultOptions);

  return network;
}

export default {
  getDefaultOptions,
  convertModelRecommendationToVisNodeEdgeList,
  createVisNetwork
}