import VueNonreactive from 'vue-nonreactive/vue-nonreactive.js';
import Vue from 'vue'
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
    currentNetworIdForKernelRequests() {
      return this.$store.getters['mod_workspace/GET_currentNetworIdForKernelRequests']
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

      let theData = {
        receiver: this.currentNetworIdForKernelRequests,
        action: 'getGlobalTrainingStatistics',
        value: { }
      };
      coreRequest(theData)
        .then((data)=> {
          if(data === 'Null' || data === null) {
            return
          }

          // This launch an event to stop fetching statistics infinitely
          if(theData.action === 'getTestingStatistics') {
            this.$store.commit('mod_events/set_componentEvent_test_receiveData');
          }
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

      let theData = {
        receiver: this.currentNetworIdForKernelRequests,
        action: this.$store.getters['mod_workspace/GET_testIsOpen']
          ? 'getTestingStatistics'
          : 'getTrainingStatistics',
        value: {
          layerId: layerId,
          layerType: layerType,
          view: view
        }
      };
      coreRequest(theData)
        .then((data)=> {
          if(data === 'Null' || data === null) {
            return
          }

          // This launch an event to stop fetching statistics infinitely
          if(theData.action === 'getTestingStatistics') {
            this.$store.commit('mod_events/set_componentEvent_test_receiveData');
          }
          
          Vue.nonreactive(data);
          if(view.length && this && this.chartData) {
            this.$set(this.chartData, view, data)
          }
          else this.chartData = data;

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
