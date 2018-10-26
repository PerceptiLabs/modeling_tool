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
                base-radio(groupName="group")
                  span None
                base-radio(groupName="group")
                  span Sigmoid
                base-radio(groupName="group")
                  span ReLu
                base-radio(groupName="group")
                  span tanh
          .settings-layer_section
            .form_row
              .form_label Patch size:
              .form_input
                input
          .settings-layer_section
            .form_row
              .form_label Stride:
              .form_input
                input
          .settings-layer_section
            .form_row
              .form_label Feature maps:
              .form_input
                input
          .settings-layer_section
            .form_row
              .form_label Zero-padding for convulution:
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
              .form_label Dropout:
              .form_input
                base-radio(groupName="group5")
                  span None
                base-radio(groupName="group5")
                  span Sigmoid
          .settings-layer_section
            .form_row
              .form_label Batch Normalization:
              .form_input
                base-radio(groupName="group6")
                  span Yes
                base-radio(groupName="group6")
                  span No
          .settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-checkbox(valueInput="Pooling" v-model="settings.pooling")
                //input(type="checkbox" :value="settings.pooling" @change="changeCheckbox($event)")
          template(v-if="settings.pooling")
            .settings-layer_section
              .form_row
                .form_label Pooling type:
                .form_input
                  base-radio(groupName="group7")
                    span Max pooling
                  base-radio(groupName="group7")
                    span Mean pooling
            .settings-layer_section
              .form_row
                .form_label Pooling area:
                .form_input
                  input
            .settings-layer_section
              .form_row
                .form_label Pooling stride:
                .form_input
                  input
            .settings-layer_section
              .form_row
                .form_label Zero-padding for pooling:
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
  name: 'SetProcessCrop',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        pooling: false
      }
    }
  },
  methods: {
    changeCheckbox(ev) {
      console.log('changeCheckbox');
      this.$emit('input', ev.target.value)
    }
  }
}
</script>
