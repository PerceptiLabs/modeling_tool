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
    currentNetworkName() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
    },
    serverStatus() {
      return this.$store.getters['mod_workspace/GET_networkCoreStatus']
    },
  },
  watch: {
    serverStatus(newStatus, oldStatus) {
      if(oldStatus === 'Paused') {
        this.returnDataRequest(this.saveParams.layerId, this.saveParams.layerType, this.saveParams.view);
      }
    },
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
      // if(layerId === undefined) {
      //   setTimeout(()=>{
      //     this.chartRequest(layerId, layerType, view);
      //   }, 500);
      //   return
      // }
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
      this.idTimer = setInterval(()=>{
        // if(this.serverStatus === 'Finished') {
        //   clearInterval(this.idTimer);
        // }
        //if(this.serverStatus === 'Training') {
        if(layerId === undefined) {
          return
        }
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> {
              //console.log(data);
              if(view.length) {
                //this.chartData[view] = data
                this.$set(this.chartData, view, data)
              }
              else this.chartData = data
            })
            .catch((err) =>{
              console.error(err);
              clearInterval(this.idTimer);
            });
        //}
      }, this.timeInterval)
    }
  }
};

export default viewBoxMixin
