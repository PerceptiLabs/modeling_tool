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
        if(!this.currentEl.layerCode) this.updateCode();
        else this.coreCode = JSON.parse(JSON.stringify(this.currentEl.layerCode));

        if (this.currentEl.layerSettings) this.settings = JSON.parse(JSON.stringify(this.currentEl.layerSettings));
      })
  },
  computed: {
    userMode() {
      return this.$store.state.globalView.userMode
    },
    codeInputDim() {
      return this.currentEl.layerMeta.InputDim
    },
    // codeDefault
    // codeSettings

  },
  methods: {
    updateCode() {
      this.coreCode = this.codeDefault
    },
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
    applySettings(tabName) {
      if(tabName === 'Settings') {
        this.updateCode();
      }
      console.log(this.coreCode);
      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': this.coreCode ? JSON.parse(JSON.stringify(this.coreCode)) : null,
        'set': this.settings,
        tabName
      };
      this.$store.dispatch('mod_workspace/SET_elementSettings', JSON.parse(JSON.stringify(saveSettings)));
      this.$store.dispatch('mod_api/API_getOutputDim');
      this.hideAllWindow();
    }
  }
};

export default netElementSettings

