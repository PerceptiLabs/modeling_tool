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
              .form_label Labels:
              .form_input
                base-select(
                  v-model="idSelectElement"
                  :selectOptions="inputLayers"
                  )
          .settings-layer_section
            .form_row
              .form_label Cost function:
              .form_input
                base-radio(groupName="group" valueInput="Cross_entropy" v-model="settings.Loss")
                  span Cross-Entropy
                base-radio(groupName="group" valueInput="Quadratic" v-model="settings.Loss")
                  span Quadratic
                base-radio(groupName="group" valueInput="W_cross_entropy" v-model="settings.Loss")
                  span Weighted Cross-Entropy
                base-radio(groupName="group" valueInput="Dice" v-model="settings.Loss")
                  span DICE
                  //-Cross-Entropy
            .form_row(v-if="settings.Loss === 'W_cross_entropy'")
              .form_label Class weights:
              .form_input
                input(type="number" v-model="settings.Class_weights")
          .settings-layer_section
            .form_row
              .form_label Optimizer:
              .form_input
                base-radio(groupName="group1" valueInput="ADAM" v-model="settings.Optimizer")
                  span ADAM
                base-radio(groupName="group1" valueInput="SGD" v-model="settings.Optimizer")
                  span SGD
                base-radio(groupName="group1" valueInput="Momentum" v-model="settings.Optimizer")
                  span Momentum
                base-radio(groupName="group1" valueInput="RMSprop" v-model="settings.Optimizer")
                  span RMSprop
            template(v-if="settings.Optimizer === 'ADAM'")
              .form_row
                .form_label Beta 1:
                .form_input
                  input(type="mod_workspace" v-model="settings.Beta_1")
              .form_row
                .form_label Beta 2:
                .form_input
                  input(type="number" v-model="settings.Beta_2")
            template(v-if="settings.Optimizer === 'Momentum'")
              .form_row
                .form_label Momentum:
                .form_input
                  input(type="number" v-model="settings.Momentum")
              .form_row
                .form_label Decay:
                .form_input
                  input(type="number" v-model="settings.Decay")
          .settings-layer_section
            .form_row
              .form_label Learning rate:
              .form_input
                input(type="number" v-model="settings.Learning_rate")
          //.settings-layer_section
            .form_row
              .form_label Regularization:
              .form_input
                input(type="text")
          //.settings-layer_section
            .form_row
              .form_label N_class:
              .form_input
                input(type="text" v-model="settings.N_class")
          //.settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-checkbox(valueInput="Pooling" v-model="settings.pooling")
          //.settings-layer_section
            .form_row
              .form_label Learning rate:
              .form_input
                input(type="number")

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
  name: 'SetTrainNormal',
  mixins: [mixinSet],
  components: { SettingsCode },
  props: {
    inputId: {
      type: Array,
    }
  },
  created() {
    this.inputId.forEach((id)=>{
      let el = this.currentNetworkList.filter((element)=> element.layerId === id);
      this.inputLayers.push({
        text: el[0].layerName,
        value: el[0].layerId
      })
    });
    // this.$nextTick(()=>{
    //
    // });
  },
  mounted() {
    if(this.settings.Labels) {
      this.idSelectElement = this.settings.Labels;
    }
    else this.idSelectElement = this.inputLayers[0].value;
  },
  data() {
    return {
      inputLayers: [],
      idSelectElement: '',
      settings: {
        Labels: '',
        N_class: '1',
        Loss: "Cross_entropy", //#Cross_entropy, Quadratic, W_cross_entropy, Dice
        Class_weights: 1,
        Learning_rate: "0.01",
        Optimizer: "SGD", //#SGD, Momentum, ADAM, RMSprop
        Beta_1: '0.1',
        Beta_2: '0.1',
        Momentum: '0.1',
        Decay: '0.1',
        Training_iters: "20000"
      },
    }
  },
  computed: {
    network_output() {
      return this.inputId.filter((id)=>id !== this.idSelectElement)
    },
    labels() {
      let lab = [];
      lab.push(this.idSelectElement);
      return lab
    },
    currentNetworkList() {
      return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
    },
    coreCode() {
      let loss = '';
      let optimizer = '';
      let accuracy = '';
      switch (this.settings.Loss) {
        case 'Cross_entropy':
          loss = `flat_logits = tf.reshape(X['${this.network_output}'], [-1, N_class]);
flat_labels = tf.reshape(X['${this.labels}'], [-1, N_class]);
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=flat_labels, logits=flat_logits));`
          break;
        case 'Quadratic':
          loss = `loss=tf.losses.mean_squared_error(X['${this.labels}'],X['${this.network_output}']);`
          break;
        case 'W_cross_entropy':
          loss = `flat_logits = tf.reshape(X['${this.network_output}'], [-1, N_class]);
flat_labels = tf.reshape(X['${this.labels}'], [-1, N_class]);
class_weights = tf.constant(${this.settings.Class_weights},dtype=tf.float32);
loss = tf.reduce_mean(tf.nn.weighted_cross_entropy_with_logits(flat_labels,flat_logits, ${this.settings.Class_weights}));`
          break;
        case 'Dice':
          loss = `eps = 1e-5;
prediction = X['${this.network_output}'];
intersection = tf.reduce_sum(tf.multiply(prediction, X['${this.labels}']));
union = eps + tf.reduce_sum(tf.multiply(prediction, prediction)) + tf.reduce_sum(tf.multiply(X['${this.labels}'], X['${this.labels}']));
cost_tmp = (2 * intersection/ (union));
cost_clip = tf.clip_by_value(cost_tmp, eps, 1.0-eps);
loss = 1 - cost_clip;`
          break;
      }
      switch (this.settings.Optimizer) {
        case 'SGD':
          optimizer = `optimizer = tf.train.GradientDescentOptimizer(${this.settings.Learning_rate}).minimize(loss);
Y=optimizer;`
          break;
        case 'Momentum':
          optimizer = `global_step = tf.Variable(0);
start_learning_rate = ${this.settings.Learning_rate};
learning_rate_momentum = tf.train.exponential_decay(learning_rate=start_learning_rate,global_step=global_step, decay_steps=${this.settings.Training_iters},decay_rate=${this.settings.Decay}, staircase=True);
Y=tf.train.MomentumOptimizer(learning_rate=learning_rate_momentum,momentum=${this.settings.Momentum}).minimize(loss,global_step=global_step);`
          break;
        case 'ADAM':
          optimizer = `Y=tf.train.AdamOptimizer(${this.settings.Learning_rate},beta1=${this.settings.Beta_1},beta2=${this.settings.Beta_2}).minimize(loss);`
          break;
        case 'RMSprop':
          optimizer = `Y=tf.train.RMSPropOptimizer(${this.settings.Learning_rate},decay=${this.settings.Decay},momentum=${this.settings.Momentum}).minimize(loss);`
          break;
      }
      if(this.settings.N_Class < 1) {
        accuracy = `correct_prediction = tf.equal(X['${this.network_output}'], X['${this.labels}']);
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32));`
      }
      else accuracy = `arg_output=tf.argmax(X['${this.network_output}'],-1);
arg_label=tf.argmax(X['${this.labels}'],-1);
correct_prediction = tf.equal(arg_output, arg_label);
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32));`

      return `N_class=list(X.values())[-1].get_shape().as_list()[-1];
${loss}
${optimizer}
${accuracy}`
    }
  }
}
</script>
