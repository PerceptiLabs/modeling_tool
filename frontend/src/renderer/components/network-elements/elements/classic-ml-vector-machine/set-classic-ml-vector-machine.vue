<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
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
            base-radio(group-name="group" value-input="Sigmoid1" v-model="settings.neurons")
              span Anomalie detection
      template(v-if="userMode === 'Advanced'")
        .settings-layer_section
          .form_row
            .form_label Split:
            .form_input
              base-radio(group-name="group1" value-input="None" v-model="settings.neurons1")
                span RBF
              base-radio(group-name="group1" value-input="Sigmoid" v-model="settings.neurons1")
                span Precomputed
              base-radio(group-name="group1" value-input="None1" v-model="settings.neurons1")
                span Linear
              base-radio(group-name="group1" value-input="Sigmoid1" v-model="settings.neurons1")
                span Sigmoid
              base-radio(group-name="group1" value-input="Sigmoid11" v-model="settings.neurons1")
                span Poly
        .settings-layer_section
          .form_row
            .form_label Kernel degree:
            .form_input
              input(type="text")
        .settings-layer_section
          .form_row
            .form_label Kernel coefficient:
            .form_input
              base-radio(group-name="group2" value-input="None" v-model="settings.neurons2")
                span Auto
              base-radio(group-name="group2" value-input="None1" v-model="settings.neurons2")
                span Scale
        .settings-layer_section
          .form_row
            .form_label Tolerance:
            .form_input
              input(type="text")
        .settings-layer_section
          .form_row
            .form_label Tolerance:
            .form_input
              input(type="text")

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
  name: 'SetClassicMLSVM',
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
