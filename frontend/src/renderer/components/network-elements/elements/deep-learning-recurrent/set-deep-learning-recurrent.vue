<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.neurons")
          .form_label Neurons:
          .form_input
            input(type="number" v-model="settings.Neurons")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.recurrentAlternative")
          .form_label Recurrent alternative:
          .form_input
            div
              base-radio(group-name="group" value-input="LSTM" v-model="settings.Version")
                span LSTM
            div
              base-radio(group-name="group" value-input="GRU" v-model="settings.Version")
                span GRU
            div
              base-radio(group-name="group" value-input="RNN" v-model="settings.Version")
                span RNN
            //div
              button.btn.btn--primary(type="button") Custom

      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.timeSteps")
          .form_label Time steps:
          .form_input
            input(type="number" v-model="settings.Time_steps")

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
  name: 'SetDeepLearningRecurrent',
  mixins: [mixinSet],
  data() {
    return {
      settings: {
        Neurons: "10",
        Version: "LSTM", //#LSTM, GRU, RNN
        Time_steps: "2",
      },
      interactiveInfo: {
        neurons: {
          title: 'Neurons',
          text: 'Set how many neurons to use.'
        },
        recurrentAlternative: {
          title: 'Recurrent alternative',
          text: 'Choose which recurrent alternative to use'
        },
        timeSteps: {
          title: 'Time steps',
          text: 'Choose how many time steps to use'
        }
      },
    }
  }
}
</script>
