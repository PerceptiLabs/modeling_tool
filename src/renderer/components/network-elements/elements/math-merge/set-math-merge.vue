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


      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
          :the-code="coreCode"
        )

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
  },
  computed: {
    coreCode() {
      switch (this.settings.Type) {
        case 'Add':
          return `for i in range(0,len(list(X.values())),2):
                    if not Y:
                       Y=list(X.values())[i]
                    Y=tf. add(list(X.values())[i],Y)`
          break;
        case 'Sub':
          return `for i in range(0,len(list(X.values())),2):
                    if not Y:
                       Y=list(X.values())[i]
                    Y=tf. subtract(list(X.values())[i],Y)`
          break;
        case 'Multi':
          return `for i in range(0,len(list(X.values())),2):
                  if not Y:
                     Y=list(X.values())[i]
                  Y=tf.multiply(list(X.values())[i],Y)`
          break;
        case 'Div':
          return `for i in range(0,len(list(X.values())),2):
                    if not Y:
                       Y=list(X.values())[i]
                    Y=tf.divide(list(X.values())[i],Y)`
          break;
        case 'Concat':
          return `for c in range(0,len(list(X.values())),2):
                    if not Y:
                       Y=c
                    Y=tf.concat([Y, list(X.values())[c]],properties["${this.settings.Merge_dim}"])`
          break;
      }
    }
  }
}
</script>
