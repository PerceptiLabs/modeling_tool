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
  // created() {
  //   // if(this.chartDataDefault){
  //   //   this.chartData = {...this.chartDataDefault}
  //   // }
  // },
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
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest
    },
    doRequest() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.chartsRequest.doRequest
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
      //this.chartData = {...this.chartDataDefault};
      this.getData();
    },
    chartRequest(layerId, layerType, view) {
      this.startRequest = new Date();

      if(layerId === undefined) {
        return
      }
      //this.$store.commit('mod_events/set_charts_requestCounterAdd');
      let theData = {
        reciever: this.currentNetworkID,
        //action: 'getLayerStatistics',
        action: this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest
          ? 'getTestingStatistics'
          : 'getTrainingStatistics',
        value: {
          layerId: layerId,
          layerType: layerType,
          view: view
        }
      };
      coreRequest(theData, null, null, this._name)
        .then((data)=> {
          if(data === 'Null') {
            return
          }
          Vue.nonreactive(data);
          if(view.length) {
            this.$set(this.chartData, view, data)
          }
          else this.chartData = data;

          //console.log(data);
          let stopRequest = new Date();
          let answerDelay = stopRequest - this.startRequest;
          this.$store.dispatch('mod_workspace/CHECK_requestInterval', answerDelay);
          // console.log(`request -> before show ${this._name}`, `${answerDelay}ms`);
        })
        .catch((err)=> {
          console.log('answer err');
          console.error(err);
        });
    }
  }
};

export default viewBoxMixin
