<template lang="pug">
div
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.method")
      .form_label Method:
      .form_input
        base-radio(
          group-name="group",
          value-input="Q_learning",
          v-model="settings.ReinforceType"
        )
          span Q-learning
        //- base-radio(group-name="group" value-input="Policy_learning" v-model="settings.ReinforceType")
        //-   span Policy-learning
        //- base-radio(group-name="group" value-input="A3C" v-model="settings.ReinforceType")
        //-   span A3C
        //- base-radio(group-name="group" value-input="A2C" v-model="settings.ReinforceType")
        //-   span A2C
        //- base-radio(group-name="group" value-input="PPO" v-model="settings.ReinforceType")
        //-   span PPO
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.optimizer")
      .form_label Optimizer:
      .form_input
        base-radio(
          group-name="group1",
          value-input="SGD",
          v-model="settings.Optimizer"
        )
          span SGD
        base-radio(
          group-name="group1",
          value-input="ADAM",
          v-model="settings.Optimizer"
        )
          span Adam
        base-radio(
          group-name="group1",
          value-input="adagrad",
          v-model="settings.Optimizer"
        )
          span Adagrad
        base-radio(
          group-name="group1",
          value-input="RMSprop",
          v-model="settings.Optimizer"
        )
          span RMSprop
  .settings-layer_section
    .form_row
      .form_label History length:
      .form_input
        input(
          type="number",
          v-model="settings.History_length",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )
  .settings-layer_section
    .form_row
      .form_label Batch size:
      .form_input
        input(
          type="number",
          v-model="settings.Batch_size",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
      .form_label Learning rate:
      .form_input
        input(
          type="text",
          v-model="settings.Learning_rate",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
      .form_label Max steps:
      .form_input
        input(
          type="text",
          v-model="settings.Max_steps",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
      .form_label Episodes:
      .form_input
        input(
          type="text",
          v-model="settings.Episodes",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )
  //-.settings-layer_section
    .form_row
      .form_label Regularization:
      .form_input
        input(type="text" disabled="disabled")
  //-.settings-layer_section
    .form_row
      .form_label Gradient clipping:
      .form_input
        base-checkbox(valueInput="Pooling" v-model="settings.pooling")
  //-.settings-layer_section
    .form_row
      .form_label Clip at:
      .form_input
        input(type="number" disabled="disabled")
  //- template(slot="Code-content")
  //-   settings-code(
  //-     :current-el="currentEl"
  //-     :el-settings="settings"
  //-     v-model="coreCode"
  //-   )
</template>

<script>
import mixinSet from "@/core/mixins/net-element-settings.js";
import mixinFocus from "@/core/mixins/net-element-settings-input-focus.js";

export default {
  name: "SetTrainReinforce",
  mixins: [mixinSet, mixinFocus],
  data() {
    return {
      settings: {
        ReinforceType: "Q_learning",
        Update_freq: "4",
        Gamma: "0.95",
        Loss: "Quadratic",
        Eps: "1",
        Eps_min: "0.1",
        Eps_decay: "0.2",
        Learning_rate: "0.01",
        Optimizer: "SGD",
        Max_steps: "1000",
        Episodes: "20000",
        History_length: "10",
        Batch_size: "32"
      },
      interactiveInfo: {
        method: {
          title: "Method",
          text: "Choose which method to use"
        },
        optimizer: {
          title: "Optimizer",
          text: "Choose which optimiser to use"
        },
        learningRate: {
          title: "Learning rate",
          text: "Set the learning rate"
        }
      }
    };
  },
  mounted() {
    this.saveSettingsToStore("Settings");
  }
};
</script>
