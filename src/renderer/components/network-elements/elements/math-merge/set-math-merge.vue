<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      :disabled="tabSelected != i"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Operation:
              .form_input
                div
                  base-radio(groupName="group" valueInput="Concat" v-model="settings.Type")
                    span Concatenate
                  .form_row(v-if="settings.Type == 'Concat' ")
                    span Merge dimension
                    .form_input
                      input(type="number" v-model="settings.Merge_dim")
                div
                  base-radio(groupName="group" valueInput="Sub" v-model="settings.Type")
                    span Subtraction
                div
                  base-radio(groupName="group" valueInput="Add" v-model="settings.Type")
                    span Addition
                div
                  base-radio(groupName="group" valueInput="Multi" v-model="settings.Type")
                    span Multiplication
                div
                  base-radio(groupName="group" valueInput="Div" v-model="settings.Type")
                    span Division
          .settings-layer_section

          .settings-layer_foot
            button.btn.btn--primary(type="button"
            @click="applySettings"
            ) Apply


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
        Type:"Add", //#Add, Sub, Multi, Div, Concat
        Merge_dim: ''
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
