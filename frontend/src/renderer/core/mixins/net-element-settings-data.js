import {coreRequest}  from "@/core/apiWeb.js";

const netElementSettingsData = {
  data() {
    return {
      imgData: null,
      actionSpace: '',
      Partition_summary: [70,20,10],
    }
  },
  computed: {
    currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
    },
    inputPath() {
      return this.settings.accessProperties.Path.length > 0
        ? this.settings.accessProperties.Path[0].name
        : ''
    }
  },
  methods: {
    coreRequest,
    dataSettingsMeta(layerType) {
      return this.deleteDataMeta(layerType)
        .then(()=> this.getDataMeta(layerType))
    },
    dataSettingsPlot(layerType) {
      //console.log('dataSettingsPlot', layerType);
      this.deleteDataMeta(layerType)
        .then(()=> this.getDataMeta(layerType))
        .then(()=> this.getDataPlot(layerType))
    },

    getDataPlot(type) {
      //console.log('getDataPlot');
      let theData = {
        reciever: this.currentNetworkID,
        action: 'getDataPlot',
        value: {
          Id: this.currentEl.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      this.coreRequest(theData)
        .then((data) => {
          //console.log('getDataPlot', data);
          if (data) this.imgData = data;
        })
        .catch((err)=> {
          //console.log('answer err');
          console.error(err);
        });
    },
    getDataMeta(type) {
      let theData = {
        reciever: this.currentNetworkID,
        action: 'getDataMeta',
        value: {
          Id: this.currentEl.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      //console.log('getDataMeta', theData);
      return this.coreRequest(theData)
        .then((data) => {
          if (data) {
            //console.log('getDataMeta', data);
            if(data.Action_space) this.actionSpace = data.Action_space;
            this.settings.accessProperties = {...this.settings.accessProperties, ...data};
            return data;
          }
          else throw 'error 70'
        })
        .catch((err) => {
          console.error(err);
        });
    },
    getPartitionSummary(type) {

      let theData = {
        reciever: this.currentNetworkID,
        action: 'getPartitionSummary',
        value: {
          Id: this.currentEl.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      //console.log('getPartitionSummary', theData);
      return this.coreRequest(theData)
        .then((data) => {
          //console.log('getPartitionSummary answer', data);
          if (data) {
            this.Partition_summary = data;
          }
          else throw 'error 95'
        })
        .catch((err) => {
          console.error(err);
        });
    },
    deleteDataMeta(type) {
      //console.log('deleteData');
      let theData = {
        reciever: this.currentNetworkID,
        action: 'deleteData',
        value: {
          Id: this.currentEl.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      return this.coreRequest(theData)
        .then((data) => {
          //console.log('deleteData', data);
          return data
        })
        .catch((err) => {
          console.error(err);
        });
    },
  }
};

export default netElementSettingsData
