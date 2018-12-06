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
      .popup_body(:class="{'active': tabSelected == 0}")
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Dimension:
              .form_input
                base-radio(groupName="group" valueInput="Automatic" v-model="settings.Conv_dim")
                  span Automatic
                base-radio(groupName="group" valueInput="1D" v-model="settings.Conv_dim")
                  span 1D
                base-radio(groupName="group" valueInput="2D" v-model="settings.Conv_dim")
                  span 2D
                base-radio(groupName="group" valueInput="3D" v-model="settings.Conv_dim")
                  span 3D
          .settings-layer_section
            .form_row
              .form_label Patch size:
              .form_input
                input(type="text" v-model="settings.Patch_size")
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
                base-radio(groupName="group3" valueInput="SAME"  v-model="settings.Padding")
                  span SAME
                base-radio(groupName="group3" valueInput="VALID"  v-model="settings.Padding")
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
          .settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-radio(groupName="group6" :valueInput="true"  v-model="settings.PoolBool")
                  span Yes
                base-radio(groupName="group6" :valueInput="false"  v-model="settings.PoolBool")
                  span No
          //-.settings-layer_section
            .form_row
              .form_label Batch Normalization:
              .form_input
                base-radio(groupName="group6")
                  span Yes
                base-radio(groupName="group6")
                  span No
          //-.settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-checkbox(valueInput="Pooling" v-model="settings.pooling")
                //input(type="checkbox" :value="settings.pooling" @change="changeCheckbox($event)")
          template(v-if="settings.PoolBool")
            .settings-layer_section
              .form_row
                .form_label Pooling type:
                .form_input
                  base-radio(groupName="Pooling" valueInput="Max"  v-model="settings.Pooling")
                    span Max pooling
                  base-radio(groupName="Pooling" valueInput="Mean"  v-model="settings.Pooling")
                    span Mean pooling
            .settings-layer_section
              .form_row
                .form_label Pooling area:
                .form_input
                  input(type="text" v-model="settings.Pool_area")
            .settings-layer_section
              .form_row
                .form_label Pooling stride:
                .form_input
                  input(type="text" v-model="settings.Pool_stride")
            .settings-layer_section
              .form_row
                .form_label Zero-padding for pooling:
                .form_input
                  base-radio(groupName="Pool_padding" valueInput="SAME" v-model="settings.Pool_padding")
                    span SAME
                  base-radio(groupName="Pool_padding" valueInput="VALID" v-model="settings.Pool_padding")
                    span VALID

          .settings-layer_foot
            button.btn.btn--primary(type="button" @click="applySettings") Apply

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetDeepLearningConv',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        Conv_dim: "2D", //Automatic, 1D, 2D, 3D
        Patch_size: "3",
        Stride: "2",
        Padding: "SAME", //'SAME', 'VALID'
        Feature_maps: "8",
        Activation_function: "Sigmoid", //Sigmoid, ReLU, Tanh, None
        Dropout: false, //True, False
        PoolBool: false, //True, False
        Pooling: "Max", //Max, Mean
        Pool_area: "2",
        Pool_padding: "SAME", //'SAME', 'VALID'
        Pool_stride: "2",
      }
    }
  },
  methods: {

  }
}
</script>
