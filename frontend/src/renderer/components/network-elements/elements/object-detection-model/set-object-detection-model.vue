<template lang="pug">
div
  .settings-layer_section
  .settings-layer_section(v-if="settings.source === 'Local'")
    button.btn.btn--secondary(type="button", @click="openFilePicker()")
      i.icon.icon-open-file
      span Load Model Folder

  .settings-layer_section(v-if="settings.source === 'URL'")
    .form_row(v-tooltip-interactive:right="interactiveInfo.url")
      .form_label URL:
      .form_input
        input(
          type="text",
          v-model="settings.url",
          @focus="setIsSettingInputFocused(true)",
          @blur="setIsSettingInputFocused(false)"
        )

  .settings-layer_section
    .form_row(v-tooltip-interactive:right="interactiveInfo.trainable")
      .form_label Trainable:
      #tutorial_trainable.form_input(data-tutorial-hover-info)
        base-radio(
          group-name="trainableGroup",
          :value-input="true",
          v-model="settings.trainable"
        )
          span Yes
        base-radio(
          group-name="trainableGroup",
          :value-input="false",
          v-model="settings.trainable"
        )
          span No
</template>

<script>
import mixinSet from "@/core/mixins/net-element-settings.js";
import mixinSetValidators from "@/core/mixins/net-element-settings-validators.js";
import { pickDirectory as rygg_pickDirectory } from "@/core/apiRygg";

export default {
  name: "SetLayerObjectDetectionModel",
  mixins: [mixinSet, mixinSetValidators],
  data() {
    return {
      showPreview: false,
      settings: {
        source: "URL",
        url: "https://tfhub.dev/tensorflow/efficientdet/d2/1",
        path: "",
        trainable: false,
      },
      interactiveInfo: {
        source: {
          title: "Source",
          text: "Source",
        },
        url: {
          title: "URL",
          text: "URL",
        },
        trainable: {
          title: "Trainable",
          text: "Trainable",
        },
      },
    };
  },
  mounted() {
    this.saveSettingsToStore("Settings");
  },
  methods: {
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
    setIsSettingInputFocused(value) {
      this.$store.commit("mod_workspace/setIsSettingInputFocused", value);
    },
    async openFilePicker() {
      const selectedPath = await rygg_pickDirectory("Choose model to load");
      if (selectedPath && selectedPath.path) {
        this.path = selectedPath.path;
      }
    },
  },
  computed: {},
};
</script>
