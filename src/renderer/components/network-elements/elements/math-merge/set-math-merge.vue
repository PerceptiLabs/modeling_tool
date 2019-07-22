<template lang="pug">
  net-base-settings(
    :layer-code="currentEl.layerCode.length"
    :first-tab="currentEl.layerSettingsTabName"
    @press-apply="saveSettings($event)"
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
      settings-code(v-model="coreCode")

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
    settingsCode() {
      switch (this.settings.Type) {
        case 'Add':
          return `for i in range(0,len(list(X.values())),2):
if not Y:
   Y=list(X.values())[i]
Y=tf. add(list(X.values())[i],Y);`
          break;
        case 'Sub':
          return `for i in range(0,len(list(X.values())),2):
if not Y:
   Y=list(X.values())[i]
Y=tf. subtract(list(X.values())[i],Y);`
          break;
        case 'Multi':
          return `for i in range(0,len(list(X.values())),2):
if not Y:
   Y=list(X.values())[i]
Y=tf.multiply(list(X.values())[i],Y);`
          break;
        case 'Div':
          return `for i in range(0,len(list(X.values())),2):
if not Y:
   Y=list(X.values())[i]
Y=tf.divide(list(X.values())[i],Y);`
          break;
        case 'Concat':
          return `for c in range(0,len(list(X.values())),2):
if not Y:
   Y=c
Y=tf.concat([Y, list(X.values())[c]],${this.settings.Merge_dim});`
          break;
      }
    }
  }
}
</script>
