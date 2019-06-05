<template lang="pug">
  net-base-settings
    template(slot="Settings-content")
      .settings-layer_section
        .form_row
          .form_label Reshape:
          .form_input
            triple-input#tutorial_input-reshape.tutorial-relative(v-model="settings.Shape")
      //.settings-layer_section
        .form_row
          .form_label Reshape:
          .form_input
            input(type="text")
      //.settings-layer_section
        .form_row
          .form_label Transpose:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row
          .form_label Transpose:
          .form_input
            triple-input(v-model="settings.Permutation")

    template(slot="Code-content")
      settings-code(:the-code="coreCode")

    template(slot="action")
      button#tutorial_button-apply.btn.btn--primary(type="button" @click="saveSettings") Apply
</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
 // import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
  import TripleInput    from "@/components/base/triple-input";
  import { mapActions } from 'vuex';

  export default {
    name: 'SetProcessReshape',
    mixins: [mixinSet],
    components: { TripleInput },
    data() {
      return {
        settings: {
          Shape: [28,28,1],
          Permutation: [0,1,2],
        }
      }
    },
    computed: {
      coreCode() {
        return `Y=tf.reshape(X, [-1]+[layer_output for layer_output in [${this.settings.Shape}]]);
Y=tf.transpose(Y,perm=[0]+[i+1 for i in [${this.settings.Permutation}]]);`
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:    'mod_tutorials/pointActivate',
      }),
      saveSettings() {
        this.applySettings();
        this.tutorialPointActivate({way: 'next', validation: 'tutorial_input-reshape'})
      }
    }
  }
</script>
