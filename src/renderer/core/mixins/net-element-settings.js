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
    }
  },
  mounted() {
    if(typeof(this.layerSettings) !== 'string') {
      this.settings = JSON.parse(JSON.stringify(this.layerSettings));
    }
  },
  computed: {
    userMode() {
      return this.$store.state.globalView.userMode
    },
    layerSettings() {
      return this.$store.getters['mod_workspace/GET_currentSelectedEl'][0].el.layerSettings;
    },
    codeInputDim() {
      return this.currentEl.layerMeta.InputDim
    }
  },
  methods: {
    setTab(i) {
      this.tabSelected = i;
    },
    applySettings() {
      this.hideAllWindow();
      if(this._name === '<SetTrainNormal>') {
        this.settings.Labels = this.idSelectElement;
      }
      const saveSettings = {
        'code': this.coreCode,
        'set': this.settings
      };
      this.$store.dispatch('mod_workspace/SET_elementSettings', saveSettings);
      this.$store.dispatch('mod_api/API_getBeForEnd');
    }
  }
};

export default netElementSettings

