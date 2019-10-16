<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dimension")
          .form_label Dimension:
          .form_input
            input(type="text" v-model="settings.Dim")
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
  name: 'SetMathArgmax',
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
