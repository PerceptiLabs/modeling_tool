<template lang="pug">
  net-base-settings
    template(slot="Settings-content")
      .settings-layer_section
        .form_row
          .form_label Type:
          .form_input
            base-radio(group-name="group" value-input="None" v-model="settings.neurons")
              span Classification
            base-radio(group-name="group" value-input="Sigmoid" v-model="settings.neurons")
              span Regression
      .settings-layer_section
        .form_row
          .form_label Neighbors:
          .form_input
            input(type="text")
      template(v-if="userMode === 'advanced'")
        .settings-layer_section
          .form_row
            .form_label Weights:
            .form_input
              base-radio(group-name="group1" value-input="None" v-model="settings.neurons1")
                span Uniform
              base-radio(group-name="group1" value-input="Sigmoid" v-model="settings.neurons1")
                span Distance
        .settings-layer_section
          .form_row
            .form_label Algorithm:
            .form_input
              base-radio(group-name="group2" value-input="None" v-model="settings.neurons2")
                span Auto
              base-radio(group-name="group2" value-input="Sigmoid" v-model="settings.neurons2")
                span Ball tree
              base-radio(group-name="group2" value-input="None1" v-model="settings.neurons2")
                span KD tree
              base-radio(group-name="group2" value-input="Sigmoid1" v-model="settings.neurons2")
                span Brute force
        .settings-layer_section
          .form_row
            .form_label Leaf size:
            .form_input
              input(type="text")
        .settings-layer_section
          .form_row
            .form_label Weights:
            .form_input
              base-radio(group-name="group3" value-input="None" v-model="settings.neurons3")
                span Minkowski
              base-radio(group-name="group3" value-input="Sigmoid" v-model="settings.neurons3")
                span Euclidean

    template(slot="Code-content")
      settings-code(:the-code="coreCode")

    template(slot="action")
      button.btn.btn--primary(type="button" @click="applySettings") Apply

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetClassicMLKNN',
  mixins: [mixinSet],
  data() {
    return {
      settings: {
        pooling: false,
        neurons: 'None',
        neurons1: 'None',
        neurons2: 'None',
        neurons3: 'None',
        opt: 'None',
        items: ['Data_1', 'Data_2', 'Data_3', 'Data_4', 'Data_5',]
      }
    }
  },
}
</script>
