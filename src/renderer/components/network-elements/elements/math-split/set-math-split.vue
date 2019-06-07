<template lang="pug">
  net-base-settings
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.chooseAxis")
          .form_label Choose dimension:
          .form_input
            triple-input(v-model="settings.dimension")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.splitOn")
          .form_label Split on:
          .form_input
            .form_holder
              base-range(
                v-model="settings.val"
              )
            input(type="number" v-model="settings.val")
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
  name: 'SetMathSplit',
  mixins: [mixinSet],
  components: { TripleInput },
  data() {
    return {
      settings: {
        dimension: [0,1,2],
        pooling: false,
        neurons: 'None',
        val: 50
      },
      interactiveInfo: {
        chooseAxis: {
          title: 'Choose axis',
          text: 'Choose which axis to split on.'
        },
        splitOn: {
          title: 'Split on',
          text: 'Choose in which position to split on at the chosen axis'
        },
      }
    }
  },
  methods: {
    showVal(v) {
      console.log(v);
    }
  }
}
</script>
