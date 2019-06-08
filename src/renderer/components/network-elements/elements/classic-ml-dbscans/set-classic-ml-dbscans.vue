<template lang="pug">
  net-base-settings
    template(slot="Settings-content")
      .settings-layer_section
        .form_row
          .form_label Max sample distance to be in same neighborhood:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row
          .form_label Min samples in neighborhood:
          .form_input
            input(type="text")
      template(v-if="userMode === 'advanced'")
        .settings-layer_section
          .form_row
            .form_label Initialization method:
            .form_input
              base-radio(group-name="group" value-input="None" v-model="settings.neurons")
                span Auto
              base-radio(group-name="group" value-input="Sigmoid" v-model="settings.neurons")
                span Ball tree
              base-radio(group-name="group" value-input="None1" v-model="settings.neurons")
                span KD tree
              base-radio(group-name="group" value-input="Sigmoid2" v-model="settings.neurons")
                span Brute force
        .settings-layer_section
          .form_row
            .form_label Leaf size:
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
  name: 'SetClassicMLDbscans',
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
