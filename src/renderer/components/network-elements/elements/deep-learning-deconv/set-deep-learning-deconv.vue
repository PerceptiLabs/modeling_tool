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
              .form_label Dimension:
              .form_input
                base-radio(groupName="group" valueInput="Automatic" v-model="settings.Deconv_dim")
                  span Automatic
                base-radio(groupName="group" valueInput="1D" v-model="settings.Deconv_dim")
                  span 1D
                base-radio(groupName="group" valueInput="2D" v-model="settings.Deconv_dim")
                  span 2D
                base-radio(groupName="group" valueInput="3D" v-model="settings.Deconv_dim")
                  span 3D
          .settings-layer_section
            .form_row
              .form_label Stride:
              .form_input
                input(type="text" v-model="settings.Stride")
          .settings-layer_section
            .form_row
              .form_label Feature maps:
              .form_input
                input(type="text" v-model="settings.Feature_maps")

          .settings-layer_section
            .form_row
              .form_label Zero-padding:
              .form_input
                base-radio(groupName="group3" valueInput="'SAME'"  v-model="settings.Padding")
                  span SAME
                base-radio(groupName="group3" valueInput="'VALID'"  v-model="settings.Padding")
                  span VALID
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
                base-radio(groupName="group5" :valueInput="false"  v-model="settings.Dropout")
                  span None
                base-radio(groupName="group5" :valueInput="true"  v-model="settings.Dropout")
                  span Sigmoid
          .settings-layer_foot
            button.btn.btn--primary(type="button" @click="applySettings") Apply

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetDeepLearningDeconv',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        Deconv_dim: "2D", //Automatic, 1D, 2D, 3D
        Stride: "2",
        Padding: "'SAME'", //'SAME', 'VALID'
        Feature_maps: "8",
        Activation_function: "Sigmoid", //Sigmoid, ReLU, Tanh, None
        Dropout: false, //True, False
      }
    }
  },
  methods: {

  }
}
</script>
