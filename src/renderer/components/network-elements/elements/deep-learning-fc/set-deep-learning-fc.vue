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
              #tutorial_neurons.tutorial-relative.form_input
                input(type="text" v-model="settings.Neurons")
          .settings-layer_section
            .form_row
              .form_label Activation function:
              .form_input
                base-radio(groupName="group1" valueInput="None"  v-model="settings.Activation_function")
                  span None
                base-radio(groupName="group1" valueInput="Sigmoid"  v-model="settings.Activation_function")
                  span Sigmoid
                base-radio(groupName="group1" valueInput="ReLU"  v-model="settings.Activation_function")
                  span ReLU
                base-radio(groupName="group1" valueInput="Tanh"  v-model="settings.Activation_function")
                  span Tanh
          .settings-layer_section
            .form_row
              .form_label Dropout:
              .form_input
                base-radio(groupName="group2" :valueInput="true" v-model="settings.Dropout")
                  span Yes
                base-radio(groupName="group2" :valueInput="false" v-model="settings.Dropout")
                  span No
          //-.settings-layer_section
            .form_row
              .form_label Cost function:
              .form_input
                base-radio(groupName="group2")
                  span Yes
                base-radio(groupName="group2")
                  span No
          //-.settings-layer_section
            .form_row
              .form_label Batch Normalization:
              .form_input
                base-radio(groupName="group3")
                  span Yes
                base-radio(groupName="group3")
                  span No

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
        :the-code="coreCode"
        )
    .settings-layer_foot
      button#tutorial_button-apply.btn.btn--primary(type="button" @click="saveSettings") Apply

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
  import {mapActions}   from 'vuex';

  export default {
    name: 'SetDeepLearningFC',
    mixins: [mixinSet],
    components: {
      SettingsCode
    },
    data() {
      return {
        tabs: ['Settings', 'Code'],
        settings: {
          Neurons :"10",
          Activation_function: "Sigmoid",
          Dropout: false,
        }
      }
    },
    computed: {
      coreCode() {
        let activeFunc = '';
        switch (this.settings.Activation_function) {
          case 'Sigmoid':
            activeFunc = `Y=tf.sigmoid(node);`;
            break;
          case 'ReLU':
            activeFunc = `Y=tf.nn.relu(node);`;
            break;
          case 'Tanh':
            activeFunc = `Y=tf.tanh(node);`;
            break;
          case 'None':
            activeFunc = `Y=node;`;
            break;
        }
        //for element in X.get_shape().as_list()[1:]:
        const fc = `input_size=1
for element in ${this.codeInputDim}:
  input_size*=element
shape=[input_size,${this.settings.Neurons}];
initial = tf.truncated_normal(shape, stddev=0.1);
W=tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Neurons}]);
b=tf.Variable(initial);
flat_node=tf.cast(tf.reshape(X,[-1,input_size]),dtype=tf.float32);
node=tf.matmul(flat_node,W)${this.settings.Dropout ? ';\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
        return `${fc}\n${activeFunc}`
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:    'mod_tutorials/pointActivate',
      }),
      saveSettings() {
        this.applySettings();
        this.tutorialPointActivate({way:'next', validation: 'tutorial_neurons'})
      }
    }
  }
</script>
