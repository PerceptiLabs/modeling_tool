<template lang="pug">
  .popup
    ul.popup_tab-set
      template(v-if="tabSelected !== 'Preview'")
        button.popup_header(
          v-for="(tab, i) in tabSet"
          :key="tab.i"
          :class="{'disable': tabSelected != tab}"
          :disabled="tab === 'Code' && isTutorial || disableSettings"
          @click="setTab(tab)"
        )
          h4(v-html="tab")
          i.icon.icon-code-error(
            v-if="tab === 'Code' && currentEl.layerCodeError"
          )
      .popup_header.disable(v-else)
        h4 Preview
    .popup_tab-body
      .popup_body.active(
        v-for="(tabContent, i) in tabSet"
        :key="tabContent.i"
        v-if="tabSelected === tabContent"
        )
        .settings-layer
          slot(:name="tabContent+'-content'")
        #js-hide-btn.settings-layer_foot
          slot(:name="tabContent+'-action'")
            button.btn.btn--primary.btn--disabled(type="button"
              @click="hideAllWindow"
              :disabled="isTutorial"
            ) Cancel
            button.btn.btn--primary(type="button"
              @click="applySettings(tabContent)"
              :id="idSetBtn"
            ) Apply
            //-button.btn.btn--dark-blue-rev(type="button"
              v-if="showUpdateCode"
              @click="updateCode"
              ) Update code
      .popup_body.active(v-if="tabSelected === 'Preview'")
        settings-preview(
          :current-el="currentEl"
          @to-settings="toSettings"
          )


</template>

<script>
  import coreRequest  from "@/core/apiCore.js";
  import SettingsPreview  from "@/components/network-elements/elements-settings/setting-preview.vue";
export default {
  name: 'NetBaseSettings',
  components: {SettingsPreview },
  inject: ['hideAllWindow'],
  props: {
    tabSet: {
      type: Array,
      default: function() {
        return ['Settings', 'Code']
      }
    },
    currentEl: {
      type: Object,
    },
    idSetBtn: {
      type: String,
      default: ''
    },
    showPreview: {
      type: Boolean,
      default: false
    }
  },
  mounted() {
    this.toSettings();
    if(this.currentEl.layerCode || this.currentEl.layerSettings) this.tabSelected = 'Preview';
  },
  data() {
    return {
      tabSelected: '',
      disableSettings: false,
    }
  },
  computed: {
    isTutorial() {
      return this.$store.getters['mod_tutorials/getIstutorialMode']
    }
  },
  watch: {
    showPreview(newVal) {
      if(newVal) this.tabSelected = 'Preview';
    }
  },
  methods: {
    coreRequest,
    toSettings() {
      let tab = this.currentEl.layerSettingsTabName || this.tabSet[0];
      if(tab === 'Code') this.disableSettings = true;
      this.setTab(tab);
    },
    setTab(name) {
      this.tabSelected = name;
    },
    applySettings(name) {
      this.$emit('press-apply', name);
      //const elId = this.currentEl.layerId;
      if(name !== 'Cloud') {
        this.tabSelected = 'Preview';this.tabSelected = 'Preview';
      }
      let tab = this.currentEl.layerSettingsTabName || this.tabSet[0];
      if(tab === 'Code') this.disableSettings = true;
    },
    updateCode(name) {
      this.$emit('press-update')
    },
    // confirmSettings() {
    //   this.$emit('press-confirm');
    // },

  }
}
</script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  .popup {
    min-width: 29rem;
    box-shadow: $layer-shad;
  }
  .popup_body {
    max-width: calc(50vw - #{$w-sidebar});
    min-width: 29rem;
  }
  .popup_header {
    .icon {
      margin-left: 1em;
    }
  }
  .popup_body--show-code {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    top: 0;
    max-width: none;
    background-color: $bg-toolbar;
    max-height: none;
    .settings-layer {
      max-height: none;
      overflow: hidden;
    }
  }
  .settings-layer_foot {
    justify-content: flex-end;
    .btn {
      height: auto;
      min-width: 7rem;
    }
    .btn + .btn {
      margin-left: .8rem;
    }
  }
</style>
