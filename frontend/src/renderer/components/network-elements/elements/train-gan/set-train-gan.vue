<template lang="pug">
  div
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.labels")
        .form_label Switch:
        #tutorial_labels.form_input(data-tutorial-hover-info)
          base-select(
            v-model="settings.switch_layer"
            :select-options="allSwitchLayers"
          )
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.labels")
        .form_label Real Data:
        #tutorial_labels.form_input(data-tutorial-hover-info)
          base-select(
            v-model="settings.real_data_layer"
            :select-options="allRealDataLayers"
          )
    .settings-layer_section
      .form_row
        .form_label Epochs:
        .form_input
          input(
            type="number"
            v-model="settings.Epochs"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    // .settings-layer_section
    //   .form_row(v-tooltip-interactive:right="interactiveInfo.costFunction")
    //     .form_label Cost function:
    //     #tutorial_cost-function.tutorial-relative.form_input(data-tutorial-hover-info)
    //       base-radio(group-name="group" value-input="Cross_entropy" v-model="settings.Loss")
    //         span Cross-Entropy
    //       base-radio(group-name="group" value-input="Quadratic" v-model="settings.Loss")
    //         span Quadratic
    //       base-radio(group-name="group" value-input="W_cross_entropy" v-model="settings.Loss")
    //         span Weighted Cross-Entropy
    //       base-radio(group-name="group" value-input="Dice" v-model="settings.Loss")
    //         span DICE
    //       base-radio(group-name="group" value-input="Regression" v-model="settings.Loss")
    //         span Regression
    //         //-Cross-Entropy
    //   .form_row(v-if="settings.Loss === 'W_cross_entropy'")
    //     .form_label Class weights:
    //     .form_input
    //       input(type="number" v-model="settings.Class_weights")
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
    .settings-layer_section
      .form_row
        .form_label Batch Size:
        .form_input
          input(
            type="number"
            v-model="settings.batch_size"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label Additional Stop Condition:
        #tutorial_stop-condition.tutorial-relative.form_input(data-tutorial-hover-info)
          base-radio(group-name="group2" value-input="Epochs" v-model="settings.Stop_condition")
            span None
          base-radio(group-name="group2" value-input="TargetAccuracy" v-model="settings.Stop_condition")
            span Target Accuracy
      template(v-if="settings.Stop_condition === 'TargetAccuracy'")
        .form_row
          .form_label Target Accuracy for Stop Condition:
          .form_input
            input(
              type="number"
              v-model="settings.Stop_Target_Accuracy"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)") 
            span %


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
  name: 'SetTrainGan',
  mixins: [ mixinSet, mixinFocus ],
  beforeMount() {
    let elList = this.currentNetworkList;
    for(let key in elList) {
      if(elList[key].layerType === "Data") {
        this.allRealDataLayers.push({
          text: elList[key].layerName,
          value: elList[key].layerName,
          tutorialId: elList[key].tutorialId
        })
      }
      if(elList[key].layerType === "Other" && elList[key].componentName === 'MathSwitch') {
        this.allSwitchLayers.push({
          text: elList[key].layerName,
          value: elList[key].layerName,
          tutorialId: elList[key].tutorialId
        })
      }
    }
    if(!this.settings.switch_layer && this.allSwitchLayers.length) this.settings.switch_layer = this.allSwitchLayers[0].value.toString();
    if(!this.settings.real_data_layer && this.allRealDataLayers.length) this.settings.real_data_layer = this.allRealDataLayers[0].value.toString();
  },
  data() {
    return {
      allSwitchLayers: [],
      allRealDataLayers: [],
      settings: {
        switch_layer: '',
        real_data_layer: '',
        Epochs: '10',
        N_class: '1',
        Loss: "Quadratic", //#Cross_entropy, Quadratic, W_cross_entropy, Dice
        Stop_condition: "Epochs",
        Stop_Target_Accuracy: 0,
        Class_weights: '1',
        Learning_rate: "0.001",
        batch_size: '3',
        Optimizer: "ADAM", //#SGD, Momentum, ADAM, RMSprop
        Beta_1: '0.9',
        Beta_2: '0.999',
        Momentum: '0.9',
        Decay_steps: '100000',
        Decay_rate: '0.96',
        Training_iters: "20000"
      },
      interactiveInfo: {
        labels: {
          title: 'Labels',
          text: 'Choose which input connection represents the labels'
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
    })
  },
  methods: {
    ...mapActions({
      popupInfo:               'globalView/GP_infoPopup'
    }),
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
  }
}
</script>
