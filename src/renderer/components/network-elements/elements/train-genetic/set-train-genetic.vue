<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-update="updateCode"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.population")
          .form_label Population:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.generations")
          .form_label Generations:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.retain")
          .form_label Retain:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.randomSelect")
          .form_label Random select:
          .form_input
            input(type="text")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.mutateChance")
          .form_label Mutate chance:
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
  name: 'SetTrainGenetic',
  mixins: [mixinSet],
  data() {
    return {
      settings: {
        pooling: false,
        neurons: 'None',
        opt: 'None',
        items: ['Data_1', 'Data_2', 'Data_3', 'Data_4', 'Data_5',]
      },
      interactiveInfo: {
        population: {
          title: 'Population',
          text: ''
        },
        generations: {
          title: 'Generations',
          text: ''
        },
        retain: {
          title: 'Retain',
          text: ''
        },
        randomSelect: {
          title: 'Random select',
          text: ''
        },
        mutateChance: {
          title: 'Learning rate',
          text: ''
        }
      }
    }
  },
}
</script>
