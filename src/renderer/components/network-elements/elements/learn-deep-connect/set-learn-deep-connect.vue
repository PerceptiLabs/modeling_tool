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
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Cost function:
              .form_input
                base-radio(groupName="group1")
                  span None
                base-radio(groupName="group1")
                  span Sigmoid
                base-radio(groupName="group1")
                  span ReLu
                base-radio(groupName="group1")
                  span tanh
          .settings-layer_section
            .form_row
              .form_label Cost function:
              .form_input
                base-radio(groupName="group2")
                  span Yes
                base-radio(groupName="group2")
                  span No
          .settings-layer_section
            .form_row
              .form_label Batch Normalization:
              .form_input
                base-radio(groupName="group3")
                  span Yes
                base-radio(groupName="group3")
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
        tabs: ['Settings', 'Code']
      }
    }
  }
</script>
