import coreRequest  from "@/core/apiCore.js";

const netElementSettingsData = {
  props: {
    layerId: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      imgData: null,
    }
  },
  computed: {
    currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
    },
    inputPath() {
      return this.settings.accessProperties.Path.join(', ')
    }
  },
  methods: {
    coreRequest,
    // getDataPlot(type) {
    //   let theData = {
    //     reciever: this.currentNetworkID,
    //     action: 'getDataPlot',
    //     value: {
    //       Id: this.layerId,
    //       Type: type,
    //       Properties: this.settings
    //     }
    //   };
    //   //console.log('getDataImg', theData);
    //   this.coreRequest(theData)
    //     .then((data)=> {
    //       //console.log('answer getDataImg', data);
    //       if(data === 'Null') {
    //         return
    //       }
    //       this.imgData = data;
    //     })
    //     .catch((err)=> {
    //       console.log('answer err');
    //       console.error(err);
    //     });
    // },
    // getDataMeta(type) {
    //   let theData = {
    //     reciever: this.currentNetworkID,
    //     action: 'getDataMeta',
    //     value: {
    //       Id: this.layerId,
    //       Type: type,
    //       Properties: this.settings
    //     }
    //   };
    //   //console.log(theData);
    //   return this.coreRequest(theData)
    //     .then((data) => {
    //       //console.log('getDataMeta ', data);
    //       if (data === 'Null') {
    //         return
    //       }
    //       this.settings.accessProperties.Dataset_size = data.Dataset_size;
    //       if (data.Columns.length) {
    //         if (!this.settings.accessProperties.Columns) this.settings.accessProperties.Columns = [0];
    //         data.Columns.forEach((el, index) => this.dataColumns.push({text: el, value: index}))
    //       }
    //     })
    //     .catch((err) => {
    //       console.error(err);
    //     });
    // },

    dataSettingsMeta(layerType) {
      return this.deleteDataMeta(layerType)
        .then(()=> this.getDataMeta(layerType))
    },
    dataSettingsPlot(layerType) {
      this.deleteDataMeta(layerType)
        .then(()=> this.getDataMeta(layerType))
        .then(()=> this.getDataPlot(layerType))
    },

    getDataPlot(type) {
      let theData = {
        reciever: this.currentNetworkID,
        action: 'getDataPlot',
        value: {
          Id: this.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      this.coreRequest(theData)
        .then((data) => {
          if (data) this.imgData = data;
        })
        .catch((err)=> {
          console.log('answer err');
          console.error(err);
        });
    },
    getDataMeta(type) {
      let theData = {
        reciever: this.currentNetworkID,
        action: 'getDataMeta',
        value: {
          Id: this.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      //console.log(theData);
      return this.coreRequest(theData)
        .then((data) => {
          if (data) {
            this.settings.accessProperties = {...this.settings.accessProperties, ...data};
            return data;
          }
          else throw 'error 115'
        })
        .catch((err) => {
          console.error(err);
        });
    },
    deleteDataMeta(type) {
      let theData = {
        reciever: this.currentNetworkID,
        action: 'deleteData',
        value: {
          Id: this.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      return this.coreRequest(theData)
        .then((data) => data)
        .catch((err) => {
          console.error(err);
        });
    },
  }
};

export default netElementSettingsData