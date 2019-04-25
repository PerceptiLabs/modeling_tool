<template lang="pug">
  div
    base-net-el(
      :data-el="elementData"
      :layer-container="true"
    )
      view-el
      template(slot="context")
        context-menu
    component(
      v-for="(el, index) in elementData.el.containerLayersList"
      :key="el.index"
      ref="layer"
      :is="el.el.componentName"
      :element-data="el"
      )

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ContextMenu  from '@/components/network-elements/net-context-menu/net-context-menu.vue';
  import ViewEl       from './view-layer-container.vue';

  import IoInput              from '@/components/network-elements/elements/io-input/io-input.vue'
  import IoOutputBackprop     from '@/components/network-elements/elements/io-output-backpropagation/io-output-backpropagation.vue'
  import IoOutputGenetic      from '@/components/network-elements/elements/io-output-genetic-algorithm/io-output-genetic-algorithm.vue'
  import IoOutputRouting      from '@/components/network-elements/elements/io-output-routing-algorithm/io-output-routing-algorithm.vue'

  import DataData             from '@/components/network-elements/elements/data-data/data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment/data-environment.vue'

  import DeepLearningFC       from '@/components/network-elements/elements/deep-learning-fc/deep-learning-fc.vue'
  import DeepLearningConv     from '@/components/network-elements/elements/deep-learning-conv/deep-learning-conv.vue'
  import DeepLearningDeconv   from '@/components/network-elements/elements/deep-learning-deconv/deep-learning-deconv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/deep-learning-recurrent.vue'

  import ProcessCrop          from '@/components/network-elements/elements/process-crop/process-crop.vue'
  import ProcessEmbed         from '@/components/network-elements/elements/process-embed/process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/process-grayscale.vue'
  import ProcessOneHot        from '@/components/network-elements/elements/process-one-hot/process-one-hot.vue'
  import ProcessReshape       from '@/components/network-elements/elements/process-reshape/process-reshape.vue'

  import TrainNormal          from '@/components/network-elements/elements/train-normal/train-normal.vue'
  import TrainNormalData      from '@/components/network-elements/elements/train-normal-data/train-normal-data.vue'
  import TrainGenetic         from '@/components/network-elements/elements/train-genetic/train-genetic.vue'
  import TrainDynamic         from '@/components/network-elements/elements/train-dynamic/train-dynamic.vue'
  import TrainReinforce       from '@/components/network-elements/elements/train-reinforce/train-reinforce.vue'

  import MathArgmax           from '@/components/network-elements/elements/math-argmax/math-argmax.vue'
  import MathMerge            from '@/components/network-elements/elements/math-merge/math-merge.vue'
  import MathSoftmax          from '@/components/network-elements/elements/math-softmax/math-softmax.vue'
  import MathSplit            from '@/components/network-elements/elements/math-split/math-split.vue'

  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/classic-ml-vector-machine.vue'

  import LayerContainer       from '@/components/network-elements/elements/layer-container/layer-container.vue'

  export default {
    name: 'LayerContainer',
    components: {
      BaseNetEl, ContextMenu, ViewEl,
      IoInput, IoOutputBackprop, IoOutputGenetic, IoOutputRouting,
      DataData, DataEnvironment,
      DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
      ProcessCrop, ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape,
      TrainNormal, TrainNormalData, TrainGenetic, TrainDynamic, TrainReinforce,
      MathArgmax, MathMerge, MathSoftmax, MathSplit,
      ClassicMLDbscans, ClassicMLKMeans, ClassicMLKNN, ClassicMLRandomForest, ClassicMLSVM,
      LayerContainer
    },
    props: {
      elementData: Object
    },
    mounted() {
      console.log(this.elementData);
    }
  }
</script>
