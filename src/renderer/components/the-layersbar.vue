<template lang="pug">
  transition(name="scroll-left")
    aside.page_layersbar(v-show="hideLayers" )
      ul.layersbar-list
        li.layer(
          v-for="(layer, i) in layersbarList"
          :key="i"
        )
          button.btn.btn--layersbar.layer_parent.js-clickout(type="button"
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
  import {trainingElements, deepLearnElements}  from '@/core/helpers.js'

  import IoInput              from '@/components/network-elements/elements/io-input/view-io-input.vue'
  import IoOutputBackprop     from '@/components/network-elements/elements/io-output-backpropagation/view-io-output-backpropagation.vue'
  import IoOutputGenetic      from '@/components/network-elements/elements/io-output-genetic-algorithm/view-io-output-genetic-algorithm.vue'
  import IoOutputRouting      from '@/components/network-elements/elements/io-output-routing-algorithm/view-io-output-routing-algorithm.vue'

  import DataData             from '@/components/network-elements/elements/data-data/view-data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment/view-data-environment.vue'

  import LearnDeepConnect     from '@/components/network-elements/elements/learn-deep-connect/view-learn-deep-connect.vue'
  import LearnDeepConvolut    from '@/components/network-elements/elements/learn-deep-convolut/view-learn-deep-convolut.vue'
  import LearnDeepDeconvolut  from '@/components/network-elements/elements/learn-deep-deconvolut/view-learn-deep-deconvolut.vue'
  import LearnDeepRecurrent   from '@/components/network-elements/elements/learn-deep-recurrent/view-learn-deep-recurrent.vue'

  import ProcessCrop          from '@/components/network-elements/elements/process-crop/view-process-crop.vue'
  import ProcessEmbed         from '@/components/network-elements/elements/process-embed/view-process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/view-process-grayscale.vue'
  import ProcessHot           from '@/components/network-elements/elements/process-hot/view-process-hot.vue'
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

  import LearnClassDbscans    from '@/components/network-elements/elements/learn-class-dbscans/view-learn-class-dbscans.vue'
  import LearnClassKMeans     from '@/components/network-elements/elements/learn-class-k-means/view-learn-class-k-means.vue'
  import LearnClassKNearest   from '@/components/network-elements/elements/learn-class-k-nearest/view-learn-class-k-nearest.vue'
  import LearnClassRandomForest  from '@/components/network-elements/elements/learn-class-random-forest/view-learn-class-random-forest.vue'
  import LearnClassVectorMachine from '@/components/network-elements/elements/learn-class-vector-machine/view-learn-class-vector-machine.vue'


export default {
  name: 'TheLayersbar',
  mixins: [clickOutside],
  components: {
    IoInput,
    IoOutputBackprop,
    IoOutputGenetic,
    IoOutputRouting,
    DataData,
    DataEnvironment,
    LearnDeepConnect,
    LearnDeepConvolut,
    LearnDeepDeconvolut,
    LearnDeepRecurrent,
    ProcessCrop,
    ProcessEmbed,
    ProcessGrayscale,
    ProcessHot,
    ProcessReshape,
    TrainNormal,
    TrainNormalData,
    TrainGenetic,
    TrainDynamic,
    TrainReinforce,
    MathArgmax,
    MathMerge,
    MathSoftmax,
    MathSplit,
    LearnClassDbscans,
    LearnClassKMeans,
    LearnClassKNearest,
    LearnClassRandomForest,
    LearnClassVectorMachine
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
        },
        {
          tooltip: 'Processing',
          layerClass: 'net-element-process',
          iconClass: 'icon-settings',
          showEl: false,
          networkElements: ['process-reshape', 'process-embed', 'process-grayscale', 'process-hot', 'process-crop']
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
          networkElements: ['LearnClassDbscans', 'LearnClassKMeans', 'LearnClassKNearest', 'LearnClassRandomForest', 'LearnClassVectorMachine']
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
      this.ClickElementTracking = ev.target.closest('.js-clickout');
      document.addEventListener('click', this.clickOutside);

      if (this.layersbarList[index].showEl) {
        this.layersbarList[index].showEl = false
      }
      else {
        this.clickOutsideAction();
        this.layersbarList[index].showEl = true;
      }
    },
    clickOutsideAction() {
      this.layersbarList.forEach((item)=> {
        item.showEl = false
      })
    },
  }
}
</script>

<style lang="scss">
  @import "../scss/base";
  $indent: 5px;
  .page_layersbar {
    grid-area: layersbar;
    max-width: $w-layersbar;
  }
  .layersbar-list {
    padding: 0;
    margin: 0;
    list-style: none;
    transform: translateY(0);
    transition: transform $animation-speed $animation-speed;
    padding-bottom: 30px;
  }
  .layer {
    position: relative;
    padding: $indent;
  }
  .layer_parent {
    position: relative;
    z-index: 1;
    &:after {
      content: "\e922";
      font-family: 'icomoon' !important;
      position: absolute;
      line-height: 1;
      right: 1px;
      bottom: 1px;
      font-size: 11px;
    }
  }
  ul.layer_child-list {
    @include multi-transition (transform, opacity, visibility);
    position: absolute;
    top: 0;
    left: -$indent;
    padding: $indent;
    margin: 0;
    list-style: none;
    opacity: 0;
    visibility: hidden;
    @media (max-height: 1000px) {
      .layer:nth-child(n+5) & {
        bottom: 0;
        top: auto;
      }
    }
    .active + & {
      transform: translateX(100%);
      opacity: 1;
      visibility: visible;
    }
    > li + li {
      padding-top: $indent;
    }
  }

  //Animations
  .scroll-left-enter {
    max-width: 0;
    .layersbar-list {
      transform: translateY(-120%);
    }
  }
  .scroll-left-enter-active {
    transition: max-width $animation-speed 0s;
  }
  .scroll-left-leave-active {
    transition: max-width $animation-speed $animation-speed;
    .layersbar-list {
      transition: transform $animation-speed;
    }
  }
  .scroll-left-leave-to {
    max-width: 0;
    .layersbar-list {
      transform: translateY(-120%);
    }
  }

</style>
