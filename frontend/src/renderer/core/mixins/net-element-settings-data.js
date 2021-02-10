const netElementSettingsData = {
  data() {
    return {
      Mix_settingsData_actionSpace: '',
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
    Mix_settingsData_getDataMeta(layerId, autoUpdateAccessProperties = true) {
      this.$store.commit('mod_workspace/SET_webLoadingDataFlag', true);
      this.showSpinner = true;
      return this.$store.dispatch('mod_api/API_getDataMeta', {layerId, settings: this.settings})
        .then((data) => {
          if (data) {
            if(data.Action_space) {
              this.Mix_settingsData_actionSpace = data.Action_space;
            }

            if (autoUpdateAccessProperties){
              this.settings.accessProperties = {...this.settings.accessProperties, ...data};
            }
            return data;
          }
        })
        .catch((err) => {
          console.error('getDataMeta', err);
        })
        .finally(()=> {
          this.showSpinner = false;
          this.$store.commit('mod_workspace/SET_webLoadingDataFlag', false);
        } )
    },
    Mix_settingsData_getPartitionSummary(layerId) {
      return this.$store.dispatch('mod_api/API_getPartitionSummary', {layerId, settings: this.settings})
        .then((data) => {
          if (data) {
            this.Mix_settingsData_Partition_summary = data;
          }
        })
        .catch((err) => {
          console.error('getPartitionSummary', err);
        });
    },
    // not used more
    Mix_settingsData_deleteDataMeta(type) {
      return Promise.resolve();
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
