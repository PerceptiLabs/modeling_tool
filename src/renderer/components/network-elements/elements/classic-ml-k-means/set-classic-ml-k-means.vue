<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
    @press-update="updateCode"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row
          .form_label Clusters:
          .form_input
            input(type="text")
      template(v-if="userMode === 'advanced'")
        .settings-layer_section
          .form_row
            .form_label Max iterations:
            .form_input
              input(type="text")
        .settings-layer_section
          .form_row
            .form_label Method:
            .form_input
              base-radio(group-name="group" value-input="None" v-model="settings.neurons")
                span Kmeans++
              base-radio(group-name="group" value-input="Sigmoid" v-model="settings.neurons")
                span Random
        .settings-layer_section
          .form_row
            .form_label Initialization iteractions:
            .form_input
              input(type="text")
        .settings-layer_section
          .form_row
            .form_label Convergence tolerance:
            .form_input
              input(type="text")
    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        v-model="coreCode"
      )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetClassicMLKMeans',
  mixins: [mixinSet],
  data() {
    return {
      settings: {
        pooling: false,
        neurons: 'None',
        opt: 'None',
        items: ['Data_1', 'Data_2', 'Data_3', 'Data_4', 'Data_5',]
      }
    }
  },
}
</script>
