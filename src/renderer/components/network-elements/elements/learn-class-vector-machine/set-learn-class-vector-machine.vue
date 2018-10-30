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
                base-radio(groupName="group" valueInput="Sigmoid1" v-model="settings.neurons")
                  span Anomalie detection
          template(v-if="userMode === 'advanced'")
            .settings-layer_section
              .form_row
                .form_label Split:
                .form_input
                  base-radio(groupName="group1" valueInput="None" v-model="settings.neurons1")
                    span RBF
                  base-radio(groupName="group1" valueInput="Sigmoid" v-model="settings.neurons1")
                    span Precomputed
                  base-radio(groupName="group1" valueInput="None1" v-model="settings.neurons1")
                    span Linear
                  base-radio(groupName="group1" valueInput="Sigmoid1" v-model="settings.neurons1")
                    span Sigmoid
                  base-radio(groupName="group1" valueInput="Sigmoid11" v-model="settings.neurons1")
                    span Poly
            .settings-layer_section
              .form_row
                .form_label Kernel degree:
                .form_input
                  input(type="text")
            .settings-layer_section
              .form_row
                .form_label Kernel coefficent:
                .form_input
                  base-radio(groupName="group2" valueInput="None" v-model="settings.neurons2")
                    span Auto
                  base-radio(groupName="group2" valueInput="None1" v-model="settings.neurons2")
                    span Scale
            .settings-layer_section
              .form_row
                .form_label Tolerance:
                .form_input
                  input(type="text")
            .settings-layer_section
              .form_row
                .form_label Tolerance:
                .form_input
                  input(type="text")

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
  name: 'SetLearnClassVectorMachine',
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
