import VueNonreactive from 'vue-nonreactive/vue-nonreactive.js';
import Vue from 'vue'
Vue.use(VueNonreactive);
import requestApi   from "@/core/api.js";

const viewBoxMixin = {
  data() {
    return {
      chartData: {},
      saveParams: {}
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
  // beforeDestroy() {
  //   clearInterval(this.idTimer);
  //   this.chartData = {};
  // },
  computed: {
    statElementID() {
      let viewBoxEl = this.$store.getters['mod_workspace/GET_currentSelectedEl'].find((element)=>element.el.layerType === 'Training');
      return viewBoxEl === undefined ? undefined : viewBoxEl.el.layerId.toString()
    },
    boxElementID() {
      let viewBoxEl = this.$store.getters['mod_workspace/GET_currentSelectedEl'].find((element)=>element.el.layerType !== 'Training');
      return viewBoxEl === undefined ? undefined : viewBoxEl.el.layerId.toString()
    },
    currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
    },
    serverStatus() {
      return this.$store.getters['mod_workspace/GET_networkCoreStatus']
    },
    eventRequest() {
      return this.$store.state.mod_events.chartsRequest.doRequest
    },
    // eventShowChart() {
    //   //return this.$store.state.mod_api.startWatchGetStatus
    // },
    testIsOpen() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest
    },
  },
  watch: {
    boxElementID() {
      this.resetViewBox();
    },
    statElementID() {
      this.resetViewBox();
    },
    eventRequest(newVal) {
      if(!(newVal % 2)) this.getData();
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
      if(layerId === undefined) {
        return
      }
      //this.$store.commit('mod_events/set_charts_requestCounterAdd');
      let theData = {
        reciever: this.currentNetworkID,
        action: 'getLayerStatistics',
        value: {
          layerId: layerId,
          layerType: layerType,
          view: view
        }
      };
      //console.log('send');
      const client = new requestApi();
      client.sendMessage(theData)
        .then((data)=> {
          //console.log(data);
          if(data === 'Null') {
            return
          }
          Vue.nonreactive(data);
          if(view.length) {
            this.$set(this.chartData, view, data)
          }
          else this.chartData = data;
        })
        .catch((err)=> {
          console.log('answer err');
          console.error(err);
        });
    }
  }
};

export default viewBoxMixin
