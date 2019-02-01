import VueNonreactive from 'vue-nonreactive/vue-nonreactive.js';
import Vue from 'vue'
Vue.use(VueNonreactive);
import requestApi   from "@/core/api.js";

const viewBoxMixin = {
  data() {
    return {
      chartData: {},
      idTimer: null,
      timeInterval: 2000,
      saveParams: {}
    }
  },
  created() {
    if(this.chartDataDefault){
      this.chartData = {...this.chartDataDefault}
    }
  },
  mounted() {
    this.getStatistics();
  },
  beforeDestroy() {
    clearInterval(this.idTimer);
    this.chartData = {};
  },
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
    doRequest() {
      return this.$store.state.mod_api.startWatchGetStatus
    },
  },
  watch: {
    boxElementID() {
      this.resetViewBox();
    },
    statElementID() {
      this.resetViewBox();
    },
    doRequest(newVal) {
      newVal ? this.getData() : null;
    }
  },
  methods: {
    resetViewBox() {
      clearInterval(this.idTimer);
      this.getData();
    },
    setTabAction() {
      clearInterval(this.idTimer);
      this.chartData = {...this.chartDataDefault};
      this.getData();
    },
    chartRequest(layerId, layerType, view) {
      let theData = {
        reciever: this.currentNetworkID,
        action: 'getLayerStatistics',
        value: {
          layerId: layerId,
          layerType: layerType,
          view: view
        }
      };

      this.idTimer = setInterval(()=>{
        if(layerId === undefined) {
          return
        }
        const client = new requestApi();
        client.sendMessage(theData)
          .then((data)=> {
            Vue.nonreactive(data);
            if(view.length) {
              this.$set(this.chartData, view, data)
            }
            else this.chartData = data;
          })
          .catch((err) =>{
            console.error(err);
            clearInterval(this.idTimer);
          });
        if(!this.doRequest) {
          clearInterval(this.idTimer)
        }
      }, this.timeInterval);
    }
  }
};

export default viewBoxMixin
