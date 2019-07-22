<template lang="pug">
  net-base-settings(
    :layer-code="currentEl.layerCode.length"
    :first-tab="currentEl.layerSettingsTabName"
    @press-apply="saveSettings($event)"
    @press-update="updateCode"
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
      settings-code(v-model="coreCode")

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
  },
  computed: {
    settingsCode() {
      switch (this.settings.Version) {
        case 'LSTM':
          return `node=tf.reshape(X,[-1, ${this.settings.Time_steps}, np.prod(${this.codeInputDim})]);
cell = tf.nn.rnn_cell.LSTMCell(${this.settings.Neurons}, state_is_tuple=True);
rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype);
Y=tf.reshape(rnn_outputs,[-1,cell.output_size]);`
          break;
        case 'GRU':
          return `node=tf.reshape(X,[-1, ${this.settings.Time_steps}, np.prod(${this.codeInputDim})]);
cell = tf.nn.rnn_cell.GRUCell(${this.settings.Neurons});
rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype);
Y=tf.reshape(rnn_outputs,[-1,cell.output_size]);`
          break;
        case 'RNN':
          return `node=tf.reshape(X,[-1, ${this.settings.Time_steps}, np.prod(${this.codeInputDim})]);
cell = tf.nn.rnn_cell.BasicRNNCell(${this.settings.Neurons});
rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype);
Y=tf.reshape(rnn_outputs,[-1,cell.output_size]);`
          break;
      }
    }
  }
}
</script>
