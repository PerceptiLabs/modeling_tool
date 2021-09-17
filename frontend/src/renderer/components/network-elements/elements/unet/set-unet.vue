<template lang="pug">
  div
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.neurons")
        .form_label Attention:
        .form_input
          base-radio(group-name="attention" :value-input="true"  v-model="settings.attention")
            span Yes
          base-radio(group-name="attention" :value-input="false"  v-model="settings.attention")
            span No
    template(v-if="settings.attention")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.neurons")
          .form_label Attention Type:
          .form_input
            .form_input(data-tutorial-hover-info)
              base-radio(group-name="atten_type" :value-input="'add'"  v-model="settings.atten_type")
                span add
              base-radio(group-name="atten_type" :value-input="'multiply'"  v-model="settings.atten_type")
                span multiply
      .settings-layer_section
        .form_row
          .form_label Attention Activation:
          .form_input(data-tutorial-hover-info)
            base-radio(group-name="atten_activation" value-input="ReLU"  v-model="settings.atten_activation")
              span Relu
            base-radio(group-name="atten_activation" value-input="Softmax"  v-model="settings.atten_activation")
              span Softmax
            base-radio(group-name="atten_activation" value-input="LeakyReLU"  v-model="settings.atten_activation")
              span Leaky ReLu
            base-radio(group-name="atten_activation" value-input="Snake"  v-model="settings.atten_activation")
              span Snake
            base-radio(group-name="atten_activation" value-input="GELU"  v-model="settings.atten_activation")
              span Gelu
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.neurons")
        .form_label N labels:
        .form_input
          input(
            type="number"
            v-model="settings.n_labels"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.neurons")
        .form_label Stack num down:
        .form_input
          input(
            type="number"
            v-model="settings.stack_num_down"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.neurons")
        .form_label Stack num up:
        .form_input
          input(
            type="number"
            v-model="settings.stack_num_up"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label Activation:
        .form_input(data-tutorial-hover-info)
          base-radio(group-name="activation" value-input="ReLU"  v-model="settings.activation")
            span Relu
          base-radio(group-name="activation" value-input="Softmax"  v-model="settings.activation")
            span Softmax
          base-radio(group-name="activation" value-input="LeakyReLU"  v-model="settings.activation")
            span Leaky ReLu
          base-radio(group-name="activation" value-input="Snake"  v-model="settings.activation")
            span Snake
          base-radio(group-name="activation" value-input="GELU"  v-model="settings.activation")
            span Gelu
    .settings-layer_section
      .form_row
        .form_label Output Activation:
        .form_input(data-tutorial-hover-info)
          base-radio(group-name="output_activation" :value-input="false"  v-model="settings.output_activation")
            span None
          base-radio(group-name="output_activation" value-input="Softmax"  v-model="settings.output_activation")
            span Softmax
          base-radio(group-name="output_activation" value-input="ReLU"  v-model="settings.output_activation")
            span Relu
          base-radio(group-name="output_activation" value-input="LeakyReLU"  v-model="settings.output_activation")
            span Leaky ReLu
          base-radio(group-name="output_activation" value-input="Sigmoid"  v-model="settings.output_activation")
            span Sigmoid
    .settings-layer_section
      .form_row
        .form_label Batch Normalization:
        .form_input
          base-radio(group-name="batch_norm" :value-input="true" v-model="settings.batch_norm")
            span Yes
          base-radio(group-name="batch_norm" :value-input="false" v-model="settings.batch_norm")
            span No
    .settings-layer_section
      .form_row
        .form_label Pool:
        .form_input(data-tutorial-hover-info)
          base-radio(group-name="pool" :value-input="false"  v-model="settings.pool")
            span None
          base-radio(group-name="pool" value-input="max"  v-model="settings.pool")
            span Max
          base-radio(group-name="pool" value-input="ave"  v-model="settings.pool")
            span Avg
    .settings-layer_section
      .form_row
        .form_label Unpool:
        .form_input(data-tutorial-hover-info)
          base-radio(group-name="unpool" :value-input="false"  v-model="settings.unpool")
            span None
          base-radio(group-name="unpool" value-input="bilinear"  v-model="settings.unpool")
            span Bilinear
          base-radio(group-name="unpool" value-input="nearest"  v-model="settings.unpool")
            span Nearest
    .settings-layer_section
      .form_row
        .form_label Backbone:
        .form_input(data-tutorial-hover-info)
          base-select(
            selectPlaceholder="None"
            v-model="settings.backbone"
            :select-options="backboneOptions"
          )
    template(v-if="settings.backbone !== false")
      .settings-layer_section
        .form_row
          .form_label Backbone weights:
          .form_input
            base-radio(group-name="backbone_weights" :value-input="true" v-model="settings.backbone_weights")
              span Yes
            base-radio(group-name="backbone_weights" :value-input="false" v-model="settings.backbone_weights")
              span No
      .settings-layer_section
        .form_row
          .form_label Freeze backbone:
          .form_input
            base-radio(group-name="freeze_backbone" :value-input="true" v-model="settings.freeze_backbone")
              span Yes
            base-radio(group-name="freeze_backbone" :value-input="false" v-model="settings.freeze_backbone")
              span No
      .settings-layer_section
        .form_row
          .form_label Freeze batch normal:
          .form_input
            base-radio(group-name="freeze_batch_norm" :value-input="true" v-model="settings.freeze_batch_norm")
              span Yes
            base-radio(group-name="freeze_batch_norm" :value-input="false" v-model="settings.freeze_batch_norm")
              span No
</template>

<script>
import mixinSet           from '@/core/mixins/net-element-settings.js';
import mixinSetValidators from '@/core/mixins/net-element-settings-validators.js';

import { mapGetters, mapActions } from 'vuex';
import isEqual from 'lodash.isequal';
import {isEnvDataWizardEnabled} from "@/core/helpers";

export default {
  name: 'SetUnet',
  mixins: [mixinSet, mixinSetValidators],
  mounted() {
    this.saveSettingsToStore("Settings");
  },
  watch: {
    'settings.backbone': {
      handler(currentValue) {
        if (currentValue === null) {
          this.settings.backbone = false;
        };
      },
    },
  },
  data() {
    return {
      backboneOptions: [
        {text: 'None', value: false },
        {text: 'VGG16', value: 'VGG16'},
        {text: 'VGG19', value: 'VGG19'},
        {text: 'ResNet50', value: 'ResNet50'},
        {text: 'ResNet101', value: 'ResNet101'},
        {text: 'ResNet152', value: 'ResNet152'},
        {text: 'ResNet50V2', value: 'ResNet50V2'},
        {text: 'ResNet101V2', value: 'ResNet101V2'},
        {text: 'ResNet152V2', value: 'ResNet152V2'},
        {text: 'DenseNet121', value: 'DenseNet121'},
        {text: 'DenseNet169', value: 'DenseNet169'},
        {text: 'DenseNet201', value: 'DenseNet201'},
        {text: 'EfficientNetB0', value: 'EfficientNetB0'},
        {text: 'EfficientNetB1', value: 'EfficientNetB1'},
        {text: 'EfficientNetB2', value: 'EfficientNetB2'},
        {text: 'EfficientNetB3', value: 'EfficientNetB3'},
        {text: 'EfficientNetB4', value: 'EfficientNetB4'},
        {text: 'EfficientNetB5', value: 'EfficientNetB5'},
        {text: 'EfficientNetB6', value: 'EfficientNetB6'},
        {text: 'EfficientNetB7', value: 'EfficientNetB7'},
      ],
      settings: {
        filter_num:[64, 128, 256, 512],
        n_labels: 1,
        stack_num_down: 2,
        stack_num_up: 2,
        activation: 'ReLU',
        output_activation: 'Softmax',
        batch_norm: false,
        pool: 'max',
        unpool: 'bilinear',
        backbone: false,
        backbone_weights: true,
        freeze_backbone: true,
        freeze_batch_norm: true,
        attention: false, //  bool
        atten_activation: 'ReLU',
        atten_type: 'add', // add | multiply
      },
      interactiveInfo: {
        convolutionType: {
          title: 'Convolution Type',
          text: 'Choose which type of convolutional operation to use'
        },
        dimension: {
          title: 'Dimension',
          text: 'Choose which type of convolutional operation to use'
        },
        patchSize: {
          title: 'Patch size',
          text: 'Set the patch size'
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
          text: 'Choose if dropout should be used or not'
        },
        batchNormalization: {
          title: 'Batch Normalization',
          text: 'Choose if batch normalization should be used or not'
        },
        pooling: {
          title: 'Pooling',
          text: 'Choose if dropout should be used or not'
        },
        poolingType: {
          title: 'Pooling type',
          text: 'Choose if pooling should be used or not'
        },
        poolingArea: {
          title: 'Pooling area',
          text: 'Choose pooling area'
        },
        poolingStride: {
          title: 'Pooling stride',
          text: 'Choose pooling stride'
        },
        ZeroPaddingPooling: {
          title: 'Zero-padding',
          text: 'Zero-padding for pooling'
        }
      },
    }
  },
  methods: {
    setIsSettingInputFocused(value) {
      this.$store.commit("mod_workspace/setIsSettingInputFocused", value);
    },
    saveSettings(tabName) {
      if (!this.isValidKeepProbability) { return; }

      this.applySettings(tabName);
    },
  },
}
</script>
