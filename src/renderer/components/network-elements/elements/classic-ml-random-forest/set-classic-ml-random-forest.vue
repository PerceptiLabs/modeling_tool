<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-update="updateCode"
  )
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
          .form_label Trees:
          .form_input
            input(type="text")
      template(v-if="userMode === 'advanced'")
        .settings-layer_section
          .form_row
            .form_label Split:
            .form_input
              base-radio(group-name="group1" value-input="None" v-model="settings.neurons1")
                span Gini impurity
              base-radio(group-name="group1" value-input="Sigmoid" v-model="settings.neurons1")
                span Information gain
        .settings-layer_section
          .form_row
            .form_label Max depth:
            .form_input
              base-radio(group-name="group2" value-input="None" v-model="settings.neurons2")
                span None
            input(type="number")
        .settings-layer_section
          .form_row
            .form_label Min samples to split node:
            .form_input
              input(type="text")
        .settings-layer_section
          .form_row
            .form_label Min samples in leaf:
            .form_input
              input(type="text")
        .settings-layer_section
          .form_row
            .form_label Max features to split node:
            .form_input
              base-radio(group-name="group2" value-input="None" v-model="settings.neurons3")
                span Auto
              base-radio(group-name="group2" value-input="None1" v-model="settings.neurons3")
                span Log2
            input(type="number")

    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        v-model="coreCode"
      )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetClassicMLRandomForest',
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
  }
}
</script>
