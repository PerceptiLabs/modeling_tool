import { getFirstElementFromObject, deepCopy, deepCloneNetwork } from "@/core/helpers";

export const defaultNetwork = {  // TODO(anton.k): why doesn't this contain an apiMeta field?
  networkName: 'New_Model',
  networkID: '',
  networkElementList: {},
  networkRootFolder: '',
  networkSnapshots: [],
  networkMeta: {
      openStatistics: null, //null - hide Statistics; false - close Statistics, true - open Statistics
      openTest: null,
      hideModel: false,
      hideStatistics: false,
      hideTest: false,
      zoom: 1,
      zoomSnapshot: 1,
      usingWeights: false,
      netMode: 'edit',//'addArrow'
      coreStatus: {
        Status: 'Waiting' //Created, Training, Validation, Paused, Finished
      },
      chartsRequest: {
        timerID: null,
        waitGlobalEvent: false,
        doRequest: 0,
        showCharts: 0
      }
  }  
};

const findFreePosition = (currentPos, checkingList, indent, widthEl, currentId) => {
  let checkPosition = currentPos;
  checkingPosition();
  
  return checkPosition;
  
  function checkingPosition() {
    return checkingList.forEach((el)=> {
      if(currentId === el.layerId ) return;
      if(
        checkPosition.top > (el.layerMeta.position.top - indent/2)
          && checkPosition.top < (el.layerMeta.position.top + indent/2 + widthEl)
          && checkPosition.left > (el.layerMeta.position.left - indent/2)
          && checkPosition.left < (el.layerMeta.position.left + indent/2 + widthEl)
      ) {
        checkPosition.top = checkPosition.top + indent;
        checkingPosition();
        return
      }
      else return checkPosition
    })
  }
};



const createPositionElements = (list) => {
  if(!list || Object.keys(list).length === 0 || Object.values(list)[0].layerMeta.position.top !== null) {
    return;
  } else {
    let elList = Object.values(list);
    const elGap = 60;
    const widthEl = widthElement;
    const defaultPosition = { top: 0, left: 0 };
    let arrLeft = [];
    let arrTop = [];
    
    elList[0].layerMeta.position = {...defaultPosition};
    elList.forEach((el)=> {
      if(el.layerMeta.position.top === null) {
        el.layerMeta.position = {...defaultPosition};
        
        let newElPosition = this.findFreePosition(el.layerMeta.position, elList, elGap, widthEl, el.layerId);
        arrTop.push(newElPosition.top);
        arrLeft.push(newElPosition.left);
      }
      
      if(el.connectionOut.length) {
        let outLength = el.connectionOut.length;
        el.connectionOut.forEach((elId, i)=> {
          if(list[elId].layerMeta.position.top === null) {
            const top = el.layerMeta.position.top + (elGap - ((outLength / 2) * (elGap + widthEl)) + ((elGap + widthEl) * i));
            const left = el.layerMeta.position.left + elGap + widthEl;
            
            let newPosition = this.findFreePosition({top, left}, elList, elGap, widthEl, list[elId].layerId);
            
            list[elId].layerMeta.position.top = newPosition.top;
            arrTop.push(newPosition.top);
            list[elId].layerMeta.position.left = newPosition.left;
            arrLeft.push(newPosition.left);
          }
        })
      };
    });
    
    const netHeight = (Math.max(...arrTop) - Math.min(...arrTop));
    const netWidth = (Math.max(...arrLeft) - Math.min(...arrLeft));
    const corrTop = (document.body.clientHeight /2) - (netHeight/2);
    const corrLeft = (document.body.clientWidth /2) - (netWidth/2) - 300;
    const correctionTop = corrTop > 0 ? corrTop : elGap;
    const correctionLeft = corrLeft > 0 ? corrLeft : elGap;
    
    elList.forEach((el)=> {
      el.layerMeta.position.top = el.layerMeta.position.top + correctionTop;
      el.layerMeta.position.left = el.layerMeta.position.left + correctionLeft;
    })
  }
}

const removeChartData = (network, copy = true) => {
  if (copy) {
    network = deepCopy(network); 
  }
  
  network = cleanNetworkElementListChartData(network);
  network = cleanNetworkSnapshotsChartData(network);
  if (network.networkMeta && network.networkMeta.chartsRequest)
    network.networkMeta.chartsRequest.timerID = null;
  if (network.networkMeta.coreStatus) {
    delete(network.networkMeta.coreStatus);
  }
  return network;


  function cleanNetworkElementListChartData(net) {
    if (!net || !net['networkElementList']) { return net; }

    for (const key of Object.keys(net['networkElementList'])) {
      const layerObject = net['networkElementList'][key];
      if (!layerObject.hasOwnProperty('chartData')) { continue; }
  
      layerObject['chartData'] = {};
      layerObject['chartDataIsLoading'] = 0;
    }
    return net
  }

  function cleanNetworkSnapshotsChartData(net) {
    if (!net || !net['networkSnapshots']) { return net; }
    
    const networkHaveSnapshots = net.networkSnapshots && net.networkSnapshots.length > 0;

    if(networkHaveSnapshots) {
      for (const key of Object.keys(net['networkSnapshots'][0])) {
        const layerObject = net['networkSnapshots'][0][key];
        if (!layerObject.hasOwnProperty('chartData')) { continue; }
    
        layerObject['chartData'] = {};
      }
    }
   
    return net
  }
}

function makeNetworkElementList(graphSettings, frontendSettings) {
  let elements = {}
  
  for (const key of Object.keys(frontendSettings.layerMeta)) {
    elements[key] = deepCopy(frontendSettings.layerMeta[key]);

    elements[key]['layerName'] = graphSettings[key]['Name']
    elements[key]['componentName'] = graphSettings[key]['Type']
    elements[key]['layerSettings'] = graphSettings[key]['Properties']
    elements[key]['layerCode'] = graphSettings[key]['Code']
    elements[key]['backward_connections'] = graphSettings[key]['backward_connections']
    elements[key]['forward_connections'] = graphSettings[key]['forward_connections']
    elements[key]['visited'] = graphSettings[key]['visited']
    elements[key]['previewVariable'] = graphSettings[key]['previewVariable']
  }
  return deepCloneNetwork(elements)
}

function makeGraphSettings(elements) {
  let layers = {}

  for(let layer in elements) {
    const el = elements[layer];

    layers[el.layerId] = {
      Name: el.layerName,
      Type: el.componentName,
      Properties: el.layerSettings,
      Code: el.layerCode,
      backward_connections: el.backward_connections,
      forward_connections: el.forward_connections,
      visited: el.visited,
      previewVariable: el.previewVariable
    };
  }    
  return layers
}

function makeLayerMeta(elements) {
  let layerMeta = {}
    
  for(let layer in elements) {
    const el = deepCopy(elements[layer]);

    delete el['layerName']
    delete el['componentName'],
    delete el['layerSettings'],
    delete el['layerCode'],
    delete el['backward_connections'],
    delete el['forward_connections'],
    delete el['visited'],
    delete el['previewVariable']
    
    layerMeta[layer] = el;
  }
  return layerMeta;
}

export const assembleModel = (datasetSettings, trainingSettings, graphSettings, frontendSettings) => {
  /** Constructs a frontend model from its components **/  
  let newNetwork = deepCopy(defaultNetwork);
  
  newNetwork.apiMeta = deepCopy(frontendSettings.apiMeta);
  newNetwork.networkID = frontendSettings.apiMeta.model_id;
  newNetwork.networkName = frontendSettings.networkName;
  newNetwork.networkElementList = makeNetworkElementList(graphSettings, frontendSettings);

  if (frontendSettings.networkMeta) {
    newNetwork.networkMeta = deepCopy(frontendSettings.networkMeta);
  }

  if (frontendSettings.networkRootFolder) {
    newNetwork.networkRootFolder = frontendSettings.networkRootFolder;
  }
  
  newNetwork.networkMeta.trainingSettings = deepCopy(trainingSettings);
  newNetwork.networkMeta.datasetSettings = deepCopy(datasetSettings);
  
  createPositionElements(newNetwork.networkElementList); // TODO: is this used?

  return newNetwork;
}

export const disassembleModel = (inputNetwork) => {
  /** Deconstructs a frontend model to something that can be stored in Rygg **/
  let network = deepCloneNetwork(inputNetwork);  
  network = removeChartData(network, false);

  
  const parts = {
    datasetSettings: deepCopy(network.networkMeta.datasetSettings),
    trainingSettings: deepCopy(network.networkMeta.trainingSettings),
    graphSettings: makeGraphSettings(network.networkElementList),    
    frontendSettings: { 
      apiMeta: deepCopy(network.apiMeta),
      networkName: network.networkName,
      networkMeta: deepCopy(network.networkMeta),      
      networkRootFolder: deepCopy(network.networkRootFolder),      
      layerMeta: makeLayerMeta(network.networkElementList)
    }
  };

  delete parts.frontendSettings.networkMeta.datasetSettings;
  delete parts.frontendSettings.networkMeta.trainingSettings;  
  
  return parts;
}



