<template lang="pug">
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo")
      .form_label Number of classes:
      #tutorial_number-of-classes.form_input.tutorial-relative
        input(
          type="text"
          v-model="settings.N_class"
          @focus="setIsSettingInputFocused(true)"
          @blur="setIsSettingInputFocused(false)"
          )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
import {mapGetters, mapActions } from 'vuex';

export default {
  name: 'SetProcessOneHot',
  mixins: [mixinSet, mixinFocus],
  data() {
    return {
      settings: {
        N_class: '10',
      },
      interactiveInfo: {
        title: 'Number of classes',
        text: 'Set the number of classes in the data'
      }
    }
  },
  mounted() {
    this.saveSettingsToStore("Settings");
  },
  watch: {
    'settings.N_class': {
      handler() {
        if(this.isTutorialMode) {
          this.settings.N_class = 10;
          this.popupInfo("While the value of this field should be 10. But soon you will be able to set a different number of classes in the data. We are working on it");
        }
      }
    },
  },
  computed: {
    ...mapGetters({
      isTutorialMode: 'mod_tutorials/getIsTutorialMode'
    }),
  },
  methods: {
    ...mapActions({
       popupInfo:                'globalView/GP_infoPopup'
    }),
    saveSettings(tabName) {
      this.applySettings(tabName);
    }
  },
}
</script>
