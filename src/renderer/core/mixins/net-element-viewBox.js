import VueNonreactive from 'vue-nonreactive/vue-nonreactive.js';
import Vue from 'vue'
Vue.use(VueNonreactive);

import coreRequest  from "@/core/apiCore.js";

const viewBoxMixin = {
  data() {
    return {
      chartData: {},
      saveParams: {},
      startRequest: 0
    }
  },
  mounted() {
    this.getData();
  },
  beforeDestroy() {
    this.chartData = {};
  },
  computed: {
    statElementID() {
      let viewBoxEl = this.$store.getters['mod_workspace/GET_currentSelectedEl'].find((element)=>element.layerType === 'Training');
      return viewBoxEl === undefined ? undefined : viewBoxEl.layerId.toString()
    },
    boxElementID() {
      let viewBoxEl = this.$store.getters['mod_workspace/GET_currentSelectedEl'].find((element)=>element.layerType !== 'Training');
      return viewBoxEl === undefined ? undefined : viewBoxEl.layerId.toString()
    },
    currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
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
    }
  },
  methods: {
    resetViewBox() {
      this.getData();
    },
    setTabAction() {
      this.getData();
    },
    chartRequest(layerId, layerType, view) {
      this.startRequest = new Date();

      if(!layerId || !layerType) return;
      console.log(layerType);
      let theData = {
        reciever: this.currentNetworkID,
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
          if(data === 'Null') {
            return
          }
          Vue.nonreactive(data);
          console.log(data);
          if(view.length) {
            this.$set(this.chartData, view, data)
          }
          else this.chartData = data;

          let stopRequest = new Date();
          let answerDelay = stopRequest - this.startRequest;
          this.$store.dispatch('mod_workspace/CHECK_requestInterval', answerDelay);
        })
        .catch((err)=> {
          console.log('answer err');
          console.error(err);
        });
    }
  }
};

export default viewBoxMixin
