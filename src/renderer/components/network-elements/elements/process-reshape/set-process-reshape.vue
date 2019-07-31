<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    id-set-btn="tutorial_button-apply"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
    @press-update="updateCode"
    )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.reshape")
          .form_label Reshape:
          #tutorial_input-reshape.form_input(data-tutorial-hover-info)
            triple-input.tutorial-relative(v-model="settings.Shape")

      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.transpose")
          .form_label Transpose:
          #tutorial_input-transpose.form_input(data-tutorial-hover-info)
            triple-input(v-model="settings.Permutation")

    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        v-model="coreCode"
      )

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import TripleInput    from "@/components/base/triple-input";
  import { mapActions, mapGetters } from 'vuex';

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
      ...mapGetters({
        isTutorialMode: 'mod_tutorials/getIstutorialMode'
      }),
      codeDefault() {
        return {
          Output: `Y=tf.reshape(X, [-1]+[layer_output for layer_output in [${this.settings.Shape}]]);
Y=tf.transpose(Y,perm=[0]+[i+1 for i in [${this.settings.Permutation}]]);`
        }
      }
    },
    watch: {
      'settings.Shape': {
        handler(newValue, oldVal) {
          let correctVal = oldVal.every((item, index)=> {
            return item === newValue[index]
          });

          if(this.isTutorialMode && !correctVal) {
            this.infoPopup("Please don't change value of Reshape field when you in tutorial mode.");
            this.settings.Shape = [28,28,1];
          }
        }
      },
      'settings.Permutation': {
        handler(newValue, oldVal) {
          let correctVal = oldVal.every((item, index)=> {
            return item === newValue[index]
          });

          if(this.isTutorialMode && !correctVal) {
            this.infoPopup("Please don't change value of Transpose field when you in tutorial mode.");
            this.settings.Permutation = [0,1,2];
          }
        }
      },
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:    'mod_tutorials/pointActivate',
        infoPopup:                'globalView/GP_infoPopup',
      }),
      saveSettings(tabName) {
        this.applySettings(tabName);
        this.tutorialPointActivate({way: 'next', validation: 'tutorial_input-reshape'})
      },
    }
  }
</script>
