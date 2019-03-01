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
              .form_label Type:
              .form_input
                base-radio(groupName="group" valueInput="None" v-model="settings.neurons")
                  span Classification
                base-radio(groupName="group" valueInput="Sigmoid" v-model="settings.neurons")
                  span Regression
          .settings-layer_section
            .form_row
              .form_label Trees:
              .form_input
                input(type="text")
          template(v-if="userMode === 'advanced'")
            .settings-layer_section
              .form_row
                .form_label Split:
                .form_input
                  base-radio(groupName="group1" valueInput="None" v-model="settings.neurons1")
                    span Gini impurity
                  base-radio(groupName="group1" valueInput="Sigmoid" v-model="settings.neurons1")
                    span Information gain
            .settings-layer_section
              .form_row
                .form_label Max depth:
                .form_input
                  base-radio(groupName="group2" valueInput="None" v-model="settings.neurons2")
                    span None
                input(type="number")
            .settings-layer_section
              .form_row
                .form_label Min samples to split node:
                .form_input
                  input(type="text")
            .settings-layer_section
              .form_row
                .form_label Min samples in leaf:
                .form_input
                  input(type="text")
            .settings-layer_section
              .form_row
                .form_label Max features to split node:
                .form_input
                  base-radio(groupName="group2" valueInput="None" v-model="settings.neurons3")
                    span Auto
                  base-radio(groupName="group2" valueInput="None1" v-model="settings.neurons3")
                    span Log2
                input(type="number")

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
        :the-code="coreCode"
        )
    .settings-layer_foot
      button.btn.btn--primary(type="button" @click="applySettings") Apply

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetClassicMLRandomForest',
  mixins: [mixinSet],
  components: {
    SettingsCode,
  },
  data() {
    return {
      settings: {
        pooling: false,
        neurons: 'None',
        neurons1: 'None',
        neurons2: 'None',
        neurons3: 'None',
        opt: 'None',
        items: ['Data_1', 'Data_2', 'Data_3', 'Data_4', 'Data_5',]
      }
    }
  },
  methods: {

  }
}
</script>
