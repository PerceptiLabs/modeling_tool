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
      actionSpace: ''
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
            if(data.Action_space) this.actionSpace = data.Action_space;
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