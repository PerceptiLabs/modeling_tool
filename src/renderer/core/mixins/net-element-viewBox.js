import requestApi   from "@/core/api.js";

const viewBoxMixin = {
  data() {
    return {
      chartData: {},
      idTimer: null,
      timeInterval: 1000,
      saveParams: {}
    }
  },
  mounted() {
    this.getStatistics()
  },
  beforeDestroy() {
    clearInterval(this.idTimer);
  },
  computed: {
    statElementID() {
      let viewBoxEl = this.$store.getters['mod_workspace/GET_currentSelectedEl'].find((element)=>element.el.layerType === 'Training');
      return viewBoxEl.el.layerId.toString()
    },
    boxElementID() {
      let viewBoxEl = this.$store.getters['mod_workspace/GET_currentSelectedEl'].find((element)=>element.el.layerType !== 'Training');
      return viewBoxEl.el.layerId.toString()
    },
    currentNetworkName() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkName
    },
    serverStatus() {
      return this.$store.getters['mod_api/GET_serverStatus']
    },
  },
  watch: {
    serverStatus(newStatus, oldStatus) {
      if(oldStatus === 'Paused') {
        this.returnDataRequest(this.saveParams.layerId, this.saveParams.layerType, this.saveParams.view);
      }
    }
  },
  methods: {
    returnDataRequest(layerId, layerType, view) {
      return {
        reciever: this.currentNetworkName,
        action: 'getLayerStatistics',
        value: {
          layerId: layerId,
          layerType: layerType,
          view: view
        }
      };
    },
    chartRequest(layerId, layerType, view) {
      //TODO it is not work
      this.saveParams = {
          layerId,
          layerType,
          view
      };
      let theData = {
        reciever: this.currentNetworkName,
        action: 'getLayerStatistics',
        value: {
          layerId: layerId,
          layerType: layerType,
          view: view
        }
      };
      //TODO need stop when pause
      let idTimer = setInterval(()=>{
        if(this.serverStatus === 'Finished') {
          clearInterval(idTimer);
        }
        if(this.serverStatus === 'Training') {
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> {
              this.chartData = data
            })
            .catch((err) =>{
              console.error(err);
              clearInterval(this.idTimer);
            });
        }
      }, this.timeInterval)
    }
  }
};

export default viewBoxMixin
