<template lang="pug">
div
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.convolutionType")
      .form_label Convolution type:
      #tutorial_convolution_type.form_input(data-tutorial-hover-info)
        base-radio(
          group-name="convolutionTypeGroup",
          value-input="Conv",
          v-model="settings.Conv_type"
        )
          span Conv
        base-radio(
          group-name="convolutionTypeGroup",
          value-input="Transpose",
          v-model="settings.Conv_type"
        )
          span Transpose
        base-radio(
          group-name="convolutionTypeGroup",
          value-input="Separable",
          v-model="settings.Conv_type"
        )
          span Separable
        base-radio(
          group-name="convolutionTypeGroup",
          value-input="Depthwise",
          v-model="settings.Conv_type"
        )
          span Depthwise
    .form_row(v-tooltip-interactive:right="interactiveInfo.dimension")
      .form_label Dimension:
      #tutorial_dimension.form_input(data-tutorial-hover-info)
        base-radio(
          v-for="convDimOption in validConvolutionDimOptions",
          :key="convDimOption",
          group-name="group",
          :value-input="convDimOption",
          v-model="settings.Conv_dim"
        )
          span {{ convDimOption }}

  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.patchSize")
      .form_label Patch size:
      #tutorial_patch-size.form_input.tutorial-relative(
        data-tutorial-hover-info
      )
        input(
          type="text",
          v-model="settings.Patch_size",
          ref="pathSize",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.stride")
      .form_label Stride:
      #tutorial_stride.form_input.tutorial-relative(data-tutorial-hover-info)
        input(
          type="text",
          v-model="settings.Stride",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.featureMaps")
      .form_label Feature maps:
      #tutorial_feature-maps.tutorial-relative.form_input(
        data-tutorial-hover-info
      )
        input(
          type="text",
          v-model="settings.Feature_maps",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )

  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.zeroPadding")
      .form_label Zero-padding:
      #tutorial_zero-padding.form_input(data-tutorial-hover-info)
        base-radio(
          group-name="group3",
          value-input="SAME",
          v-model="settings.Padding"
        )
          span SAME
        base-radio(
          group-name="group3",
          value-input="VALID",
          v-model="settings.Padding"
        )
          span VALID
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.activationFunction")
      .form_label Activation function:
      #tutorial_activeFunc.form_input(data-tutorial-hover-info)
        base-radio(
          group-name="group1",
          value-input="None",
          v-model="settings.Activation_function"
        )
          span None
        base-radio(
          group-name="group1",
          value-input="Sigmoid",
          v-model="settings.Activation_function"
        )
          span Sigmoid
        base-radio(
          group-name="group1",
          value-input="ReLU",
          v-model="settings.Activation_function"
        )
          span ReLU
        base-radio(
          group-name="group1",
          value-input="Tanh",
          v-model="settings.Activation_function"
        )
          span Tanh
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.dropout")
      .form_label Dropout:
      #tutorial_dropout.form_input(data-tutorial-hover-info)
        base-radio(
          group-name="group5",
          :value-input="true",
          v-model="settings.Dropout"
        )
          span Yes
        base-radio(
          group-name="group5",
          :value-input="false",
          v-model="settings.Dropout"
        )
          span No
  .settings-layer_section(v-if="settings.Dropout")
    .form_row(v-tooltip-interactive:right="interactiveInfo.pooling")
      .form_label Keep probability:
      .form_input
        input(
          type="number",
          v-model="settings.Keep_prob",
          :class="{ invalid: !isValidKeepProbability }",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.batchNormalization")
      .form_label Batch Normalization:
      .form_input
        base-radio(
          group-name="group4",
          :value-input="true",
          v-model="settings.Batch_norm"
        )
          span Yes
        base-radio(
          group-name="group4",
          :value-input="false",
          v-model="settings.Batch_norm"
        )
          span No
  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.pooling")
      .form_label Pooling:
      #tutorial_pooling.form_input(data-tutorial-hover-info)
        base-radio(
          group-name="group6",
          :value-input="true",
          v-model="settings.PoolBool"
        )
          span Yes
        base-radio(
          group-name="group6",
          :value-input="false",
          v-model="settings.PoolBool"
        )
          span No
  template(v-if="settings.PoolBool")
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.poolingType")
        .form_label Pooling type:
        .form_input
          base-radio(
            group-name="Pooling",
            value-input="Max",
            v-model="settings.Pooling"
          )
            span Max pooling
          base-radio(
            group-name="Pooling",
            value-input="Mean",
            v-model="settings.Pooling"
          )
            span Mean pooling
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.poolingArea")
        .form_label Pooling area:
        .form_input
          input(
            type="text",
            v-model="settings.Pool_area",
            @focus="setIsSettingInputFocused(true)",
            @blur="setIsSettingInputFocused(false)"
          )
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.poolingStride")
        .form_label Pooling stride:
        .form_input
          input(
            type="text",
            v-model="settings.Pool_stride",
            @focus="setIsSettingInputFocused(true)",
            @blur="setIsSettingInputFocused(false)"
          )
    .settings-layer_section
      .form_row(
        v-tooltip-interactive:right="interactiveInfo.ZeroPaddingPooling"
      )
        .form_label Zero-padding for pooling:
        .form_input
          base-radio(
            group-name="Pool_padding",
            value-input="SAME",
            v-model="settings.Pool_padding"
          )
            span SAME
          base-radio(
            group-name="Pool_padding",
            value-input="VALID",
            v-model="settings.Pool_padding"
          )
            span VALID
</template>

<script>
import mixinSet from "@/core/mixins/net-element-settings.js";
import mixinSetValidators from "@/core/mixins/net-element-settings-validators.js";

export default {
  name: "SetDeepLearningConv",
  mixins: [mixinSet, mixinSetValidators],
  mounted() {
    this.saveSettingsToStore("Settings");
  },
  data() {
    return {
      settings: {
        Conv_type: "Conv",
        Conv_dim: "2D", //Automatic, 1D, 2D, 3D
        Patch_size: "3",
        Stride: "2",
        Padding: "SAME", //'SAME', 'VALID'
        Feature_maps: "8",
        Activation_function: "Sigmoid", //Sigmoid, ReLU, Tanh, None
        Dropout: false, //True, False
        Keep_prob: "1",
        Batch_norm: false,
        PoolBool: false, //True, False
        Pooling: "Max", //Max, Mean
        Pool_area: "2",
        Pool_padding: "SAME", //'SAME', 'VALID'
        Pool_stride: "2"
      },
      interactiveInfo: {
        convolutionType: {
          title: "Convolution Type",
          text: "Choose which type of convolutional operation to use"
        },
        dimension: {
          title: "Dimension",
          text: "Choose which type of convolutional operation to use"
        },
        patchSize: {
          title: "Patch size",
          text: "Set the patch size"
        },
        stride: {
          title: "Stride",
          text: "Set the stride"
        },
        featureMaps: {
          title: "Feature maps",
          text: "Set the number of feature maps."
        },
        zeroPadding: {
          title: "Zero-padding",
          text: "Choose to use zero-padding or not."
        },
        activationFunction: {
          title: "Activation function",
          text: "Choose which activation function to use"
        },
        dropout: {
          title: "Dropout",
          text: "Choose if dropout should be used or not"
        },
        batchNormalization: {
          title: "Batch Normalization",
          text: "Choose if batch normalization should be used or not"
        },
        pooling: {
          title: "Pooling",
          text: "Choose if dropout should be used or not"
        },
        poolingType: {
          title: "Pooling type",
          text: "Choose if pooling should be used or not"
        },
        poolingArea: {
          title: "Pooling area",
          text: "Choose pooling area"
        },
        poolingStride: {
          title: "Pooling stride",
          text: "Choose pooling stride"
        },
        ZeroPaddingPooling: {
          title: "Zero-padding",
          text: "Zero-padding for pooling"
        }
      }
    };
  },
  computed: {
    validConvolutionDimOptions() {
      const convType = this.settings.Conv_type;

      if (convType === "Conv") {
        return ["1D", "2D", "3D"];
      } else if (convType === "Transpose") {
        return ["2D", "3D"];
      } else if (convType === "Separable") {
        return ["1D", "2D"];
      } else if (convType === "Depthwise") {
        return ["2D"];
      }
    }
  },
  methods: {
    setIsSettingInputFocused(value) {
      this.$store.commit("mod_workspace/setIsSettingInputFocused", value);
    },
    onFocus(inputId) {},
    onBlur(inputId) {},
    saveSettings(tabName) {
      if (!this.isValidKeepProbability) {
        return;
      }

      this.applySettings(tabName);
    }
  },
  watch: {
    "settings.Conv_type": {
      handler(newVal) {
        // To make sure a valid Conv_dim is always set
        if (
          this.validConvolutionDimOptions &&
          this.validConvolutionDimOptions.length &&
          !this.validConvolutionDimOptions.includes(this.settings.Conv_dim)
        ) {
          this.settings.Conv_dim = this.validConvolutionDimOptions[0];
        }
      }
    }
  }
};
</script>
