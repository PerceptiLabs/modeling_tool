import VueNonreactive from 'vue-nonreactive/vue-nonreactive.js';
import Vue from 'vue'
Vue.use(VueNonreactive);

import coreRequest  from "@/core/apiCore.js";

const viewBoxMixin = {
  props: {
    currentTab: {type: String, default: ''}
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
      let viewBoxEl = this.$store.getters['mod_workspace/GET_currentSelectedEl'].find((element)=>element.layerType === 'Training');
      return viewBoxEl === undefined ? undefined : viewBoxEl.layerId.toString()
    },
    boxElementID() {
      let viewBoxEl = this.$store.getters['mod_workspace/GET_currentSelectedEl'].find((element)=>element.layerType !== 'Training');
      return viewBoxEl === undefined ? undefined : viewBoxEl.layerId.toString()
    },
    currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId']
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
    chartRequest(layerId, layerType, view) {
      this.startRequest = new Date();

      if(!layerId || !layerType) return;
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
          if(data === 'Null' || data === null) {
            return
          }
          Vue.nonreactive(data);
          if(view.length) {
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
