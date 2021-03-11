<template lang="pug">
  div
    .settings-layer_section
      .form_row
        .form_label Include top:
        .form_input
          base-radio(group-name="include_top" :value-input="true"  v-model="settings.include_top")
            span Yes
          base-radio(group-name="include_top" :value-input="false"  v-model="settings.include_top")
            span No

    .settings-layer_section(v-if="includeTopFalse")
      .form_row
        .form_label Pooling:
        .form_input
          base-radio(group-name="pooling" :value-input="'None'" v-model="settings.pooling")
            span None
          base-radio(group-name="pooling" :value-input="'avg'" v-model="settings.pooling")
            span avg
          base-radio(group-name="pooling" :value-input="'max'" v-model="settings.pooling")
            span max

    .settings-layer_section
      .form_row
        .form_label Trainable:
        .form_input
          base-radio(group-name="trainable" :value-input="true"  v-model="settings.trainable")
            span Yes
          base-radio(group-name="trainable" :value-input="false"  v-model="settings.trainable")
            span No

    .settings-layer_section(v-if="includeTopTrueNoWeights")
      .form_row
        .form_label Alpha:
        .form_input
          input(
            type="number"
            v-model="settings.alpha"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")

    .settings-layer_section(v-if="includeTopTrueNoWeights")
      .form_row
        .form_label Classes:
        .form_input
          input(
            type="number"
            v-model="settings.classes"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")

    .settings-layer_section
      .form_row
        .form_label Weights:
        .form_input
          base-radio(group-name="weights" value-input="None" v-model="settings.weights")
            span None
          base-radio(group-name="weights" value-input="imagenet" v-model="settings.weights")
            span imagenet

</template>

<script>
  import mixinSet           from '@/core/mixins/net-element-settings.js';
  import mixinSetValidators from '@/core/mixins/net-element-settings-validators.js';

  export default {
    name: 'SetPreTrainedMobileNetV2',
    mixins: [mixinSet, mixinSetValidators],
    data() {
      return {
        showPreview: false,
        settings: {
          include_top: false,
          trainable: false,
          pooling: 'None',
          classes: 0,
          weights: 'imagenet',
          alpha: '1',
          classifier_activation: 'softmax'
        },
        interactiveInfo: {},
      }
    },
    mounted() {
      this.saveSettingsToStore("Settings");
    },
    methods: {
      saveSettings(tabName) {
        if (this.settings.alpha < 0 || this.settings.alpha > 1) { return; }

        this.applySettings(tabName);
      },
      setIsSettingInputFocused(value) {
        this.$store.commit("mod_workspace/setIsSettingInputFocused", value);
      },
    },
    computed: {
      includeTopTrueNoWeights() {
        return this.settings.include_top && this.settings.weights === 'None';
      },
      includeTopFalse() {
        return !this.settings.include_top;
      }
    }
  }
</script>
