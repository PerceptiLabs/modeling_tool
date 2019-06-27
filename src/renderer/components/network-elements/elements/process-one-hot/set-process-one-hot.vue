<template lang="pug">
  net-base-settings(
    :layer-code="currentEl.layerCode.length"
    :first-tab="currentEl.layerSettingsTabName"
    @press-apply="saveSettings($event)"
    @press-update="updateCode"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo")
          .form_label Number of classes:
          #tutorial_number-of-classes.form_input.tutorial-relative
            input(type="text" v-model="settings.N_class")

    template(slot="Code-content")
      settings-code(v-model="coreCode")

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import { mapActions } from 'vuex';

export default {
  name: 'SetProcessOneHot',
  mixins: [mixinSet],
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
  computed: {
    settingsCode() {
      return `Y=tf.one_hot(tf.cast(X,dtype=tf.int32),${this.settings.N_class});`
    }
  },
  methods: {
    ...mapActions({
       tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    saveSettings() {
      this.applySettings();
      this.tutorialPointActivate({way:'next', validation: 'tutorial_number-of-classes'})
    }
  }
}
</script>
