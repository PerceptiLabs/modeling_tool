<template lang="pug">
  div
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.dimension")
        .form_label Dimension:
        .form_input
          input(
            type="text"
            v-model="settings.Dim"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    //- template(slot="Code-content")
    //-   settings-code(
    //-     :current-el="currentEl"
    //-     :el-settings="settings"
    //-     v-model="coreCode"
    //-   )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
import TripleInput    from "@/components/base/triple-input";

export default {
  name: 'SetMathArgmax',
  mixins: [mixinSet, mixinFocus],
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
  },
  mounted() {
    this.saveSettingsToStore("Settings");
  },
}
</script>
