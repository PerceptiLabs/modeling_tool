import SettingsCode     from '@/components/network-elements/elements-settings/setting-code.vue';
import NetBaseSettings  from '@/components/network-elements/net-base-settings/net-base-settings.vue';
import { deepCopy }     from "@/core/helpers.js";
import isEqual from 'lodash.isequal';
const netElementSettings = {
  props: {
    currentEl: {
      type: Object,
    }
  },
  components: { SettingsCode, NetBaseSettings },
  beforeMount() {
    this.isSettedFromCore = true;
    if(this.currentEl.layerSettings) this.settings = deepCopy(this.currentEl.layerSettings);

  },
  data() {
    return {
      isSettedFromCore: false,
      settings: {},
      coreCode: null
    }
  },
  watch: {
    'computedSettings': {
      handler(newVal, oldVal) {
        if(this.isSettedFromCore) {
          this.isSettedFromCore = false;
        } else {
          if(!isEqual(JSON.parse(JSON.stringify(newVal)), JSON.parse(JSON.stringify(oldVal)))) {
            this.saveSettings("Settings");
          }
        }
      },
      deep: true,
    },
  },
  computed: {
    userMode() {
      return this.$store.getters['mod_user/GET_userRole']
    },
    codeInputDim() {
      return this.currentEl.layerMeta.InputDim
    },
    computedSettings: function() {
      return Object.assign({}, this.settings);
    }
  },
  methods: {
    saveSettingsToStore(tabName) {
      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': this.currentEl.layerCode ? deepCopy(this.currentEl.layerCode) : null,
        'set': this.settings,
        'visited': this.currentEl.visited,
        tabName
      };
      this.$store.dispatch('mod_workspace/SET_elementSettings', deepCopy(saveSettings));
    },
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
    applySettings(tabName) {
      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': this.currentEl.layerCode,
        'set': this.settings,
        'visited': true,
        tabName
      };
      this.$store.dispatch('mod_workspace/SET_elementSettings', deepCopy(saveSettings));
      // console.trace();
      this.$store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', this.currentEl.layerId);
      // this.$store.dispatch('mod_api/API_getPreviewSample',  {layerId: this.currentEl.layerId, varData: 'output'}).then((data)=> {
      //   this.$store.dispatch('mod_workspace/SET_NetworkChartData', { 
      //     layerId: this.currentEl.layerId,
      //     payload: data,
      //   });
      //   this.$store.dispatch('mod_events/EVENT_calcArray');
      // });
      this.$store.dispatch('mod_tracker/EVENT_applyLayerSettings', {
        componentName: this.currentEl.componentName, 
        tabName
      }, {root: true});
      // this.$store.dispatch('mod_api/API_updateNetworkSetting', this.currentEl.layerId);
    },
    confirmSettings() {
      this.hideAllWindow();
    }
  }
};

export default netElementSettings

