<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    :show-preview="showPreview"
    @press-apply="saveSettings($event)"
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

      //-.settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.timeSteps")
          .form_label Time steps:
          .form_input
            input(type="number" v-model="settings.Time_steps")

      .settings-layer_section
        .form_row(v-tooltip-interactive:right='interactiveInfo.returnSequence')
          .form_label Return sequence:
          .form_input
            base-radio(group-name="probability" :value-input="true"  v-model="settings.Return_sequence")
              span Yes
            base-radio(group-name="probability" :value-input="false"  v-model="settings.Return_sequence")
              span No

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
    template(slot="Settings-action")
      button.btn.btn--primary(type="button"
        v-coming-soon="true"
      ) Custom
      button.btn.btn--primary.btn--disabled(type="button"
        @click="hideAllWindow"
      ) Cancel
      button.btn.btn--primary(type="button"
        @click="applyRecurrentSettings"
      ) Apply

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetDeepLearningRecurrent',
  mixins: [mixinSet],
  inject: ['hideAllWindow'],
  data() {
    return {
      showPreview: false,
      settings: {
        Neurons: "10",
        Version: "LSTM", //#LSTM, GRU, RNN
        Time_steps: "1",
        Dropout: false, //True, False
        Return_sequence: false, //True, False
        Keep_prob: "1"
      },
      interactiveInfo: {
        neurons: {
          title: 'Neurons',
          text: 'Set how many neurons to use.'
        },
        returnSequence: {
          title: 'Return sequence',
          text: 'Select if return sequence should be used'
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
  },
  methods: {
    applyRecurrentSettings() {
      this.applySettings('Settings');
      this.showPreview = true
    }
  }
}
</script>
