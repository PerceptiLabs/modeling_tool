<template lang="pug">
.sidebar-setting-wrapper
  .sidebar-setting-head(
    v-if="selectedEl !== null",
  )
    .component-name {{componentTypeToName[selectedEl.componentName]}}
    sidebar-auto-setting-info(
      :key="selectedEl.layerId",
      :selectedEl="selectedEl"
    )
  perfect-scrollbar.sidebar-setting-content(
    :data-tutorial-target="'tutorial-workspace-settings'",
    ref="sidebarSettingWrapper",
  )    
    sidebar-locked-settings-wrapper(:selectedEl="selectedEl")
      component.setting-values-wrapper(
        v-if="selectedEl !== null",
        :key="selectedEl.layerId",
        v-bind:is="selectedEl.componentName",
        :currentEl="selectedEl",
        ref="componentSettings"
      )

  sidebar-setting-preview.setting-chart-wrapper(
    v-if="selectedEl !== null",
    :current-el="selectedEl"
  )

  .sidebar-setting-actions
    button.btn.btn--primary(
      v-if="shouldShowOpenCodeBtn",
      @click="onOpenCodeButtonClick()"
    ) 
      img(src="/static/img/code.svg")
      | Open Code &nbsp;

    div(
      v-tooltip:bottom="'Coming Soon'"
    )
      button.btn.btn--primary(
        v-if="shouldShowOpenCodeBtn",
        disabled
      ) 
        img(src="/static/img/save.svg")
        | Save &nbsp;

  button.btn.btn--outline-primary.reset-component-btn(
    v-if="shouldShowResetComponentBtn",
    @click="resetComponentSettings"
  ) Reset Component
</template>
<script>
import DeepLearningFC from "@/components/network-elements/elements/deep-learning-fc/set-deep-learning-fc.vue";
import DeepLearningConv from "@/components/network-elements/elements/deep-learning-conv/set-deep-learning-conv.vue";
import DeepLearningRecurrent from "@/components/network-elements/elements/deep-learning-recurrent/set-deep-learning-recurrent.vue";

import ProcessEmbed from "@/components/network-elements/elements/process-embed/set-process-embed.vue";
import ProcessGrayscale from "@/components/network-elements/elements/process-grayscale/set-process-grayscale.vue";
import ProcessOneHot from "@/components/network-elements/elements/process-one-hot/set-process-one-hot.vue";
import ProcessReshape from "@/components/network-elements/elements/process-reshape/set-process-reshape.vue";
import ProcessRescale from "@/components/network-elements/elements/process-rescale/set-process-rescale.vue";

import MathArgmax from "@/components/network-elements/elements/math-argmax/set-math-argmax.vue";
import MathMerge from "@/components/network-elements/elements/math-merge/set-math-merge.vue";

import TrainNormal from "@/components/network-elements/elements/train-normal/set-train-normal.vue";
import TrainRegression from "@/components/network-elements/elements/train-regression/set-train-regression.vue";
import TrainReinforce from "@/components/network-elements/elements/train-reinforce/set-train-reinforce.vue";
import TrainGan from "@/components/network-elements/elements/train-gan/set-train-gan.vue";
import TrainDetector from "@/components/network-elements/elements/train-detector/set-train-detector.vue";

import LayerCustom from "@/components/network-elements/elements/layer-custom/set-layer-custom.vue";

import LayerTfModel from "@/components/network-elements/elements/tensorflow-model/set-tensorflow-model.vue";
import PreTrainedVGG16 from "@/components/network-elements/elements/pretrained-vgg16/set-pretrained-vgg16.vue";
import PreTrainedMobileNetV2 from "@/components/network-elements/elements/pretrained-mobilenetv2/set-pretrained-mobilenetv2.vue";
import PreTrainedResNet50 from "@/components/network-elements/elements/pretrained-resnet50/set-pretrained-resnet50.vue";
import PreTrainedInceptionV3 from "@/components/network-elements/elements/pretrained-inceptionv3/set-pretrained-inceptionv3.vue";
import UNet from "@/components/network-elements/elements/unet/set-unet.vue";

import IoInput from "@/components/network-elements/elements/io-input/set-io-input.vue";
import IoOutput from "@/components/network-elements/elements/io-output/set-io-output.vue";

import SidebarSettingPreview from "@/components/network-elements/elements-settings/sidebar-setting-preview.vue";
import SidebarLockedSettingsWrapper from "@/components/sidebar/sidebar-locked-settings-wrapper.vue";
import SidebarAutoSettingInfo from "@/components/sidebar/sidebar-auto-setting-info.vue";

import { mapGetters, mapActions } from "vuex";
import { componentTypeToName } from '@/core/constants.js';

export default {
  name: "SidebarSettings",
  components: {
    SidebarSettingPreview,
    DeepLearningFC,
    DeepLearningConv,
    DeepLearningRecurrent,
    ProcessEmbed,
    ProcessGrayscale,
    ProcessOneHot,
    ProcessReshape,
    ProcessRescale,
    MathArgmax,
    MathMerge,
    TrainNormal,
    TrainRegression,
    TrainReinforce,
    TrainGan,
    TrainDetector,
    IoInput,
    IoOutput,
    LayerCustom,
    LayerTfModel,
    PreTrainedVGG16,
    PreTrainedInceptionV3,
    PreTrainedMobileNetV2,
    PreTrainedResNet50,
    UNet,
    SidebarLockedSettingsWrapper,
    SidebarAutoSettingInfo
  },
  data() {
    return {
      componentTypeToName: componentTypeToName
    };
  },
  created() {
    console.log('this.selectedEl', this.selectedEl);
  },
  computed: {
    ...mapGetters({
      selectedEl: "mod_workspace/GET_selectedElement", // {} or null
      currentNetworkId: "mod_workspace/GET_currentNetworkId",
    }),
    codeWindowState() {
      return this.$store.getters[
        "mod_workspace-code-editor/getCodeWindowState"
      ](this.currentNetworkId);
    },
    hasUnsavedChanges() {
      return this.$store.getters[
        "mod_workspace-code-editor/getHasUnsavedChanges"
      ](this.currentNetworkId);
    },
    isSettingPreviewVisible() {
      const hasData =
        this.selectedEl &&
        this.selectedEl.chartData &&
        this.selectedEl.chartData.series &&
        this.selectedEl.chartData.series[0].data !== "";
      return hasData && this.$store.state.mod_workspace.isSettingPreviewVisible;
    },
    shouldShowOpenCodeBtn() {
      return (
        this.selectedEl !== null &&
        this.selectedEl.layerType !== "IoOutput" &&
        this.selectedEl.layerType !== "IoInput"
      );
    },
    shouldShowResetComponentBtn() {
      return (
        this.selectedEl !== null &&
        this.selectedEl.layerType !== "IoOutput" &&
        this.selectedEl.layerType !== "IoInput"
      );
    }
  },
  watch: {
    "selectedEl.layerId"(el) {
      if (el) {
        this.$refs.sidebarSettingWrapper.$el.scrollTop = 0;
      }
    }
  },
  methods: {
    ...mapActions({
      popupConfirm: "globalView/GP_confirmPopup",
    }),
    onOpenCodeButtonClick() {
      if (this.codeWindowState && this.hasUnsavedChanges) {
        this.popupConfirm({
          text:
            "You have unsaved changes. Are you sure you want to load the selected component's code?",
          ok: () => {
            this.openComponentCode();
          }
        });
      } else {
        this.openComponentCode();
      }
    },
    openComponentCode() {
      if (!this.selectedEl) {
        return;
      }

      this.$store.dispatch("mod_workspace-code-editor/openEditor", {
        networkId: this.currentNetworkId,
        element: this.selectedEl
      });
    },
    resetComponentSettings() {
      this.$store.dispatch("mod_workspace/resetNetworkElementSettings", {
        layerId: this.selectedEl.layerId
      });
    }
  }
};
</script>
<style lang="scss" scoped>
.sidebar-setting-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.sidebar-setting-head {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 8px 15px 8px 15px;
  box-sizing: border-box;
  // height: 31px;
}

.sidebar-setting-actions {
  display: flex;
  padding: 4px 8px;

  button {
    margin: 4px;
  }
}

.sidebar-setting-head-name {
  display: flex;
  align-items: center;
  font-size: 16px;
}
.sidebar-setting-head-open-code {
  cursor: pointer;
  background: #131b30;
  border: 0.5px solid #5e6f9f;
  box-sizing: border-box;
  border-radius: 1px;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  font-size: 11px;
  line-height: 15px;
  color: #b6c7fb;

  &:hover {
    background: #6185ee;
    border-color: #6185ee;
    color: #fff;
  }
  &:active:hover {
    background: #7397fe;
  }
}
.setting-values-wrapper {
  padding: 10px 15px;
}
.setting-chart-wrapper {
  position: relative;
  width: 250px;
  // border-top: 2px solid #5D5E60;
  z-index: 10;
}

// also .sidebar-setting-content are used in _forms.scss for stylize sidebar setting inputs
.sidebar-setting-content {
  flex-grow: 1;
  // padding: 10px;
  // background-color: $bg-toolbar-2;
  // border: $border-1;
  // height: calc(65vh - 99px);
  overflow-x: scroll;

  &.closed-preview {
    height: calc(
      100vh - #{$remaining-normal + $preview-header + $preview-content +
        $components-header}
    );
  }

  &.sidebar-setting-content-with-component {
    height: calc(75vh - #{$remaining-normal});
    padding-bottom: 30px;

    &.closed-preview {
      height: calc(
        75vh - #{$remaining-normal + $preview-header + $preview-content}
      );
    }
  }
}
.reset-component-btn {
  margin: 0 12px 10px;
}

.primary {
  margin-left: 16px;
}

.no-border {
  border-width: 0px !important;
}

.component-name {
  font-size: 14px;
  font-weight: bold;
}
</style>
