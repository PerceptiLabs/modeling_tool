<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Neurons:
              .form_input
                input(type="number" v-model="settings.Neurons")
          .settings-layer_section
            .form_row
              .form_label Recurrent alternative:
              .form_input
                div
                  base-radio(groupName="group" valueInput="LSTM" v-model="settings.Version")
                    span LSTM
                div
                  base-radio(groupName="group" valueInput="GRU" v-model="settings.Version")
                    span GRU
                div
                  base-radio(groupName="group" valueInput="RNN" v-model="settings.Version")
                    span RNN
                //div
                  button.btn.btn--primary(type="button") Custom

          .settings-layer_section
            .form_row
              .form_label Time steps:
              .form_input
                input(type="number" v-model="settings.Time_steps")

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
        :the-code="coreCode"
        )
    .settings-layer_foot
      button.btn.btn--primary(type="button" @click="applySettings") Apply

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetDeepLearningRecurrent',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        Neurons: "10",
        Version: "LSTM", //#LSTM, GRU, RNN
        Time_steps: "2",
      }
    }
  },
  computed: {
    coreCode() {
      switch (this.settings.Version) {
        case 'LSTM':
          return `
          node=tf.reshape(X,[-1, ${this.settings.Time_steps}, np.prod(${this.codeInputDim})]);
          cell = tf.nn.rnn_cell.LSTMCell(${this.settings.Neurons}, state_is_tuple=True);
          rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype);
          Y=tf.reshape(rnn_outputs,[-1,cell.output_size]);`
          break;
        case 'GRU':
          return `
          node=tf.reshape(X,[-1, ${this.settings.Time_steps}, np.prod(${this.codeInputDim})]);
          cell = tf.nn.rnn_cell.GRUCell(${this.settings.Neurons});
          rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype);
          Y=tf.reshape(rnn_outputs,[-1,cell.output_size]);`
          break;
        case 'RNN':
          return `
          node=tf.reshape(X,[-1, ${this.settings.Time_steps}, np.prod(${this.codeInputDim})]);
          cell = tf.nn.rnn_cell.BasicRNNCell(${this.settings.Neurons});
          rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype);
          Y=tf.reshape(rnn_outputs,[-1,cell.output_size]);`
          break;
      }
    }
  }
}
</script>
