import VueNonreactive from 'vue-nonreactive/vue-nonreactive.js';
import Vue from 'vue'
import base64url from "base64url";
import { renderingKernel }  from "@/core/apiRenderingKernel.js";

Vue.use(VueNonreactive);
import {coreRequest }  from "@/core/apiWeb.js";

const viewBoxMixin = {
  props: {
    currentTab: {type: String, default: ''},
    sectionTitle: { type: String, default: ''},
    networkElement: {type: Object, default: function () { return {}}}
  },
  data() {
    return {
      chartData: {},
      saveParams: {},
      startRequest: 0
    }
  },
  mounted() {
    if(this.btnList) this.$emit('btn-list', this.btnList);
    this.getData();
  },
  beforeDestroy() {
    this.chartData = null;
  },
  computed: {
    statElementID() {
      let statisticElement = this.$store.state['mod_statistics'].selectedElArr.statistics;
      return statisticElement.layerId.toString();
    },
    boxElementID() {
      let statisticElement = this.$store.state['mod_statistics'].selectedElArr.viewBox;
      return statisticElement.layerId.toString();
    },
    currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId']
    },
    currentNetworkIdForKernelRequests() {
      return this.$store.getters['mod_workspace/GET_currentNetworkIdForKernelRequests']
    },
    currentTrainingSessionId() {
      const networkId = this.currentNetworkIdForKernelRequests;
      const directory = this.$store.getters['mod_workspace/GET_currentNetworkCheckpointDirectoryByModelId'](networkId)
      return base64url(directory)  // URL safe base64
    },
    serverStatus() {
      return this.$store.getters['mod_workspace/GET_networkCoreStatus']
    },
    testIsOpen() {
      return this.$store.getters['mod_workspace/GET_testIsOpen']
    },
    doRequest() {
      return this.$store.getters['mod_workspace/GET_networkDoRequest']
    },

  },
  watch: {
    boxElementID() {
      this.resetViewBox();
    },
    statElementID() {
      this.resetViewBox();
    },
    doRequest() {
      this.getData();
    },
    currentTab() {
      this.getData();
    }
  },
  methods: {
    resetViewBox() {
      this.getData();
    },
    setTabAction() {
      this.getData();
    },
    chartGlobalRequest() {
      this.startRequest = new Date();

      const modelId = this.currentNetworkIdForKernelRequests;
      const trainingSessionId = this.currentTrainingSessionId
      
      renderingKernel.getTrainingResults(modelId, trainingSessionId, 'global-results')      
        .then((data)=> {
          if(data === 'Null' || data === null) {
            return
          }

          // This launch an event to stop fetching statistics infinitely
          let prevData =  {};
          Object.keys(this.chartData).map(key => {prevData[key] = this.chartData[key]})
          
          Object.keys(data).map(key => {
            prevData[key] = data[key];
          })
          this.chartData = prevData;
          
          let stopRequest = new Date();
          let answerDelay = stopRequest - this.startRequest;
          this.$store.dispatch('mod_workspace/CHECK_requestInterval', answerDelay);
        })
        .catch((err)=> {
          console.error(err);
        });
    },
    chartRequest(layerId, layerType, view) {
      this.startRequest = new Date();

      const modelId = this.currentNetworkIdForKernelRequests;
      const trainingSessionId = this.currentTrainingSessionId;
      
      renderingKernel.getTrainingResults(modelId, trainingSessionId, 'layer-results', layerId, view)
        .then((data)=> {
          if(data === 'Null' || data === null || data === undefined) {
            return
          }
                    
          //  Think that this should be returned by kernel
          
          if (data.PvGAndConfusionMatrix && data.PvGAndConfusionMatrix.LastEpoch) {
            data.PvGAndConfusionMatrix.LastEpoch.xAxis = {
              type: 'category',
              data: data.PvGAndConfusionMatrix.LastEpoch.nameList
            };
          }

          
          Vue.nonreactive(data);
          if(view.length && this && this.chartData) {
            this.$set(this.chartData, view, data)
          }
          else {
            this.chartData = data;
          }
          
          let stopRequest = new Date();
          let answerDelay = stopRequest - this.startRequest;
          this.$store.dispatch('mod_workspace/CHECK_requestInterval', answerDelay);
        })
        .catch((err)=> {
          console.error(err);
        });
    }
  },
};

export default viewBoxMixin
