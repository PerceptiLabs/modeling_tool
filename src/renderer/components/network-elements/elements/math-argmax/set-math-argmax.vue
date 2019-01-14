<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
        :disabled="tabSelected != i"
        v-tooltip:right="'ArgMax'"
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
                triple-input(
                  :value1="50"
                  :value2="60"
                  :value3="10"
                  @setValue1="showVal"
                  @setValue2="showVal"
                  @setValue3="showVal"

                )
          .settings-layer_section
          .settings-layer_foot
            button.btn.btn--primary(type="button") Apply


      .popup_body(
        :class="{'active': tabSelected == 1}"
        )
        settings-code

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
        pooling: false,
        neurons: 'None',
        val: 50
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
