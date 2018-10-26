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
              .form_label Deconvolutional dimensions:
              .form_input
                base-radio(groupName="group" valueInput="None" v-model="settings.neurons")
                  span None
                base-radio(groupName="group" valueInput="Sigmoid" v-model="settings.neurons")
                  span Sigmoid
                base-radio(groupName="group" valueInput="ReLu" v-model="settings.neurons")
                  span ReLu
                base-radio(groupName="group" valueInput="tanh" v-model="settings.neurons")
                  span tanh
          .settings-layer_section
            .form_row
              .form_label Stride:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Feature maps:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Zero-padding:
              .form_input
                base-radio(groupName="group3")
                  span Yes
                base-radio(groupName="group3")
                  span No
          .settings-layer_section
            .form_row
              .form_label Activation function:
              .form_input
                base-radio(groupName="group4")
                  span None
                base-radio(groupName="group4")
                  span Sigmoid
                base-radio(groupName="group4")
                  span ReLu
                base-radio(groupName="group4")
                  span tanh
          .settings-layer_section
            .form_row
              .form_label Batch Normalization:
              .form_input
                base-radio(groupName="group6")
                  span Yes
                base-radio(groupName="group6")
                  span No
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
  name: 'SetProcessDeconvolut',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        neurons: 'None'
      }
    }
  },
  methods: {

  }
}
</script>
