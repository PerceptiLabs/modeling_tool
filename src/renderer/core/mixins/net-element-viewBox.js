const viewBoxMixin = {
  data() {
    return {
      idTimer: null,
      timeInterval: 1000,
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
    }
  }
};

export default viewBoxMixin
