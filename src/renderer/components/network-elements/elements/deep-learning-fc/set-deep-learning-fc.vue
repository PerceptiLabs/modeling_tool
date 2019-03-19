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
              .form_input(id="tutorial_neurons" class="tutorial-relative")
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
          .settings-layer_foot
            button.btn.btn--primary(type="button"
              @click="saveSettings"
              id="tutorial_button-apply"
            ) Apply



      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
        :the-code="coreCode"
        )

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
        return `
        input_size=1
	        for element in X.get_shape().as_list()[1:]:
            input_size*=element
        shape=[input_size,${this.settings.Neurons}];
        initial = tf.truncated_normal(shape, stddev=0.1);
        W=tf.Variable(initial);
        initial = tf.constant(0.1, shape=[${this.settings.Neurons}]);
        b=tf.Variable(initial);
        flat_node=tf.cast(tf.reshape(X,[-1,input_size]),dtype=tf.float32);
        node=tf.matmul(flat_node,W);
        node=tf.nn.dropout(node,keep_prob);
        node=node+b
        `
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:    'mod_tutorials/pointActivate',
      }),
      saveSettings() {
        this.applySettings()
        this.tutorialPointActivate({way:'next', validation: 'tutorial_neurons'})
      }
    }
  }
</script>
