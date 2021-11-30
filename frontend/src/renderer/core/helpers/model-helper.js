import { getFirstElementFromObject } from "@/core/helpers";
import cloneDeep from "lodash.clonedeep";

export const getDatasetPath = (datasetSettings) => {
  if (datasetSettings.csv_path) {
    return datasetSettings.csv_path;
  } else if (datasetSettings.filePath) {
    return datasetSettings.filePath;
  } else if (datasetSettings.featureSpecs && Object.keys(datasetSettings).length > 0) {
    return getFirstElementFromObject(datasetSettings.featureSpecs).csv_path;
  } else {
    return null;
  }
}

export const formatCSVTypesIntoKernelFormat = (csvData) => {
  const payload = {};
  for (const [idx, val] of csvData.columnNames.entries()) {
    const sanitizedVal = val.replace(/^\n|\n$/g, "");
    payload[sanitizedVal] = {
      iotype: csvData.ioTypes[idx],
      datatype: csvData.dataTypes[idx],
      preprocessing: csvData.preprocessingTypes[idx],
    }
  }
  return payload;
}


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
    network = cloneDeep(network); 
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

export const assembleModel = (name, elementList, rootFolder, meta, snapshots, apiMeta, datasetSettings = null, trainingSettings = null) => {
  /** Constructs a frontend model from its components **/  
  let newNetwork = cloneDeep(defaultNetwork);


  newNetwork.apiMeta = apiMeta;
  newNetwork.networkID = apiMeta.model_id;

  if (rootFolder) {
    newNetwork.networkRootFolder = rootFolder;
  }
  if (name) {
    newNetwork.networkName = name;
  }
  if (snapshots) {
    newNetwork.networkSnapshots = snapshots;
  }
  if (elementList) {
    newNetwork.networkElementList = elementList;
  }
  if (meta) {
    newNetwork.networkMeta = meta;
  }
  if (trainingSettings) {
    newNetwork.networkMeta.trainingSettings = cloneDeep(trainingSettings);
  }
  if (datasetSettings) {
    newNetwork.networkMeta.datasetSettings = cloneDeep(datasetSettings);
  }
  
  createPositionElements(newNetwork.networkElementList); // TODO: is this used?
  return newNetwork;
}

export const assembleModelFromJson = (jsonNet, apiMeta) => {
  /** Constructs a frontend model from whatever is stored in Rygg **/
  return assembleModel(
    jsonNet.networkName,
    jsonNet.networkElementList,
    jsonNet.networkRootFolder,
    jsonNet.networkMeta,
    jsonNet.networkSnapshots,
    apiMeta
  );
}

export const disassembleModel = (inputNetwork) => {
  /** Deconstructs a frontend model to something that can be stored in Rygg **/
  let network = cloneDeep(inputNetwork);  // Defensive copy
  network = removeChartData(network, false);
  
  return {
    apiMeta: network.apiMeta,
    networkName: network.networkName,
    networkID: network.networkID,
    networkMeta: network.networkMeta,
    networkElementList: network.networkElementList,
    networkRootFolder: network.networkRootFolder,
    networkSnapshots: network.networkSnapshots
  }
}



