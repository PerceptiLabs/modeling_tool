import {mapGetters} from "vuex";

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
    if(typeof(this.currentEl.layerSettings) !== 'string') {
      this.settings = JSON.parse(JSON.stringify(this.currentEl.layerSettings));
    }
    this.$store.dispatch('mod_api/API_getInputDim');
  },
  computed: {
    userMode() {
      return this.$store.state.globalView.userMode
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

