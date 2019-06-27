import SettingsCode     from '@/components/network-elements/elements-settings/setting-code.vue';
import NetBaseSettings  from '@/components/network-elements/net-base-settings/net-base-settings.vue';

const netElementSettings = {
  inject: ['hideAllWindow'],
  props: {
    currentEl: {
      type: Object,
    }
  },
  components: { SettingsCode, NetBaseSettings },
  data() {
    return {
      settings: {},
      coreCode: '',
    }
  },
  mounted() {
    this.$store.dispatch('mod_api/API_getInputDim')
      .then(()=>{
        if(!this.currentEl.layerCode) {
          this.updateCode();
        }
        else {
          this.settings = JSON.parse(JSON.stringify(this.currentEl.layerSettings));
          this.coreCode = this.currentEl.layerCode
        }
      })
  },
  computed: {
    userMode() {
      return this.$store.state.globalView.userMode
    },
    codeInputDim() {
      return this.currentEl.layerMeta.InputDim
    },
  },
  methods: {
    updateCode() {
      this.coreCode = this.settingsCode
    },
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
    applySettings(tabName) {
      if(this._name === '<SetTrainNormal>') this.settings.Labels = this.idSelectElement;
      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': this.coreCode,
        'set': this.settings,
        tabName
      };
      this.$store.dispatch('mod_workspace/SET_elementSettings', saveSettings);
      this.$store.dispatch('mod_api/API_getOutputDim');
      this.hideAllWindow();
    }
  }
};

export default netElementSettings

