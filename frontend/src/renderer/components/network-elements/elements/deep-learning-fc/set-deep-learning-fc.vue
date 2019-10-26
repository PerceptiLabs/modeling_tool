<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    id-set-btn="tutorial_button-apply"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.neurons")
          .form_label Neurons:
          #tutorial_neurons.tutorial-relative.form_input(data-tutorial-hover-info)
            input(type="text" v-model="settings.Neurons")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.activationFunction")
          .form_label Activation function:
          #tutorial_activation_function.form_input(data-tutorial-hover-info)
            base-radio(group-name="group1" value-input="None"  v-model="settings.Activation_function")
              span None
            base-radio(group-name="group1" value-input="Sigmoid"  v-model="settings.Activation_function")
              span Sigmoid
            base-radio(group-name="group1" value-input="ReLU"  v-model="settings.Activation_function")
              span ReLU
            base-radio(group-name="group1" value-input="Tanh"  v-model="settings.Activation_function")
              span Tanh
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dropout")
          .form_label Dropout:
          .form_input
            base-radio(group-name="group5" :value-input="true" v-model="settings.Dropout")
              span Yes
            base-radio(group-name="group5" :value-input="false" v-model="settings.Dropout")
              span No

      .settings-layer_section(v-if="settings.Dropout")
        .form_row(v-tooltip-interactive:right="interactiveInfo.pooling")
          .form_label Keep probability:
          .form_input
            input(type="number" v-model="settings.Keep_prob")
    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
  import NetBaseSettings  from '@/components/network-elements/net-base-settings/net-base-settings.vue';
  import {mapGetters, mapActions}   from 'vuex';

  export default {
    name: 'SetDeepLearningFC',
    mixins: [mixinSet],
    components: { SettingsCode, NetBaseSettings },
    data() {
      return {
        settings: {
          Neurons :"10",
          Activation_function: "Sigmoid",
          Dropout: false,
          Keep_prob: '1',
        },
        interactiveInfo: {
          neurons: {
            title: 'Neurons',
            text: 'Set how many neurons to use'
          },
          activationFunction: {
            title: 'Activation function',
            text: 'Choose activation function for each neuron'
          },
          dropout: {
            title: 'Dropout',
            text: 'Choose if dropout should be used or not'
          }
        },
      }
    },
    computed: {
      ...mapGetters({
        isTutorialMode: 'mod_tutorials/getIstutorialMode'
      }),
    },
    watch: {
      'settings.Neurons': {
        handler() {
          if(this.isTutorialMode) {
            this.settings.Neurons = 10;
            this.popupInfo("While the value of this field should be 10. But soon you will be able to set a different number of neurons. We are working on it");
          }
        }
      },
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:   'mod_tutorials/pointActivate',
        popupInfo:               'globalView/GP_infoPopup'
      }),
      saveSettings(tabName) {
        this.applySettings(tabName);
        this.$nextTick(()=> this.tutorialPointActivate({way: 'next', validation: 'tutorial_neurons'}));
      }
    }
  }
</script>
