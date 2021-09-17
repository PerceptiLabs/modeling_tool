import SettingsCode     from '@/components/network-elements/elements-settings/setting-code.vue';
import NetBaseSettings  from '@/components/network-elements/net-base-settings/net-base-settings.vue';
import { deepCopy, debounce }     from "@/core/helpers.js";
import isEqual from 'lodash.isequal';
import cloneDeep from 'lodash.clonedeep';

const netElementSettings = {
  props: {
    currentEl: {
      type: Object,
    }
  },
  components: { SettingsCode, NetBaseSettings },
  beforeMount() {
    this.isSetFromCore = true;
    if(this.currentEl.layerSettings) {
      this.settings = deepCopy(this.currentEl.layerSettings);
    } else {
      // it will be triggered only when component is created
      this.saveSettingsToStore("Settings");
      this.$store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', this.currentEl.layerId);
    }

    if(!this.currentEl.hasOwnProperty('initialSettings')) {
      this.$store.dispatch('mod_workspace/setNetworkElementDefaultSetting', { layerId: this.currentEl.layerId});
    }

  },
  created() {
    this.debouncedSaveSettings = debounce( function() {
      this.saveSettings("Settings", true);
    }, 800)
  },
  data() {
    return {
      isSetFromCore: false,
      settings: {},
      coreCode: null,
      debouncedSaveSettings: null,
      isFirstSettingChange: true,
    }
  },
  watch: {
    'computedSettings': {
      handler(newVal, oldVal) {
        if(!isEqual(JSON.parse(JSON.stringify(newVal)), JSON.parse(JSON.stringify(oldVal)))) {
          // Note that the "saveSettings" function called is the one in the layer.
          // Not the one in this file.
          if(this.isFirstSettingChange) {
            this.isFirstSettingChange = false;
          } else {
            this.debouncedSaveSettings();
          }
        }
      },
      deep: true,
    },
    resetSettingClicker : {
      handler() {
        this.isSetFromCore = true;
        this.settings = cloneDeep(this.currentEl.layerSettings);
      }
    }
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
    },
    resetSettingClicker() {
      return this.$store.state.mod_events.componentEvents.model.resetSettingClick;
    },
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
      this.$store.dispatch('mod_tracker/EVENT_applyLayerSettings', {
        componentName: this.currentEl.componentName, 
        tabName
      }, {root: true});
    },
    confirmSettings() {
      this.hideAllWindow();
    }
  }
};

export default netElementSettings

