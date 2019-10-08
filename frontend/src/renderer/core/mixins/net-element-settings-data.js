import coreRequest  from "@/core/apiCore.js";
const netElementSettingsData = {
  data() {
    return {
      Mix_settingsData_imgData: null,
      //Mix_settingsData_actionSpace: '',
      Mix_settingsData_Partition_summary: [70,20,10],
    }
  },
  computed: {
    Mix_settingsData_currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId']
    },
    Mix_settingsData_inputPath() {
      const pathArr = this.settings.accessProperties.Sources.map((el)=> el.path);
      return pathArr.join(', ')
    }
  },
  methods: {
    // ...mapActions({
    //   api_getPreviewVariableList:,
    //   api_getPreviewSample:      'mod_api/API_getPreviewSample',
    // }),
    coreRequest,
    // Mix_settingsData_dataSettingsMeta(layerType) {
    //   return this.Mix_settingsData_deleteDataMeta(layerType)
    //     .then(()=> this.Mix_settingsData_getDataMeta(layerType))
    // },
    // Mix_settingsData_dataSettingsPlot(layerType) {
    //   this.Mix_settingsData_getDataMeta(layerType)
    //     .then(()=> this.Mix_settingsData_getDataPlot(layerType))
    // },
    // Mix_settingsData_getPreviewVariableList(layerId) {
    //   //console.log('Mix_settingsData_getPreviewVariableList');
    //   this.$store.dispatch('mod_api/API_getPreviewVariableList', layerId)
    //     .then((data)=> {
    //       console.log(data);
    //       //this.$store.dispatch('mod_api/API_getPreviewSample', {layerId, varData: 'Y'})
    //       //this.api_getPreviewSample({layerId, })
    //     })
    //     // .then((imgData)=> {
    //     //   console.log(imgData);
    //     // })
    // },
    // Mix_settingsData_getDataPlot(type) {
    //   let theData = {
    //     reciever: this.Mix_settingsData_currentNetworkID,
    //     action: 'getDataPlot',
    //     value: {
    //       Id: this.currentEl.layerId,
    //       Type: type,
    //       Properties: this.settings
    //     }
    //   };
    //   this.coreRequest(theData)
    //     .then((data) => {
    //       console.log('getDataPlot', data);
    //       if (data) this.Mix_settingsData_imgData = data;
    //     })
    //     .catch((err)=> {
    //       console.error(err);
    //     });
    // },

    Mix_settingsData_getDataMeta(layerId) {
      return this.$store.dispatch('mod_api/API_getDataMeta', layerId)
        .then((data) => {
          //console.log('getDataMeta', data);
          if (data) {
            if(data.Action_space) this.Mix_settingsData_actionSpace = data.Action_space;
            this.settings.accessProperties = {...this.settings.accessProperties, ...data};
            return data;
          }
          else throw 'error 70'
        })
        .catch((err) => {
          console.error(err);
        });
    },
    Mix_settingsData_getPartitionSummary(layerId) {
      return this.$store.dispatch('mod_api/API_getPartitionSummary', layerId)
        .then((data) => {
          if (data) {
            this.Mix_settingsData_Partition_summary = data;
          }
          else throw 'error 95'
        })
        .catch((err) => {
          console.error(err);
        });
    },
    Mix_settingsData_deleteDataMeta(type) {
      let theData = {
        reciever: this.Mix_settingsData_currentNetworkID,
        action: 'deleteData',
        value: {
          Id: this.currentEl.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      return this.coreRequest(theData)
        .then((data) => {
          console.log('deleteData', data);
          return data
        })
        .catch((err) => {
          console.error(err);
        });
    },
    Mix_settingsData_prepareSources(pathArr, type) {
      return pathArr.map((el)=> { return {
        type,
        "path": el
      }})
    }
  }
};

export default netElementSettingsData
