<template lang="pug">
  .settings-layer_section.rescale
    .form_row
      .form_label Width * Height:
      .form_input(style="padding-left: 0")
        input(
          style="width: 60px"
          type="number"
          v-model="settings.width"
          @focus="setIsSettingInputFocused(true)"
          @blur="setIsSettingInputFocused(false)"
          @keyup="changeWidth"
          )
      .form_input
        input(
          style="width: 60px"
          type="number" 
          v-model="settings.height"
          @focus="setIsSettingInputFocused(true)"
          @blur="setIsSettingInputFocused(false)"
          @keyup="changeHeight"
          )
    button.btn.btn--icon.visible-icon.rescale(
      type="button"
      :class="{'invisible-icon': !isLocked}"
      @click="toggleLock()"
    )
      i.icon.icon-lock
    i.icon.multiple.icon-app-close
    
</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
  import { mapActions, mapGetters } from 'vuex';

  export default {
    name: 'SetProcessRescale',
    mixins: [mixinSet, mixinFocus],
    mounted() {
      this.$store.dispatch('mod_api/API_getInputDim');
      this.saveSettingsToStore("Settings");
      if(this.currentEl.layerMeta.InputDim) {
        const dimention = this.currentEl.layerMeta.InputDim.split(",");
        const width = parseInt(dimention[0].slice(1));
        const height = parseInt(dimention[1].slice(1));

        this.ratio = height / width;
        this.settings.width = width;
        this.settings.height = height;
      }
    },
    data() {
      return {
        settings: {
          width: 40,
          height: 30
        },
        isLocked: true,
        ratio: 0.75
      }
    },
    methods: {
      changeWidth() {
        if(this.isLocked) {
          this.settings.height = parseInt(this.settings.width * this.ratio);
        }
      },
      changeHeight() {
        if(this.isLocked) {
          this.settings.width = parseInt(this.settings.height / this.ratio);
        }
      },
      saveSettings(tabName) {
        this.applySettings(tabName);
      },
      toggleLock() {
        this.isLocked = !this.isLocked;
        if(this.isLocked && this.settings.width > 0) 
          this.ratio = this.settings.height / this.settings.width
      }
    },
  }
</script>

<style lang="scss">
  @import "../../../../scss/base";
  .visible-icon {
    &.invisible-icon {
      color: $disable-txt;
    }
  }
  .settings-layer_section.rescale {
    margin-top: 10px;
    position: relative;
  }
  .btn--icon.rescale {
    position: absolute;
    top: 0;
    right: 10px;
  }
  .multiple.icon-app-close {
    position: absolute;
    top: 18px;
    right: 31%;
    font-size: 6px;    
  }
</style>
