<template lang="pug">
  net-base-settings
    template(slot="Settings-content")
      .settings-layer_section
        .form_row
          .form_label Dimension:
          .form_input
            input(type="text" v-model="settings.Dim")
    template(slot="Code-content")
      settings-code(:the-code="coreCode")

    template(slot="action")
      button.btn.btn--primary(type="button" @click="applySettings") Apply
</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
//import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
import TripleInput    from "@/components/base/triple-input";

export default {
  name: 'SetMathArgmax',
  mixins: [mixinSet],
  components: { TripleInput },
  data() {
    return {
      settings: {
        Dim: -1,
      }
    }
  },
  computed: {
    coreCode() {
      return `Y=tf.argmax(X,${this.settings.Dim});`
    }
  }
}
</script>
