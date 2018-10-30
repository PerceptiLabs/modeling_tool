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
              .form_label Neurons:
              .form_input
                div
                  base-radio(groupName="group" valueInput="Concantenate" v-model="settings.neurons")
                    span Concantenate
                  .form_row(v-if="settings.neurons == 'Concantenate' ")
                    span Merge dimensions
                    .form_input
                      input(type="number")
                div
                  base-radio(groupName="group" valueInput="Substractions" v-model="settings.neurons")
                    span Substractions
                div
                  base-radio(groupName="group" valueInput="Addition" v-model="settings.neurons")
                    span Addition
                div
                  base-radio(groupName="group" valueInput="Multiplication" v-model="settings.neurons")
                    span Multiplication
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

export default {
  name: 'SetMathSplit',
  mixins: [mixinSet],
  components: {
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
