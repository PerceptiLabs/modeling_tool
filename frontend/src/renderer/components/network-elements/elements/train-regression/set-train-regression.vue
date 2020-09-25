<template lang="pug">
  div
    .settings-layer_section
      .form_row
        .form_label(v-tooltip-interactive:right="interactiveInfo.epochs") Epochs:
        #tutorial_epochs.form_input(data-tutorial-hover-info)
          input(
            type="number"
            v-model="settings.Epochs"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label Batch Size: 
        .form_input
          input(
            type="number"
            v-model="settings.Batch_size"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.costFunction")
        .form_label Loss function:
        #tutorial_cost-function.tutorial-relative.form_input(data-tutorial-hover-info)
          base-radio(group-name="group" value-input="Regression" v-model="settings.Loss")
            span Regression
            //-Cross-Entropy
      .form_row(v-if="settings.Loss === 'W_cross_entropy'")
        .form_label Class weights:
        .form_input
          input(
            type="number"
            v-model="settings.Class_weights"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.optimizer")
        .form_label Optimizer:
        #tutorial_optimizer.form_input(data-tutorial-hover-info)
          base-radio(group-name="group1" value-input="ADAM" v-model="settings.Optimizer")
            span ADAM
          base-radio(group-name="group1" value-input="SGD" v-model="settings.Optimizer")
            span SGD
          base-radio(group-name="group1" value-input="Momentum" v-model="settings.Optimizer")
            span Momentum
          base-radio(group-name="group1" value-input="RMSprop" v-model="settings.Optimizer")
            span RMSprop

      template(v-if="settings.Optimizer === 'ADAM'")
        .form_row
          .form_label Beta 1:
          .form_input
            input(
              type="number"
              v-model="settings.Beta_1"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
        .form_row
          .form_label Beta 2:
          .form_input
            input(
              type="number"
              v-model="settings.Beta_2"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
      template(v-if="settings.Optimizer === 'Momentum'")
        .form_row
          .form_label Momentum:
          .form_input
            input(
              type="number"
              v-model="settings.Momentum"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
        .form_row
          .form_label Decay rate:
          .form_input
            input(
              type="number"
              v-model="settings.Decay_rate"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
        .form_row
          .form_label Decay steps:
          .form_input
            input(
              type="number"
              v-model="settings.Decay_steps"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
        .form_label Learning rate:
        #tutorial_learning_rate.form_input(data-tutorial-hover-info)
          input(
            type="number"
            v-model="settings.Learning_rate"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")

    //- template(slot="Code-content")
    //-   settings-code(
    //-     :current-el="currentEl"
    //-     :el-settings="settings"
    //-     v-model="coreCode"
    //-   )

</template>

<script>
import mixinSet from '@/core/mixins/net-element-settings.js';
import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'SetTrainRegression',
  mixins: [ mixinSet, mixinFocus ],
  beforeMount() {
    this.inputId.forEach((id)=> {
      let elList = this.currentNetworkList;
      this.inputLayers.push({
        text: elList[id].layerName,
        value: elList[id].layerId,
        tutorialId: elList[id].tutorialId
      })
    });
    if(!this.settings.Labels && this.inputLayers.length) this.settings.Labels = this.inputLayers[0].value.toString();
  },
  data() {
    return {
      inputLayers: [],
      settings: {
        Labels: '',
        Epochs: '10',
        N_class: '1',
        Loss: "Regression", 
        Class_weights: '1',
        Learning_rate: "0.001",
        Optimizer: "ADAM", //#SGD, Momentum, ADAM, RMSprop
        Beta_1: '0.9',
        Beta_2: '0.999',
        Momentum: '0.9',
        Decay_steps: '100000',
        Decay_rate: '0.96',
        Batch_size: 8,
        Training_iters: "20000"
      },
      interactiveInfo: {
        labels: {
          title: 'Labels',
          text: 'Choose which input connection is represent the labels'
        },
        epochs: {
          title: 'epochs',
          text: 'Choose'
        },
        costFunction: {
          title: 'Split on',
          text: 'Choose in which position to split on at the chosen axis'
         },
        optimizer: {
          title: 'Optimizer',
          text: 'Choose which optimizer to use'
        },
        learningRate: {
          title: 'Learning rate',
          text: 'Set the learning rate'
        }
      }
    }
  },
  mounted() {
    this.saveSettingsToStore("Settings");
  },
  computed: {
    ...mapGetters({
      isTutorialMode:     'mod_tutorials/getIsTutorialMode',
      currentNetworkList: 'mod_workspace/GET_currentNetworkElementList'
    }),
    inputId() {
      return this.currentEl.connectionIn
    },
    notLabelsInput() {
      return this.inputId.filter((id)=>id !== this.settings.Labels)
    },
  },
  methods: {
    ...mapActions({
      popupInfo:               'globalView/GP_infoPopup'
    }),
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
  },
}
</script>
