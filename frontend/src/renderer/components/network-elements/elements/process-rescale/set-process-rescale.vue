<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    id-set-btn="tutorial_button-apply"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
    )
    template(slot="Settings-content")
      .settings-layer_section.rescale
        .form_row
          .form_label Width * Height:
          .form_input
            input(type="number" v-model="settings.width" @keyup="changeWidth")
          .form_input
            input(type="number" v-model="settings.height"  @keyup="changeHeight")
        button.btn.btn--icon.visible-icon.rescale(
          type="button"
          :class="{'invisible-icon': !isLocked}"
          @click="toggleLock()"
        )
          i.icon.icon-lock
        i.icon.multiple.icon-app-close


    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import { mapActions, mapGetters } from 'vuex';

  export default {
    name: 'SetProcessRescale',
    mixins: [mixinSet],
    mounted() {
      this.$store.dispatch('mod_api/API_getInputDim');
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
      }
    }
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
    top: 20px;
    right: 32%;
  }
</style>
