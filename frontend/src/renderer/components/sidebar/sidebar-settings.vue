<template lang="pug">
  .sidebar-setting-wrapper
    .sidebar-setting-head
      sidebar-auto-setting-info(
        v-if="selectedEl !== null"
        :key="selectedEl.layerId"
        :selectedEl="selectedEl"
      )
      .sidebar-setting-head-name Settings
      button.btn-menu-bar(
        v-if="shouldShowOpenCodeBtn"
        @click="onOpenCodeButtonClick()"
        ) Open code
    perfect-scrollbar.sidebar-setting-content(
      :data-tutorial-target="'tutorial-workspace-settings'"
      :class="{'sidebar-setting-content-with-component': selectedEl !== null, 'closed-preview': isSettingPreviewVisible}"
      ref="sidebarSettingWrapper"
      )
      sidebar-locked-settings-wrapper(
        :selectedEl="selectedEl"
      )
        component.setting-values-wrapper(
          v-if="selectedEl !== null"
          :key="selectedEl.layerId"
          v-bind:is="selectedEl.componentName"
          :currentEl="selectedEl"
          ref="componentSettings"
          )

    sidebar-setting-preview.setting-chart-wrapper(
      v-if="selectedEl !== null"
      :current-el="selectedEl"
      )
    button.reset-component-btn(
      v-if="shouldShowResetComponentBtn"
      @click="resetComponentSettings"
      ) Reset Component
</template>
<script>

import DataData       from '@/components/network-elements/elements/data-data/set-data-data.vue'
import DataRandom         from '@/components/network-elements/elements/data-random/set-data-random.vue'
import DataEnvironment    from '@/components/network-elements/elements/data-environment/set-data-environment.vue'
import DataCloud          from '@/components/network-elements/elements/data-cloud/set-data-cloud.vue'

import DeepLearningFC        from '@/components/network-elements/elements/deep-learning-fc/set-deep-learning-fc.vue'
import DeepLearningConv      from '@/components/network-elements/elements/deep-learning-conv/set-deep-learning-conv.vue'
import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/set-deep-learning-recurrent.vue'

import ProcessCrop      from '@/components/network-elements/elements/process-crop/set-process-crop.vue'
import ProcessEmbed     from '@/components/network-elements/elements/process-embed/set-process-embed.vue'
import ProcessGrayscale from '@/components/network-elements/elements/process-grayscale/set-process-grayscale.vue'
import ProcessOneHot    from '@/components/network-elements/elements/process-one-hot/set-process-one-hot.vue'
import ProcessReshape   from '@/components/network-elements/elements/process-reshape/set-process-reshape.vue'
import ProcessRescale   from '@/components/network-elements/elements/process-rescale/set-process-rescale.vue'

import MathArgmax   from '@/components/network-elements/elements/math-argmax/set-math-argmax.vue'
import MathMerge    from '@/components/network-elements/elements/math-merge/set-math-merge.vue'
import MathSwitch    from '@/components/network-elements/elements/math-switch/set-math-switch.vue'
import MathSplit    from '@/components/network-elements/elements/math-split/set-math-split.vue'

import TrainNormal          from '@/components/network-elements/elements/train-normal/set-train-normal.vue'
import TrainRegression      from '@/components/network-elements/elements/train-regression/set-train-regression.vue'
import TrainGenetic         from '@/components/network-elements/elements/train-genetic/set-train-genetic.vue'
import TrainDynamic         from '@/components/network-elements/elements/train-dynamic/set-train-dynamic.vue'
import TrainReinforce       from '@/components/network-elements/elements/train-reinforce/set-train-reinforce.vue'
import TrainLoss            from '@/components/network-elements/elements/train-loss/set-train-loss.vue'
import TrainOptimizer       from '@/components/network-elements/elements/train-optimizer/set-train-optimizer.vue'
import TrainGan             from '@/components/network-elements/elements/train-gan/set-train-gan.vue'
import TrainDetector        from '@/components/network-elements/elements/train-detector/set-train-detector.vue'

import LayerCustom          from '@/components/network-elements/elements/layer-custom/layer-custom.vue'

import PreTrainedVGG16        from '@/components/network-elements/elements/pretrained-vgg16/set-pretrained-vgg16.vue'
import PreTrainedMobileNetV2  from '@/components/network-elements/elements/pretrained-mobilenetv2/set-pretrained-mobilenetv2.vue'
import PreTrainedResNet50  from '@/components/network-elements/elements/pretrained-resnet50/set-pretrained-resnet50.vue'
import PreTrainedInceptionV3  from '@/components/network-elements/elements/pretrained-inceptionv3/set-pretrained-inceptionv3.vue'

import IoInput            from '@/components/network-elements/elements/io-input/set-io-input.vue'
import IoOutput             from '@/components/network-elements/elements/io-output/set-io-output.vue'

import SidebarSettingPreview  from "@/components/network-elements/elements-settings/sidebar-setting-preview.vue";
import SidebarLockedSettingsWrapper from "@/components/sidebar/sidebar-locked-settings-wrapper.vue"
import SidebarAutoSettingInfo from '@/components/sidebar/sidebar-auto-setting-info.vue'

import { mapGetters, mapActions } from 'vuex';
  
export default {
  name: 'SidebarSettings',
  components: { 
    SidebarSettingPreview,
    DataData, DataEnvironment, DataRandom, DataCloud,
    DeepLearningFC, DeepLearningConv, DeepLearningRecurrent,
    ProcessCrop, ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape, ProcessRescale,
    MathArgmax, MathMerge, MathSwitch, MathSplit,
    TrainNormal, TrainRegression, TrainGenetic, TrainDynamic, TrainReinforce, TrainLoss, TrainOptimizer, TrainGan, TrainDetector,
    IoInput, IoOutput,
    LayerCustom,
    PreTrainedVGG16, PreTrainedInceptionV3, PreTrainedMobileNetV2, PreTrainedResNet50,
    SidebarLockedSettingsWrapper,
    SidebarAutoSettingInfo
  }, 
  computed: {
    ...mapGetters({
      selectedEl: 'mod_workspace/GET_selectedElement', // {} or null
      currentNetworkId: 'mod_workspace/GET_currentNetworkId',
    }),
    codeWindowState() {
      return this.$store.getters['mod_workspace-code-editor/getCodeWindowState'](this.currentNetworkId);
    },
    hasUnsavedChanges() {
      return this.$store.getters['mod_workspace-code-editor/getHasUnsavedChanges'](this.currentNetworkId);
    },
    isSettingPreviewVisible() {
      const hasData = this.selectedEl && this.selectedEl.chartData && this.selectedEl.chartData.series && this.selectedEl.chartData.series[0].data !== '';
      return hasData && this.$store.state.mod_workspace.isSettingPreviewVisible;
    },
    shouldShowOpenCodeBtn() {
      return this.selectedEl !== null && this.selectedEl.layerType !== 'IoOutput' && this.selectedEl.layerType !== 'IoInput'
    },
    shouldShowResetComponentBtn() {
      return this.selectedEl !== null && this.selectedEl.layerType !== 'IoOutput' && this.selectedEl.layerType !== 'IoInput'
    }
  },
  watch: {
    'selectedEl.layerId'(el) {
       if(el) {
         this.$refs.sidebarSettingWrapper.$el.scrollTop = 0;
       }
    }
  },
  methods: {
    ...mapActions({
      popupConfirm: 'globalView/GP_confirmPopup',
      setNextStep:  'mod_tutorials/setNextStep',
    }),
    onOpenCodeButtonClick() {
      if (this.codeWindowState && this.hasUnsavedChanges) {
        
        this.popupConfirm(
          {
            text: 'You have unsaved changes. Are you sure you want to load the selected component\'s code?',
            ok: () => {
              this.openComponentCode();
            }
          });
      } else {
        this.openComponentCode();
      }
    },
    openComponentCode() {
      if (!this.selectedEl) { return; }

      this.setNextStep({currentStep:'tutorial-workspace-settings'});
      
      this.$store.dispatch('mod_workspace-code-editor/openEditor', {
        networkId: this.currentNetworkId,
        element: this.selectedEl,
      });
    },
    resetComponentSettings() {
      this.$store.dispatch("mod_workspace/resetNetworkElementSettings", { layerId: this.selectedEl.layerId });
    },
  }
  
}
</script>
<style lang="scss" scoped>

.sidebar-setting-head {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;

  padding-left: 15px;
  padding-right: 3px;

  background: #363E51;
  border: 1px solid #475D9C;
  box-sizing: border-box;
  height: 31px;
}
.sidebar-setting-head-name {

  font-family: Nunito Sans;
  font-style: normal;
  font-weight: normal;
  font-size: 12px;
  line-height: 16px;
  color: #B6C7FB;
}
.sidebar-setting-head-open-code {
  cursor: pointer;
  background: #131B30;
  border: 0.5px solid #5E6F9F;
  box-sizing: border-box;
  border-radius: 1px;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  font-size: 11px;
  line-height: 15px;
  color: #B6C7FB;

  &:hover {
    background: #6185EE;
    border-color: #6185EE;
    color: #fff;
  }
  &:active:hover {
    background: #7397FE;
  }
}
.setting-values-wrapper {
  // padding: 10px 15px;
}
.setting-chart-wrapper {
  position: absolute;
  width: 250px;
  border-top: 2px solid #5D5E60;
  bottom: 23px;   
  z-index: 10;
}
// also .sidebar-setting-content are used in _forms.scss for stylize sidebar setting inputs
.sidebar-setting-content {
  // padding: 10px;
  background-color: #23252A;
  height: calc(65vh - 99px);
  overflow-x: scroll;
  
  &.sidebar-setting-content-with-component {
    height: calc(65vh - 123px);
    padding-bottom: 30px;

    &.closed-preview {
      height: calc(65vh - 263px);
    }
  }
}
.reset-component-btn {
  position: absolute;
  bottom: 0;
  margin-top: auto;
  border-top: 1px solid #5D5E60;
  background: #131B30;
  border-radius: 1px;
  font-family: Nunito Sans;
  font-size: 11px;
  line-height: 18px;
  color: rgba(182, 199, 251, 0.75);
  width: 250px;
  height: 24px;
}
</style>
