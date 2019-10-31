import SettingsCode     from '@/components/network-elements/elements-settings/setting-code.vue';
import NetBaseSettings  from '@/components/network-elements/net-base-settings/net-base-settings.vue';
import { deepCopy }     from "@/core/helpers.js";

const netElementSettings = {
  props: {
    currentEl: {
      type: Object,
    }
  },
  components: { SettingsCode, NetBaseSettings },
  beforeMount() {
    if(this.currentEl.layerSettings) this.settings = deepCopy(this.currentEl.layerSettings);
  },
  data() {
    return {
      settings: {},
      coreCode: ''
    }
  },
  computed: {
    userMode() {
      return this.$store.getters['mod_user/GET_userRole']
    },
    codeInputDim() {
      return this.currentEl.layerMeta.InputDim
    },
  },
  methods: {
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
    applySettings(tabName) {
      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': this.coreCode ? deepCopy(this.coreCode) : null,
        'set': this.settings,
        tabName
      };
      this.$store.dispatch('mod_workspace/SET_elementSettings', deepCopy(saveSettings));
      this.$store.dispatch('mod_tracker/EVENT_applyLayerSettings', tabName, {root: true});
    },
    confirmSettings() {
      this.hideAllWindow();
    }
  }
};

export default netElementSettings

