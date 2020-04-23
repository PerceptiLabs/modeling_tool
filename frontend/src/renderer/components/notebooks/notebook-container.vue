<template>
  <div id="notebook-container">
    <div id="cell-list">
      <notebook-cell
        v-for="cell in cells"
        :key="cell.layerId"
        :cell="cell"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { stringifyNetworkObjects, promiseWithTimeout } from '@/core/helpers';

import NotebookCell from "@/components/notebooks/notebook-cell.vue";

export default {
  components: {
    NotebookCell
  },
  computed: {
    ...mapGetters({
      currentNetwork: "mod_workspace/GET_currentNetwork",
      coreNetwork: "mod_api/GET_coreNetwork"
    })
  },
  data() {
    return {
      cells: []
    };
  },
  methods: {
    updateNotebook(){
      Promise.all([
          this.fetchNetworkCode(),
          this.fetchNetworkCodeOrder()
        ])
        .then(([networkCodes, networkCodeOrder]) => {

          // console.log('notebookJson', notebookJson);
          // console.log('networkCode', networkCodes);
          // console.log('networkCodeOrder', networkCodeOrder);

          const validNetworkCodes = networkCodes.filter(nc => nc);
          const sortedCode = this.sortNetworkCode(validNetworkCodes, networkCodeOrder);

          this.cells = sortedCode;
        });
    },
    getDefaultNotebookJson() {
      const defaultJson = {
        "cells": [
          {
          "cell_type": "code",
          "execution_count": null,
          "metadata": {},
          "outputs": [],
          "source": []
          }
        ],
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
      };
      
      return JSON.parse(JSON.stringify(defaultJson));
    },
    fetchNetworkCode() {
      if (!this.currentNetwork || !this.currentNetwork.networkElementList) {
        return [];
      }

      const fetchCodePromises = [];

      const networkElements = Object.entries(this.currentNetwork.networkElementList);
      for (let networkElement of networkElements) {
        const promise = addIdToLayerCode.call(this, networkElement);
        fetchCodePromises.push(promiseWithTimeout(400, promise));
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

        return this.$store
          .dispatch("mod_api/API_getCode", payload)
          .then(result => {
            result.layerId = networkInformation.layerId;
            return result;
          });
      }
    },
    fetchNetworkCodeOrder() {
      return this.$store
        .dispatch("mod_api/API_getGraphOrder", this.coreNetwork)
        .then(codeOrder => codeOrder)
        .catch(error => []);
    },
    sortNetworkCode(array, sortOrder = null) {
      if (!array || !sortOrder) { return; }

      // current sort is O(n^2), will use Map if most networks have many elements
      const sortedArray = [];
      for (let sortKey of sortOrder) {

        let targetCode = array.find(element => element.layerId === sortKey);
        if (targetCode) {
          sortedArray.push(targetCode);
        }
      }
      return sortedArray;
    },
  },
  watch: {
    currentNetwork: {
      immediate: true,
      handler(newValue) {
          this.updateNotebook();
      }
    }
  },
};
</script>

<style lang="scss" scoped>
@import '../../scss/base/_variables.scss';


::-webkit-scrollbar {
  background: $bg-workspace;
  width: 6px;
}

::-webkit-scrollbar-thumb {
  border-radius: 3px;
  background-color: rgba(#989FB0, .5);
  box-shadow: 0 0 6px rgba(#000, .3);
  &:hover {
    background-color: rgba(#989FB0, 1);
  }
  &:window-inactive {
    background-color: rgba(#989FB0, .2);
  }
}

#notebook-container {
  background-color: $bg-workspace;
  padding: 5rem 0;

  width: 100%;
  height: 100%;
  overflow-y: scroll;

  #cell-list {
    display: flex;
    flex-direction: column;
  }
}
</style>