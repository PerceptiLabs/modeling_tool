<template lang="pug">
  aside.page_layersbar(:class="{'page_layersbar--hide': !hideLayers, 'tutorial-active': activeStepStoryboard === 2}")
    ul.layersbar-list#tutorial_layersbar-list
      li.layer(
        v-for="(layer, i) in layersbarList"
        :key="i"
      )
        button.btn.btn--layersbar.layer_parent.js-clickout.tooltip-wrap(type="button"
          v-tooltip:right="layer.tooltip"
          v-tooltip-interactive:right="layer.tooltip_interactive"
          @click.stop="toggleElList(i, $event, layer.id, layer.dynamic_id)"
          :class="[layer.layerClass, {'active': layer.showEl}]"
          :id="layer.id"
        )
          i.icon(:class="layer.iconClass")
        ul.layer_child-list#tutorial_layer_child-list(
          :class="layer.childListClass"
          v-if="layer.networkElements"
        )
          li(
            v-for="(element, i) in layer.networkElements"
            :key="i"
          )
            component(:is="element" :draggable="true")
      li.layer
        layer-custom(:draggable="true")

</template>

<script>
  import clickOutside from '@/core/mixins/click-outside.js'
  import {trainingElements, deepLearnElements}  from '@/core/constants.js'
  import { mapActions }       from 'vuex';

  import DataData             from '@/components/network-elements/elements/data-data/view-data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment/view-data-environment.vue'
  import DataRandom      from '@/components/network-elements/elements/data-random/view-data-random.vue'
  import DataCloud            from '@/components/network-elements/elements/data-cloud/view-data-cloud.vue'

  import DeepLearningFC       from '@/components/network-elements/elements/deep-learning-fc/view-deep-learning-fc.vue'
  import DeepLearningConv     from '@/components/network-elements/elements/deep-learning-conv/view-deep-learning-conv.vue'
  import DeepLearningDeconv   from '@/components/network-elements/elements/deep-learning-deconv/view-deep-learning-deconv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/view-deep-learning-recurrent.vue'

  import ProcessCrop          from '@/components/network-elements/elements/process-crop/view-process-crop.vue'
  import ProcessEmbed         from '@/components/network-elements/elements/process-embed/view-process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/view-process-grayscale.vue'
  import ProcessOneHot        from '@/components/network-elements/elements/process-one-hot/view-process-one-hot.vue'
  import ProcessReshape       from '@/components/network-elements/elements/process-reshape/view-process-reshape.vue'
  import ProcessRescale       from '@/components/network-elements/elements/process-rescale/view-process-rescale.vue'

  import TrainNormal          from '@/components/network-elements/elements/train-normal/view-train-normal.vue'
  import TrainRegression      from '@/components/network-elements/elements/train-regression/view-train-regression.vue'
  import TrainGenetic         from '@/components/network-elements/elements/train-genetic/view-train-genetic.vue'
  import TrainDynamic         from '@/components/network-elements/elements/train-dynamic/view-train-dynamic.vue'
  import TrainReinforce       from '@/components/network-elements/elements/train-reinforce/view-train-reinforce.vue'
  import TrainLoss            from '@/components/network-elements/elements/train-loss/view-train-loss.vue'
  import TrainOptimizer       from '@/components/network-elements/elements/train-optimizer/view-train-optimizer.vue'
  import TrainGan             from '@/components/network-elements/elements/train-gan/view-train-gan.vue'
  import TrainDetector        from '@/components/network-elements/elements/train-detector/view-train-detector.vue'

  import MathArgmax           from '@/components/network-elements/elements/math-argmax/view-math-argmax.vue'
  import MathSwitch           from '@/components/network-elements/elements/math-switch/view-math-switch.vue'
  import MathMerge            from '@/components/network-elements/elements/math-merge/view-math-merge.vue'
  import MathSoftmax          from '@/components/network-elements/elements/math-softmax/view-math-softmax.vue'
  import MathSplit            from '@/components/network-elements/elements/math-split/view-math-split.vue'

  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/view-classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/view-classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/view-classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/view-classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/view-classic-ml-vector-machine.vue'

  import LayerCustom         from '@/components/network-elements/elements/layer-custom/view-layer-custom.vue'


export default {
  name: 'TheLayersbar',
  mixins: [clickOutside],
  components: {
    DataData, DataEnvironment, DataRandom,
    // DataCloud,
    DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
    ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape, ProcessRescale,
    // ProcessCrop,
    TrainNormal, TrainRegression, TrainGenetic, TrainDynamic, TrainReinforce, TrainDetector, TrainGan,
    // TrainLoss, TrainOptimizer, 
    MathArgmax, MathMerge, MathSoftmax, MathSwitch,
    // MathSplit,

    // ClassicMLDbscans, ClassicMLKMeans, ClassicMLKNN, ClassicMLRandomForest, ClassicMLSVM,
    LayerCustom
  },
  data() {
    return {
      layersbarList: [
        {
          tooltip: 'Data',
          tooltip_interactive: {
            title: 'Data',
            text: 'Choose between reading from </br> a source or an environment'
          },
          layerClass: 'net-element-data',
          iconClass: 'icon-data',
          childListClass: '',
          showEl: false,
          networkElements: ['DataData', 'DataEnvironment', 'DataRandom', 'DataCloud'],
          id:'tutorial_data'
          //networkElements: ['DataData']
        },
        {
          tooltip: 'Processing',
          tooltip_interactive: {
            title: 'Processing',
            text: 'Process and transform the data.'
          },
          layerClass: 'net-element-process',
          iconClass: 'icon-settings',
          childListClass: '',
          showEl: false,
          networkElements: ['process-reshape', 'process-rescale', 'process-embed', 'process-grayscale', 'ProcessOneHot', 'process-crop'],
          id:'tutorial_processing'
          //networkElements: ['process-reshape', 'process-embed', 'process-grayscale', 'process-hot']
        },
        {
          tooltip: 'Deep Learning',
          tooltip_interactive: {
            title: 'Deep Learning',
            text: 'Deep learning components'
          },
          layerClass: 'net-element-learn-deep',
          iconClass: 'icon-network',
          childListClass: '',
          showEl: false,
          //networkElements: ['LearnDeepConnect', 'LearnDeepConvolut', 'LearnDeepDeconvolut', 'LearnDeepRecurrent']
          networkElements: deepLearnElements,
          id:'tutorial_deep-learning'
        },
        {
          tooltip: 'Mathematics',
          tooltip_interactive: {
            title: 'Mathematics',
            text: 'Mathematical components'
          },
          layerClass: 'net-element-math',
          iconClass: 'icon-calc',
          childListClass: '',
          showEl: false,
          networkElements: ['MathArgmax', 'MathMerge', 'MathSplit', 'MathSoftmax', 'MathSwitch'],
          id:'tutorial_mathematics'
        },
        {
          tooltip: 'Training',
          tooltip_interactive: {
            title: 'Training',
            text: 'Training components'
          },
          layerClass: 'net-element-train',
          iconClass: 'icon-training',
          childListClass: 'layer_child-list--training',
          showEl: false,
          //networkElements: ['TrainNormal', 'TrainReinforce', 'TrainGenetic', 'TrainDynamic']
          networkElements: trainingElements,
          id:'tutorial_training'
        },
        // {
        //   tooltip: 'Classic Machine Learning',
        //   tooltip_interactive: {
        //     title: 'Classic Machine Learning',
        //     text: 'Classic machine learning components'
        //   },
        //   layerClass: 'net-element-learn-class',
        //   iconClass: 'icon-mind',
        //   childListClass: '',
        //   showEl: false,
        //   networkElements: ['ClassicMLDbscans', 'ClassicMLKMeans', 'ClassicMLKNN', 'ClassicMLRandomForest', 'ClassicMLSVM'],
        //   id:'tutorial_classic-machine-learning'
        // }
      ],
    }
  },
  computed: {
    hideLayers () {
      return this.$store.state.globalView.hideLayers
    },
    activeStepStoryboard() {
      return this.$store.state.mod_tutorials.activeStepStoryboard
    }
  },
  methods: {
    toggleElList(index, ev, tutorial_id) {
      if (this.layersbarList[index].showEl) {
        this.layersbarList[index].showEl = false;
        document.removeEventListener('click', this.clickOutside);
      }
      else {
        this.clickOutsideAction();
        this.layersbarList[index].showEl = true;
        this.ClickElementTracking = ev.target.closest('.js-clickout');
        document.addEventListener('click', this.clickOutside);
      }
    },
    //btn btn--layersbar layer_parent js-clickout tooltip-wrap net-element-data
    //btn btn--layersbar                          tooltip-wrap net-element-data
    clickOutsideAction() {
      this.layersbarList.forEach((item)=> {
        item.showEl = false
      });
    }
  },
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  $indent: 5px;
  .page_layersbar {
    max-width: $w-layersbar;
    grid-area: layersbar;
    transition: max-width $animation-speed;
    border-right: 1px solid $bg-workspace;
    z-index: 1;
    &.page_layersbar--hide {
      transition: max-width $animation-speed $animation-speed;
      max-width: 0;
      .layersbar-list {
        transition: transform $animation-speed;
        transform: translateY(-120%);
      }
    }
  }
  .layersbar-list {
    margin: 0;
    padding: 0 0 30px 0;
    list-style: none;
    transition: transform $animation-speed $animation-speed;
    transform: translateY(0);
    .btn--layersbar {
      box-shadow: $box-shad;
    }
  }
  .layer {
    position: relative;
    padding: $indent $indent 0 $indent;
  }
  .layer_parent {
    position: relative;
    z-index: 1;
    &:after {
      content: '\e922';
      font-family: 'icomoon' !important;
      font-size: 1.1em;
      .is-web & {
        font-size: calc(var(--sidebar-scale-coefficient) * 1.1em);
      }
      line-height: 1;
      position: absolute;
      right: 1px;
      bottom: 1px;
    }
  }
  ul.layer_child-list {
    @include multi-transition (transform, opacity, visibility);
    position: absolute;
    top: 0;
    left: -$indent;
    opacity: 0;
    visibility: hidden;
    margin: 0;
    padding: $indent;
    //transform: translateX(-100%);
    @media (max-height: 1000px) {
      .layer:nth-child(n+5) & {
        top: auto;
        bottom: -$indent;
        &.layer_child-list--training {
          bottom: -135px;
        }
      }
    }
    .active + & {
      visibility: visible;
      opacity: 1;
      transform: translateX(100%);
    }
    > li + li {
      padding-top: $indent;
    }
  }
  ul.layer_child-list--training {
    top: -137px;
    > li:nth-child(2) {
      border-bottom: 2px solid $bg-scroll;
      padding-bottom: $indent;
    }
  }
</style>
