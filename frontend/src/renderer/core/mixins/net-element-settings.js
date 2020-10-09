import SettingsCode     from '@/components/network-elements/elements-settings/setting-code.vue';
import NetBaseSettings  from '@/components/network-elements/net-base-settings/net-base-settings.vue';
import { deepCopy, debounce }     from "@/core/helpers.js";
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
    if(this.currentEl.layerSettings) {
      this.settings = deepCopy(this.currentEl.layerSettings);
    } else {
      // it will be triggered only when component is created
      this.saveSettingsToStore("Settings");
      this.$store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', this.currentEl.layerId);
    }

  },
  created() {
    this.debouncedSaveSettings = debounce( function() {
      this.saveSettings("Settings", true);
    }, 800)
  },
  data() {
    return {
      isSettedFromCore: false,
      settings: {},
      coreCode: null,
      debouncedSaveSettings: null,
    }
  },
  watch: {
    'computedSettings': {
      handler(newVal, oldVal) {
        if(this.isSettedFromCore) {
          this.isSettedFromCore = false;
        } else {
          if(!isEqual(JSON.parse(JSON.stringify(newVal)), JSON.parse(JSON.stringify(oldVal)))) {
            // Note that the "saveSettings" function called is the one in the layer.
            // Not the one in this file.
            this.debouncedSaveSettings();
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
      this.$store.dispatch('mod_workspace/SET_elementSettings', {settings: deepCopy(saveSettings), pushOntoHistory: false}, false);
    },
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
    applySettings(tabName, pushOntoHistory) {
      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': this.currentEl.layerCode,
        'set': this.settings,
        'visited': true,
        tabName
      };
      this.$store.dispatch('mod_workspace/SET_elementSettings', {settings: deepCopy(saveSettings), pushOntoHistory});
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

