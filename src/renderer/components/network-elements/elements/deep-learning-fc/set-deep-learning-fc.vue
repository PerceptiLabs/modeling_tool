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
              .form_label Neurons:
              .form_input
                input(type="text" v-model="settings.Neurons")
          .settings-layer_section
            .form_row
              .form_label Activation function:
              .form_input
                base-radio(groupName="group1" valueInput="None"  v-model="settings.Activation_function")
                  span None
                base-radio(groupName="group1" valueInput="Sigmoid"  v-model="settings.Activation_function")
                  span Sigmoid
                base-radio(groupName="group1" valueInput="ReLU"  v-model="settings.Activation_function")
                  span ReLU
                base-radio(groupName="group1" valueInput="Tanh"  v-model="settings.Activation_function")
                  span Tanh
          .settings-layer_section
            .form_row
              .form_label Dropout:
              .form_input
                base-radio(groupName="group2" :valueInput="true" v-model="settings.Dropout")
                  span Yes
                base-radio(groupName="group2" :valueInput="false" v-model="settings.Dropout")
                  span No
          //-.settings-layer_section
            .form_row
              .form_label Cost function:
              .form_input
                base-radio(groupName="group2")
                  span Yes
                base-radio(groupName="group2")
                  span No
          //-.settings-layer_section
            .form_row
              .form_label Batch Normalization:
              .form_input
                base-radio(groupName="group3")
                  span Yes
                base-radio(groupName="group3")
                  span No
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
    name: 'SetDeepLearningFC',
    mixins: [mixinSet],
    components: {
      SettingsCode
    },
    data() {
      return {
        tabs: ['Settings', 'Code'],
        settings: {
          Neurons :"10",
          Activation_function: "Sigmoid",
          Dropout: false,
        }
      }
    }
  }
</script>
