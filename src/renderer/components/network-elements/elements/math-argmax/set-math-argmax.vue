<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Dimension:
              .form_input
                input(type="text" v-model="settings.Dim")

          .settings-layer_section
          .settings-layer_foot
            button.btn.btn--primary(type="button"
              @click="applySettings"
              ) Apply


      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
          :the-code="coreCode"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
import TripleInput    from "@/components/base/triple-input";

export default {
  name: 'SetMathArgmax',
  mixins: [mixinSet],
  components: {
    TripleInput,
    SettingsCode,
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        Dim: -1,
      }
    }
  },
  computed: {
    coreCode() {
      return `Y=tf.argmax(X,properties["${this.settings.Dim}"])`
    }
  }
}
</script>
