<template>
  <div class="notebook-box">
    <notebook-info-message />
    <div id="notebook-container">
      <div id="cell-list">
        <notebook-cell
          v-for="cell in cells"
          :key="cell.layerId"
          :cell="cell"
          :isFocused="focusedCellId === cell.layerId"
          @click="onCellClick"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { stringifyNetworkObjects, promiseWithTimeout } from '@/core/helpers';

import NotebookCell from "@/components/notebooks/notebook-cell.vue";
import NotebookInfoMessage from "@/components/notebooks/notebook-info-message.vue";

export default {
  components: {
    NotebookCell,
    NotebookInfoMessage,
  },
  computed: {
    ...mapGetters({
      currentNetwork: "mod_workspace/GET_currentNetwork",
      coreNetwork: "mod_api/GET_coreNetwork"
    })
  },
  data() {
    return {
      cells: [],
      focusedCellId: null,
      fetchedCode: {}
    };
  },
  methods: {
    onCellClick(payload) {
      this.focusedCellId = payload;
    },
    updateNotebook(){
      Promise.all([
          this.fetchNetworkCode(),
          this.fetchNetworkCodeOrder()
        ])
        .then(([networkCodes, networkCodeOrder]) => {

          // using "this.fetchedCode" instead of "networkCodes" because when
          // toggling the Notebook button quickly and many times, "networkCodes"
          // can return "undefined".
          const fetchedCodes = Object.values(this.fetchedCode).map(v =>  v);
          const sortedCode = this.sortNetworkCode(fetchedCodes, networkCodeOrder);

          this.cells = sortedCode;
        });
    },
    fetchNetworkCode() {
      if (!this.currentNetwork || !this.currentNetwork.networkElementList) {
        return [];
      }

      const fetchCodePromises = [];

      const networkElements = Object.entries(this.currentNetwork.networkElementList);
      for (let networkElement of networkElements) {
        const promise = promiseWithTimeout(400, addIdToLayerCode.call(this, networkElement));
        
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

        return this.$store
          .dispatch("mod_api/API_getCode", payload)
          .then(result => {
            result.layerId = networkInformation.layerId;
            this.$set(this.fetchedCode, result.layerId, result)

            // don't really need to return any results
            // the results we want are set in "this.fetchedCode"
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
        this.fetchedCode = {};
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

.notebook-box {
  position: relative;
  height: 100%;
}
#notebook-container {
  background-color: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
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