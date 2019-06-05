<template lang="pug">
  net-base-settings
    template(slot="Settings-content")
      .settings-layer_section
        .form_row
          .form_label Population:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row
          .form_label Generations:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row
          .form_label Retain:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row
          .form_label Random select:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row
          .form_label Mutate chance:
          .form_input
            input(type="text")
    template(slot="Code-content")
      settings-code(:the-code="coreCode")

    template(slot="action")
      button.btn.btn--primary(type="button" @click="applySettings") Apply
</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetTrainGenetic',
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
  methods: {

  }
}
</script>
