<template lang="pug">
  net-base-settings
    template(slot="Settings-content")
      .settings-layer_section
        .form_row
          .form_label Number of classes:
          #tutorial_number-of-classes.form_input.tutorial-relative
            input(type="text" v-model="settings.N_class")
    template(slot="Code-content")
      settings-code(:the-code="coreCode")

    template(slot="action")
      button.btn.btn--primary(type="button" @click="saveSettings") Apply
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
      }
    }
  },
  computed: {
    coreCode() {
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
