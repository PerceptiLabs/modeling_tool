const netElementSettings = {
  inject: ['hideAllWindow'],
  props: {
    currentEl: {
      type: Object,
    }
  },
  data() {
    return {
      tabSelected: 0,
      tabs: ['Settings', 'Code'],
      settings: {}
    }
  },
  mounted() {
    if(typeof(this.layerSettings) !== 'string') {
      this.settings = JSON.parse(JSON.stringify(this.layerSettings));
    }
    this.$store.dispatch('mod_api/API_getInputDim');
  },
  computed: {
    userMode() {
      return this.$store.state.globalView.userMode
    },
    layerSettings() {
      return this.$store.getters['mod_workspace/GET_currentSelectedEl'][0].layerSettings;
    },
    codeInputDim() {
      return this.currentEl.layerMeta.InputDim
    },
    coreCode() {
      return ''
    }
  },
  methods: {
    setTab(i) {
      this.tabSelected = i;
    },
    applySettings() {
      this.hideAllWindow();
      if(this._name === '<SetTrainNormal>') this.settings.Labels = this.idSelectElement;
      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': this.coreCode,
        'set': this.settings
      };

      this.$store.dispatch('mod_workspace/SET_elementSettings', saveSettings);
      this.$store.dispatch('mod_api/API_getOutputDim')
    }
  }
};

export default netElementSettings

