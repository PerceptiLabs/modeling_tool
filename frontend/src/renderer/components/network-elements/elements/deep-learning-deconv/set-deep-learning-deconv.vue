<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dimension")
          .form_label Dimension:
          .form_input
            base-radio(group-name="group" value-input="Automatic" v-model="settings.Deconv_dim")
              span Automatic
            base-radio(group-name="group" value-input="1D" v-model="settings.Deconv_dim")
              span 1D
            base-radio(group-name="group" value-input="2D" v-model="settings.Deconv_dim")
              span 2D
            base-radio(group-name="group" value-input="3D" v-model="settings.Deconv_dim")
              span 3D
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.stride")
          .form_label Stride:
          .form_input
            input(type="text" v-model="settings.Stride")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.featureMaps")
          .form_label Feature maps:
          .form_input
            input(type="text" v-model="settings.Feature_maps")

      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.zeroPadding")
          .form_label Zero-padding:
          .form_input
            base-radio(group-name="group3" value-input="'SAME'"  v-model="settings.Padding")
              span SAME
            base-radio(group-name="group3" value-input="'VALID'"  v-model="settings.Padding")
              span VALID
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.activationFunction")
          .form_label Activation function:
          .form_input
            base-radio(group-name="group1" value-input="None"  v-model="settings.Activation_function")
              span None
            base-radio(group-name="group1" value-input="Sigmoid"  v-model="settings.Activation_function")
              span Sigmoid
            base-radio(group-name="group1" value-input="ReLU"  v-model="settings.Activation_function")
              span ReLU
            base-radio(group-name="group1" value-input="Tanh"  v-model="settings.Activation_function")
              span Tanh

      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dropout")
          .form_label Dropout:
          .form_input
            base-radio(group-name="group5" :value-input="true" v-model="settings.Dropout")
              span Yes
            base-radio(group-name="group5" :value-input="false" v-model="settings.Dropout")
              span No

      .settings-layer_section(v-if="settings.Dropout")
        .form_row(v-tooltip-interactive:right="interactiveInfo.pooling")
          .form_label Keep Probability:
          .form_input
            input(type="number" v-model="settings.Keep_prob")

    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetDeepLearningDeconv',
  mixins: [mixinSet],
  data() {
    return {
      settings: {
        Deconv_dim: "2D", //Automatic, 1D, 2D, 3D
        Stride: "2",
        Padding: "'SAME'", //'SAME', 'VALID'
        Feature_maps: "8",
        Activation_function: "Sigmoid", //Sigmoid, ReLU, Tanh, None
        Dropout: false, //True, False
        Keep_prob: '1'
      },
      interactiveInfo: {
        dimension: {
          title: 'Dimension',
          text: 'Choose which type of convolutional </br> operation to use'
        },
        stride: {
          title: 'Stride',
          text: 'Set the stride'
        },
        featureMaps: {
          title: 'Feature maps',
          text: 'Set the number of feature maps.'
        },
        zeroPadding: {
          title: 'Zero-padding',
          text: 'Choose to use zero-padding or not.'
        },
        activationFunction: {
          title: 'Activation function',
          text: 'Choose which activation function to use'
        },
        dropout: {
          title: 'Dropout',
          text: 'Choose if dropout should </br> be used or not'
        }
      },
    }
  },
}
</script>
