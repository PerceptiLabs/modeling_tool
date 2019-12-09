<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.method")
          .form_label Method:
          .form_input
            base-radio(group-name="group" value-input="Q_learning" v-model="settings.ReinforceType")
              span Q-learning
            base-radio(group-name="group" value-input="Policy_learning" v-model="settings.ReinforceType")
              span Policy-learning
            base-radio(group-name="group" value-input="A3C" v-model="settings.ReinforceType")
              span A3C
            base-radio(group-name="group" value-input="A2C" v-model="settings.ReinforceType")
              span A2C
            base-radio(group-name="group" value-input="PPO" v-model="settings.ReinforceType")
              span PPO
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.optimizer")
          .form_label Optimizer:
          .form_input
            base-radio(group-name="group1" value-input="SGD" v-model="settings.Optimizer")
              span SGD
            base-radio(group-name="group1" value-input="Adam" v-model="settings.Optimizer")
              span Adam
            base-radio(group-name="group1" value-input="Momentum" v-model="settings.Optimizer")
              span Momentum
            base-radio(group-name="group1" value-input="RMSprop" v-model="settings.Optimizer")
              span RMSprop
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
          .form_label Learning rate:
          .form_input
            input(type="text" v-model="settings.Learning_rate")
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
    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetTrainReinforce',
  mixins: [mixinSet],
  data() {
    return {
      settings: {
        ReinforceType: 'Q_learning',
        Update_freq: '4',
        Gamma: '0.95',
        Loss: 'Quadratic',
        Eps: '1',
        Eps_min: '0.1',
        Eps_decay: '0.2',
        Learning_rate: '0.01',
        Optimizer: 'SGD',
      },
      interactiveInfo: {
        method: {
          title: 'Method',
          text: 'Choose which method to use'
        },
        optimizer: {
          title: 'Optimizer',
          text: 'Choose which optimiser to use'
        },
        learningRate: {
          title: 'Learning rate',
          text: 'Set the learning rate'
        }
      }
    }
  }
}
</script>
