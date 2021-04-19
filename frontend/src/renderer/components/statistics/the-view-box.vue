<template lang="pug">
  section.network_info-section
    //- .info-section_head(v-show="!testIsOpen")
    //-   h3 {{ sectionTitle }}
    view-box-btn-list(
      v-if="layerMetrics && layerType !== 'Training' && layerType !== 'IoOutput'"
      v-show="!testIsOpen"
      :layerType="'ViewBox'"
      )
    .info-section_main(v-if="elData !== null")
      component(
        :is="elData.componentName"
        :element-data="elData.viewBox"
        :current-tab="selectedMetric"
        @btn-list="setBtnList"
        )
</template>

<script>
  /*statistics*/
  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/viewBox-classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/viewBox-classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/viewBox-classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/viewBox-classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/viewBox-classic-ml-vector-machine.vue'
  import TrainDynamic     from '@/components/network-elements/elements/train-dynamic/viewBox-train-dynamic.vue'
  import TrainGenetic     from '@/components/network-elements/elements/train-genetic/viewBox-train-genetic.vue'
  import TrainNormal      from '@/components/network-elements/elements/train-normal/viewBox-train-normal.vue'
  import TrainReinforce   from '@/components/network-elements/elements/train-reinforce/viewBox-train-reinforce.vue'
  import TrainLoss        from '@/components/network-elements/elements/train-loss/viewBox-train-loss.vue'
  import TrainOptimizer   from '@/components/network-elements/elements/train-optimizer/viewBox-train-optimizer.vue'
  import TrainGan         from '@/components/network-elements/elements/train-gan/viewBox-train-gan.vue'
  import TrainRegression         from '@/components/network-elements/elements/train-regression/viewBox-train-regression.vue'
  import TrainDetector    from '@/components/network-elements/elements/train-detector/viewBox-train-detector.vue'

  /*view box*/
  import DataData         from '@/components/network-elements/elements/data-data/viewBox-data-data.vue'
  import DataRandom         from '@/components/network-elements/elements/data-random/viewBox-data-random.vue'
  import DataEnvironment  from '@/components/network-elements/elements/data-environment/viewBox-data-environment.vue'
  import DataCloud        from '@/components/network-elements/elements/data-cloud/viewBox-data-cloud.vue'
  import DeepLearningFC        from '@/components/network-elements/elements/deep-learning-fc/viewBox-deep-learning-fc.vue'
  import DeepLearningConv      from '@/components/network-elements/elements/deep-learning-conv/viewBox-deep-learning-conv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/viewBox-deep-learning-recurrent.vue'
  import ProcessCrop      from '@/components/network-elements/elements/process-crop/viewBox-process-crop.vue'
  import ProcessEmbed     from '@/components/network-elements/elements/process-embed/viewBox-process-embed.vue'
  import ProcessGrayscale from '@/components/network-elements/elements/process-grayscale/viewBox-process-grayscale.vue'
  import ProcessOneHot    from '@/components/network-elements/elements/process-one-hot/viewBox-process-one-hot.vue'
  import ProcessReshape   from '@/components/network-elements/elements/process-reshape/viewBox-process-reshape.vue'
  import ProcessRescale   from '@/components/network-elements/elements/process-rescale/viewBox-process-rescale.vue'
  import PreTrainedResNet50 from '@/components/network-elements/elements/pretrained-resnet50/viewBox-pretrained-resnet50.vue'
  import PreTrainedMobileNetV2 from '@/components/network-elements/elements/pretrained-mobilenetv2/viewBox-pretrained-mobilenetv2.vue'
  import PreTrainedVGG16 from '@/components/network-elements/elements/pretrained-vgg16/viewBox-pretrained-vgg16.vue'
  import PreTrainedInceptionV3 from '@/components/network-elements/elements/pretrained-inceptionv3/viewBox-pretrained-inceptionv3.vue'
  import MathArgmax   from '@/components/network-elements/elements/math-argmax/viewBox-math-argmax.vue'
  import MathMerge    from '@/components/network-elements/elements/math-merge/viewBox-math-merge.vue'
  import MathSwitch    from '@/components/network-elements/elements/math-switch/viewBox-math-switch.vue'
  import MathSoftmax  from '@/components/network-elements/elements/math-softmax/viewBox-math-softmax.vue'
  import MathSplit    from '@/components/network-elements/elements/math-split/viewBox-math-split.vue'
  import LayerCustom          from '@/components/network-elements/elements/layer-custom/viewBox-layer-custom.vue'
  import IoInput          from '@/components/network-elements/elements/io-input/viewBox-io-input.vue'
  import IoOutput         from '@/components/network-elements/elements/io-output/viewBox-io-output.vue'

  import ViewBoxBtnList from '@/components/statistics/view-box-btn-list.vue'

  import { mapGetters, mapMutations, mapActions } from 'vuex';

export default {
  name: "TheViewBox",
  components: {
    DataData, DataEnvironment, DataRandom,
    // DataCloud,
    DeepLearningFC, DeepLearningConv, DeepLearningRecurrent,
    ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape, ProcessRescale,
    // ProcessCrop,
    TrainNormal, TrainRegression, TrainGenetic, TrainDynamic, TrainReinforce, TrainDetector, TrainGan,
    // TrainLoss, TrainOptimizer, 
    PreTrainedResNet50, PreTrainedMobileNetV2, PreTrainedVGG16, PreTrainedInceptionV3,
    MathArgmax, MathMerge, MathSoftmax, MathSwitch,
    // MathSplit,
    IoInput, IoOutput,
    LayerCustom,
    // ClassicMLDbscans, ClassicMLKMeans, ClassicMLKNN, ClassicMLRandomForest, ClassicMLSVM,
  ViewBoxBtnList
},
  props: {
    sectionTitle: {type: String},
    elData: {
      type: Object,
      default: function () {
        return null
      }
    }
  },
  data() {
    return {
      /*
      * btnList model
      *
      * btnList: {
      *   ButtonName: null,
      *   ButtonName: {
      *     btnId: 'string',
      *     btnClass: 'string',
      *     btnInteractiveInfo: {
      *       title: 'string',
      *       text: 'string'
      *     }
      *   },
      * },
      *
      * */
    }
  },
  computed: {
    ...mapGetters({
      testIsOpen:     'mod_workspace/GET_testIsOpen',
    }),
    layerType() {
      return this.elData ? this.elData.layerType : '';
    },
    selectedMetric() {
      return this.$store.getters['mod_statistics/getSelectedMetric'](this.layerType);
    }
  },
  watch: {
    'elData.componentName': {
      handler() { this.resetBtnInfo() }
    }
  },
  methods: {
    setBtnList(objList) {
      this.$store.commit('mod_statistics/setLayerMetrics', { layerType: this.layerType, layerMetrics: objList });
      this.$store.commit('mod_statistics/setDefaultMetric', this.layerType);
    },
    resetBtnInfo() {
      this.$store.commit('mod_statistics/setLayerMetrics', { layerType: this.layerType, layerMetrics: '' });
    },
    layerMetrics() {
      return this.$store.getters['mod_statistics/getLayerMetrics'](this.layerType);
    }
  }
}
</script>

<style lang="scss">
  @import "../../scss/base";
  .open-statistic .the-view-box .info-section_main {
    padding-left: 0;
  }
  /*statistics*/
  .open-test .the-statistics .info-section_main {
    // border-left: 2px solid $bg-window;
  }
  .info-section_head {
  //   border-top: 1px solid $color-5;
  }
</style>
