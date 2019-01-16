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
  mounted() {
    this.getStatistics();
  },
  // beforeUpdate() {
  //   //this.chartData = {};
  // },
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
  },
  watch: {
    boxElementID() {
      this.resetViewBox();
    },
    statElementID() {
      this.resetViewBox();
    }
  },
  methods: {
    resetViewBox() {
      clearInterval(this.idTimer);
      this.getStatistics();
    },
    setTabAction() {
      clearInterval(this.idTimer);
      this.chartData = {};
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
      //TODO need stop when pause
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
            else this.chartData = data
          })
          .catch((err) =>{
            console.error(err);
            clearInterval(this.idTimer);
          });
      }, this.timeInterval)
    }
  }
};

export default viewBoxMixin
