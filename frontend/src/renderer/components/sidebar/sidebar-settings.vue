<template lang="pug">
  .sidebar-setting-wrapper
    .sidebat-setting-head
      .sidebat-setting-head-name Settings
      button.sidebat-setting-head-open-code(@click="onOpenCodeButtonClick()") Open code
    .sidebar-setting-content
      //- h1 {{selectedEl && selectedEl.componentName}}
      component.setting-values-wrapper(v-if="selectedEl !== null" :key="selectedEl.layerId" v-bind:is="selectedEl.componentName" :currentEl="selectedEl" ref="componentSettings")
      sidebar-setting-preview.setting-chart-wrapper(
        v-if="selectedEl !== null"
        :current-el="selectedEl"
        )
</template>
<script>

import SettingsElWeb         from '@/components/network-elements/elements/data-data/set-data-data.vue'
import SettingsElElectron   from '@/components/network-elements/elements/data-data/set-data-data-electron.vue';
import DataRandom         from '@/components/network-elements/elements/data-random/set-data-random.vue'
import DataEnvironment  from '@/components/network-elements/elements/data-environment/set-data-environment.vue'
import DataCloud        from '@/components/network-elements/elements/data-cloud/set-data-cloud.vue'

import DeepLearningFC        from '@/components/network-elements/elements/deep-learning-fc/set-deep-learning-fc.vue'
import DeepLearningConv      from '@/components/network-elements/elements/deep-learning-conv/set-deep-learning-conv.vue'
import DeepLearningDeconv    from '@/components/network-elements/elements/deep-learning-deconv/set-deep-learning-deconv.vue'
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
import MathSoftmax  from '@/components/network-elements/elements/math-softmax/set-math-softmax.vue'
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

import SidebarSettingPreview  from "@/components/network-elements/elements-settings/sidebar-setting-preview.vue";

import { mapGetters, mapActions } from 'vuex';

let DataData = null;
if(!(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1)) {
  DataData = SettingsElWeb;
} else {
  DataData = SettingsElElectron
}
  
export default {
  name: 'SidebarSettings',
  components: { 
    SidebarSettingPreview,
    DataData, DataEnvironment, DataRandom, DataCloud,
    DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
    ProcessCrop, ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape, ProcessRescale,
    MathArgmax, MathMerge, MathSwitch, MathSoftmax, MathSplit,
    TrainNormal, TrainRegression, TrainGenetic, TrainDynamic, TrainReinforce, TrainLoss, TrainOptimizer, TrainGan, TrainDetector,
    LayerCustom
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
  },
  watch: {
    'selectedEl'(el) {
        //console.log('sidebar-settings selectedEl', el);
    }
  },
  methods: {
    ...mapActions({
      popupConfirm: 'globalView/GP_confirmPopup',
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
      
      this.$store.dispatch('mod_workspace-code-editor/openEditor', {
        networkId: this.currentNetworkId,
        element: this.selectedEl,
      });
    },
  }
  
}
</script>
<style lang="scss" scoped>

.sidebar-setting-wrapper {
  
  // background-color: red;
}
.sidebat-setting-head {
  display: flex;
  align-items: center;
  justify-content: space-between;

  padding-left: 15px;
  padding-right: 3px;

  background: #363E51;
  border: 1px solid #475D9C;
  box-sizing: border-box;
  height: 25px;
}
.sidebat-setting-head-name {

  font-family: Nunito Sans;
  font-style: normal;
  font-weight: normal;
  font-size: 12px;
  line-height: 16px;
  color: #B6C7FB;
}
.sidebat-setting-head-open-code {
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

}
.setting-values-wrapper {
  // padding: 10px 15px;
}
.setting-chart-wrapper {
  margin: 0 10px 0 5px;
  border-top: 1px solid #343948;
}
// also .sidebar-setting-content are used in _forms.scss for stylize sidebar setting inputs
.sidebar-setting-content {
  // padding: 10px;
  background-color: #23252A;
  height: calc(60vh - 39px);
  overflow-x: scroll;
}
</style>
