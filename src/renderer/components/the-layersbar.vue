<template lang="pug">
  aside.page_layersbar(:class="{'page_layersbar--hide': !hideLayers}")
    ul.layersbar-list
      li.layer(
        v-for="(layer, i) in layersbarList"
        :key="i"
      )
        button.btn.btn--layersbar.layer_parent.js-clickout.tooltip-wrap(type="button"
          v-tooltip:right="layer.tooltip"
          @click.stop="toggleElList(i, $event)"
          :class="[layer.layerClass, {'active': layer.showEl}]"
        )
          i.icon(:class="layer.iconClass")
        ul.layer_child-list(
          v-if="layer.networkElements"
        )
          li(
            v-for="(element, i) in layer.networkElements"
            :key="i"
          )
            component(:is="element" :draggable='true')
      li.layer
        button.btn.btn--layersbar.net-element-add(type="button")
          i.icon.icon-add

</template>

<script>
  import clickOutside from '@/core/mixins/click-outside.js'
  import {trainingElements, deepLearnElements}  from '@/core/constants.js'

  import IoInput              from '@/components/network-elements/elements/io-input/view-io-input.vue'
  import IoOutputBackprop     from '@/components/network-elements/elements/io-output-backpropagation/view-io-output-backpropagation.vue'
  import IoOutputGenetic      from '@/components/network-elements/elements/io-output-genetic-algorithm/view-io-output-genetic-algorithm.vue'
  import IoOutputRouting      from '@/components/network-elements/elements/io-output-routing-algorithm/view-io-output-routing-algorithm.vue'

  import DataData             from '@/components/network-elements/elements/data-data/view-data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment/view-data-environment.vue'

  import DeepLearningFC       from '@/components/network-elements/elements/deep-learning-fc/view-deep-learning-fc.vue'
  import DeepLearningConv     from '@/components/network-elements/elements/deep-learning-conv/view-deep-learning-conv.vue'
  import DeepLearningDeconv   from '@/components/network-elements/elements/deep-learning-deconv/view-deep-learning-deconv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/view-deep-learning-recurrent.vue'

  import ProcessCrop          from '@/components/network-elements/elements/process-crop/view-process-crop.vue'
  import ProcessEmbed         from '@/components/network-elements/elements/process-embed/view-process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/view-process-grayscale.vue'
  import ProcessOneHot        from '@/components/network-elements/elements/process-one-hot/view-process-one-hot.vue'
  import ProcessReshape       from '@/components/network-elements/elements/process-reshape/view-process-reshape.vue'

  import TrainNormal          from '@/components/network-elements/elements/train-normal/view-train-normal.vue'
  import TrainNormalData      from '@/components/network-elements/elements/train-normal-data/view-train-normal-data.vue'
  import TrainGenetic         from '@/components/network-elements/elements/train-genetic/view-train-genetic.vue'
  import TrainDynamic         from '@/components/network-elements/elements/train-dynamic/view-train-dynamic.vue'
  import TrainReinforce       from '@/components/network-elements/elements/train-reinforce/view-train-reinforce.vue'

  import MathArgmax           from '@/components/network-elements/elements/math-argmax/view-math-argmax.vue'
  import MathMerge            from '@/components/network-elements/elements/math-merge/view-math-merge.vue'
  import MathSoftmax          from '@/components/network-elements/elements/math-softmax/view-math-softmax.vue'
  import MathSplit            from '@/components/network-elements/elements/math-split/view-math-split.vue'

  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/view-classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/view-classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/view-classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/view-classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/view-classic-ml-vector-machine.vue'


export default {
  name: 'TheLayersbar',
  mixins: [clickOutside],
  components: {
    IoInput, IoOutputBackprop, IoOutputGenetic, IoOutputRouting,
    DataData, DataEnvironment,
    DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
    ProcessCrop, ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape,
    TrainNormal, TrainNormalData, TrainGenetic, TrainDynamic, TrainReinforce,
    MathArgmax, MathMerge, MathSoftmax, MathSplit,
    ClassicMLDbscans, ClassicMLKMeans, ClassicMLKNN, ClassicMLRandomForest, ClassicMLSVM,
  },
  data() {
    return {
      layersbarList: [
        // {
        //   tooltip: 'I/O',
        //   layerClass: 'net-element-io',
        //   iconClass: 'icon-data-toggle',
        //   showEl: false,
        //   networkElements: ['IoInput', 'IoOutputBackprop', 'IoOutputGenetic', 'IoOutputRouting']
        // },
        {
          tooltip: 'Data',
          layerClass: 'net-element-data',
          iconClass: 'icon-data',
          showEl: false,
          networkElements: ['DataData', 'DataEnvironment']
          //networkElements: ['DataData']
        },
        {
          tooltip: 'Processing',
          layerClass: 'net-element-process',
          iconClass: 'icon-settings',
          showEl: false,
          networkElements: ['process-reshape', 'process-embed', 'process-grayscale', 'ProcessOneHot', 'process-crop']
          //networkElements: ['process-reshape', 'process-embed', 'process-grayscale', 'process-hot']
        },
        {
          tooltip: 'Deep Learning',
          layerClass: 'net-element-learn-deep',
          iconClass: 'icon-network',
          showEl: false,
          //networkElements: ['LearnDeepConnect', 'LearnDeepConvolut', 'LearnDeepDeconvolut', 'LearnDeepRecurrent']
          networkElements: deepLearnElements
        },
        {
          tooltip: 'Mathematics',
          layerClass: 'net-element-math',
          iconClass: 'icon-calc',
          showEl: false,
          networkElements: ['MathArgmax', 'MathMerge', 'MathSplit', 'MathSoftmax']
          //networkElements: ['MathArgmax', 'MathMerge', 'MathSoftmax']
        },
        {
          tooltip: 'Training',
          layerClass: 'net-element-train',
          iconClass: 'icon-training',
          showEl: false,
          //networkElements: ['TrainNormal', 'TrainNormalData', 'TrainReinforce', 'TrainGenetic', 'TrainDynamic']
          networkElements: trainingElements
        },
        {
          tooltip: 'Classic Machine Learning',
          layerClass: 'net-element-learn-class',
          iconClass: 'icon-mind',
          showEl: false,
          networkElements: ['ClassicMLDbscans', 'ClassicMLKMeans', 'ClassicMLKNN', 'ClassicMLRandomForest', 'ClassicMLSVM']
        }
      ],
    }
  },
  computed: {
    hideLayers () {
      return this.$store.state.globalView.hideLayers
    },
  },
  methods: {
    toggleElList(index, ev) {
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
    clickOutsideAction() {
      this.layersbarList.forEach((item)=> {
        item.showEl = false
      });
    },
  }
}
</script>

<style lang="scss">
  @import "../scss/base";
  $indent: 5px;
  .page_layersbar {
    max-width: $w-layersbar;
    grid-area: layersbar;
    transition: max-width $animation-speed;
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
    padding: 0;
    padding-bottom: 30px;
    list-style: none;
    transition: transform $animation-speed $animation-speed;
    transform: translateY(0);
  }
  .layer {
    position: relative;
    padding: $indent;
  }
  .layer_parent {
    position: relative;
    z-index: 1;
    &:after {
      content: '\e922';
      font-family: 'icomoon' !important;
      font-size: 11px;
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
    visibility: hidden;
    opacity: 0;
    margin: 0;
    padding: $indent;
    list-style: none;
    @media (max-height: 1000px) {
      .layer:nth-child(n+5) & {
        top: auto;
        bottom: 0;
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

</style>
