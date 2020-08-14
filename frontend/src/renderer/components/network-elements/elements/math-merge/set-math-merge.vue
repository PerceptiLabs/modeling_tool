<template lang="pug">
  div
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.operation")
        .form_label Operation:
        .form_input
          div
            base-radio(group-name="group" value-input="Concat" v-model="settings.Type")
              span Concatenate
            .form_row(v-if="settings.Type == 'Concat' ")
              span Merge dimension
              .form_input
                input(
                  type="number"
                  v-model="settings.Merge_dim"
                  @focus="setIsSettingInputFocused(true)"
                  @blur="setIsSettingInputFocused(false)")
          div
            base-radio(group-name="group" value-input="Sub" v-model="settings.Type")
              span Subtraction
          div
            base-radio(group-name="group" value-input="Add" v-model="settings.Type")
              span Addition
          div
            base-radio(group-name="group" value-input="Multi" v-model="settings.Type")
              span Multiplication
          div
            base-radio(group-name="group" value-input="Div" v-model="settings.Type")
              span Division
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
export default {
  name: 'SetMathSplit',
  mixins: [mixinSet, mixinFocus],
  data() {
    return {
      settings: {
        Type: "Add", //#Add, Sub, Multi, Div, Concat
        Merge_dim: ''
      },
      interactiveInfo: {
        operation: {
          title: 'Operation',
          text: 'Choose which operation to use'
        }
      }
    }
  },
  mounted() {
    this.saveSettingsToStore("Settings");
  },
}
</script>
