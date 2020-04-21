<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.labels")
          .form_label Labels:
          #tutorial_labels.form_input(data-tutorial-hover-info)
            base-select(
              v-model="settings.Labels"
              :select-options="inputLayers"
            )

    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import TripleInput    from "@/components/base/triple-input";

export default {
  name: 'SetMathSwitch',
  mixins: [mixinSet],
  components: { TripleInput },
  data() {
    return {
      settings: {
        Dim: -1,
      },
      interactiveInfo: {
        dimension: {
          title: 'Dimension',
          text: 'Choose which axis to do the operation on'
        }
      }
    }
  }
}
</script>
