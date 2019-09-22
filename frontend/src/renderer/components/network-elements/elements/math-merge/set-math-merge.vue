<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
    @press-update="updateCode"
  )
    template(slot="Settings-content")
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
                  input(type="number" v-model="settings.Merge_dim")
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
    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        v-model="coreCode"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetMathSplit',
  mixins: [mixinSet],
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
  computed: {
    codeDefault() {
      let typeCode;
      switch (this.settings.Type) {
        case 'Add':
          typeCode = `for i in range(0,len(list(X['Y'].values())),2):
if not Y:
   Y=list(X['Y'].values())[i]
Y=tf. add(list(X['Y'].values())[i],Y);`
          break;
        case 'Sub':
          typeCode = `for i in range(0,len(list(X['Y'].values())),2):
if not Y:
   Y=list(X['Y'].values())[i]
Y=tf. subtract(list(X['Y'].values())[i],Y);`
          break;
        case 'Multi':
          typeCode = `for i in range(0,len(list(X['Y'].values())),2):
if not Y:
   Y=list(X['Y'].values())[i]
Y=tf.multiply(list(X['Y'].values())[i],Y);`
          break;
        case 'Div':
          typeCode = `for i in range(0,len(list(X['Y'].values())),2):
if not Y:
   Y=list(X['Y'].values())[i]
Y=tf.divide(list(X['Y'].values())[i],Y);`
          break;
        case 'Concat':
          typeCode = `for c in range(0,len(list(X['Y'].values())),2):
if not Y:
   Y=c
Y=tf.concat([Y, list(X['Y'].values())[c]],${this.settings.Merge_dim});`
          break;
      }
      return {
        Output: typeCode
      }
    }
  }
}
</script>
