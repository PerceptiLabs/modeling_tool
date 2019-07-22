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
          #tutorial_neurons.tutorial-relative.form_input(data-tutorial-hover-info)
            input(type="text" v-model="settings.Neurons")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.activationFunction")
          .form_label Activation function:
          #tutorial_activation_function.form_input(data-tutorial-hover-info)
            base-radio(group-name="group1" value-input="None"  v-model="settings.Activation_function")
              span None
            base-radio(group-name="group1" value-input="Sigmoid"  v-model="settings.Activation_function")
              span Sigmoid
            base-radio(group-name="group1" value-input="ReLU"  v-model="settings.Activation_function")
              span ReLU
            base-radio(group-name="group1" value-input="Tanh"  v-model="settings.Activation_function")
              span Tanh
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dropout")
          .form_label Dropout:
          #tutorial_dropout.form_input(data-tutorial-hover-info)
            base-radio(group-name="group2" :value-input="true" v-model="settings.Dropout")
              span Yes
            base-radio(group-name="group2" :value-input="false" v-model="settings.Dropout")
              span No

    template(slot="Code-content")
      settings-code(v-model="coreCode")

    template(slot="action")
      button#tutorial_button-apply.btn.btn--primary(type="button" @click="saveSettings") Apply

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
  import NetBaseSettings  from '@/components/network-elements/net-base-settings/net-base-settings.vue';
  import {mapGetters, mapActions}   from 'vuex';

  export default {
    name: 'SetDeepLearningFC',
    mixins: [mixinSet],
    components: { SettingsCode, NetBaseSettings },
    data() {
      return {
        settings: {
          Neurons :"10",
          Activation_function: "Sigmoid",
          Dropout: false,
        },
        interactiveInfo: {
          neurons: {
            title: 'Neurons',
            text: 'Set how many neurons to use'
          },
          activationFunction: {
            title: 'Activation function',
            text: 'Choose activation function for each neuron'
          },
          dropout: {
            title: 'Dropout',
            text: 'Choose if dropout should be used or not'
          }
        },
      }
    },
    computed: {
      ...mapGetters({
        isTutorialMode: 'mod_tutorials/getIstutorialMode'
      }),
      settingsCode() {
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
    watch: {
      'settings.Neurons': {
        handler() {
          if(this.isTutorialMode) {
            this.settings.Neurons = 10;
            this.popupInfo("While the value of this field should be 10. But soon you will be able to set a different number of neurons. We are working on it");
          }
        }
      },
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:   'mod_tutorials/pointActivate',
        popupInfo:               'globalView/GP_infoPopup'
      }),
      saveSettings(tabName) {
        this.applySettings(tabName);
        this.tutorialPointActivate({way:'next', validation: 'tutorial_neurons'})
      }
    }
  }
</script>
