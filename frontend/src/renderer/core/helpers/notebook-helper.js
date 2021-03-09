import { promiseWithTimeout } from '@/core/helpers';

let store;
let coreNetwork;
let currentNetwork;


const notebookJsonBuilderV4 = (function (networkCode) {
  let publicMethods = {};
  let currentNotebook;

  const initNotebook = function () {
    currentNotebook = JSON.parse(JSON.stringify({
      "cells": [],
      "metadata": {
        "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
        },
        "language_info": {
        "codemirror_mode": {
          "name": "ipython",
          "version": 3
        },
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.6.2"
        }
      },
      "nbformat": 4,
      "nbformat_minor": 4
    }));
  }

  const addCodeCells = function (networkCode) {
    if (!networkCode || networkCode.length == 0) { return; }

    const tempCells = networkCode.map(nc => {      
      return ({
        "cell_type": "code",
        "execution_count": null,
        "metadata": {},
        "outputs": [],
        "source": nc.split(/\r?\n/).map(code => code + '\n')
      });
    });

    currentNotebook.cells = tempCells;
  }

  publicMethods.build = function (networkCode) {
    initNotebook();
    addCodeCells(networkCode);

    return currentNotebook;
  }

  return publicMethods;

})();

const fetchNetworkCode = () => {
  if (!currentNetwork || !currentNetwork.networkElementList) {
    return [];
  }

  // call getCode for all blocks at the same time to speed things up
  const fetchCodePromises = [];
  const networkElements = Object.entries(currentNetwork.networkElementList);

  for (let networkElement of networkElements) {
    const promise = addIdToLayerCode.call(this, networkElement);
    fetchCodePromises.push(promise);
  }

  return Promise.all(fetchCodePromises).then(code => {
    return code.filter(c => c).map(c => c);
  });

  function addIdToLayerCode(networkElement) {
    // wrote this litte function because we want a layerId key with the code
    // this is to help with the sorting in the next step

    // networkElement[0] is just the layerId
    const networkInformation = networkElement[1];
    const payload = {
      layerId: networkInformation.layerId,
      settings: networkInformation.layerSettings
    };

    return store
      .dispatch("mod_api/API_getCode", payload)
      .then(result => {
        result.layerId = networkInformation.layerId;
        return result;
      });
  }
}

const fetchImports = () => {
  return store
    .dispatch("mod_api/API_getNotebookImports", { 'Layers': coreNetwork })
    .then(importStatements => importStatements)
    .catch(error => []);
}

const fetchRunScripts = () => {
  return store
    .dispatch("mod_api/API_getNotebookRunscript", { 'Layers': coreNetwork })
    .then(runStatements => runStatements)
    .catch(error => []);
}

const fetchNetworkCodeOrder = () => {
  return store
    .dispatch("mod_api/API_getGraphOrder", coreNetwork)
    .then(codeOrder => codeOrder)
    .catch(error => []);
}

const sortNetworkCode = (array, sortOrder = null) => {
  if (!array || !sortOrder) { return; }

  // current sort is O(n^2), will use Map if most networks have many elements
  const sortedArray = [];
  for (let sortKey of sortOrder) {
    let targetCode = array.find(element => element.layerId === sortKey);
    if (targetCode) {
      sortedArray.push(targetCode.Output);
    }
  }
  return sortedArray;
}

export const createNotebookJson = async (storeReference) => {
  if (!storeReference) { return; }

  store = storeReference;
  coreNetwork = store.getters['mod_api/GET_coreNetwork'];
  currentNetwork = store.getters['mod_workspace/GET_currentNetwork'];

  return Promise.all([
    fetchNetworkCode(),
    fetchNetworkCodeOrder(),
    fetchImports(),
    fetchRunScripts()
  ])
  .then(([networkCodes, networkCodeOrder, importStatements, fetchRunScripts]) => {
    // console.log('networkCode', networkCodes);
    // console.log('networkCodeOrder', networkCodeOrder);
    const validCodes = networkCodes.filter(nc => nc); // remove undefined (timedout)
    const sortedCode = sortNetworkCode(validCodes, networkCodeOrder);

    sortedCode.unshift(importStatements);
    sortedCode.push(fetchRunScripts);

    const notebookJson = notebookJsonBuilderV4.build(sortedCode);

    return notebookJson;
  })
  .catch(() => Promise.reject());

}

export default {
  createNotebookJson
}