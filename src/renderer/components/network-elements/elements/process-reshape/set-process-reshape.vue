<template lang="pug">
  net-base-settings(
    :first-tab="currentEl.layerSettingsTabName"
    @press-apply="saveSettings($event)"
    @press-update="updateCode"
    )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.reshape")
          .form_label Reshape:
          .form_input
            triple-input#tutorial_input-reshape.tutorial-relative(v-model="settings.Shape")

      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.transpose")
          .form_label Transpose:
          .form_input
            triple-input(v-model="settings.Permutation")

    template(slot="Code-content")
      settings-code(v-model="coreCode")

    template(slot="Settings-action")
      button#tutorial_button-apply.btn.btn--primary(type="button" @click="saveSettings('Settings')") Apply
      button.btn.btn--dark-blue-rev(type="button" @click="updateCode") Update code


</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
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
        },
        interactiveInfo: {
          reshape: {
            title: 'Reshape',
            text: 'Set the new shape of the data'
          },
          transpose: {
            title: 'Transpose',
            text: 'Change the axis positions of the data'
          }
        },
      }
    },
    computed: {
      settingsCode() {
        return `Y=tf.reshape(X, [-1]+[layer_output for layer_output in [${this.settings.Shape}]]);
Y=tf.transpose(Y,perm=[0]+[i+1 for i in [${this.settings.Permutation}]]);`
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:    'mod_tutorials/pointActivate',
      }),
      saveSettings(tabName) {
        this.applySettings(tabName);
        this.tutorialPointActivate({way: 'next', validation: 'tutorial_input-reshape'})
      }
    }
  }
</script>
