<template lang="pug">
  section.network_info-section(id="tutorial_view-box")
    .info-section_head(v-if="!testIsOpen")
      h3 ViewBox
    .info-section_main(v-if="elData !== null")
      component(
        :is="elData.componentName"
        :elementData="elData.viewBox"
        )
</template>

<script>
  import DataData             from '@/components/network-elements/elements/data-data/viewBox-data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment/viewBox-data-environment.vue'

  import DeepLearningFC       from '@/components/network-elements/elements/deep-learning-fc/viewBox-deep-learning-fc.vue'
  import DeepLearningConv     from '@/components/network-elements/elements/deep-learning-conv/viewBox-deep-learning-conv.vue'
  import DeepLearningDeconv   from '@/components/network-elements/elements/deep-learning-deconv/viewBox-deep-learning-deconv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/viewBox-deep-learning-recurrent.vue'

  import ProcessCrop          from '@/components/network-elements/elements/process-crop/viewBox-process-crop.vue'
  import ProcessEmbed         from '@/components/network-elements/elements/process-embed/viewBox-process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/viewBox-process-grayscale.vue'
  import ProcessOneHot        from '@/components/network-elements/elements/process-one-hot/viewBox-process-one-hot.vue'
  import ProcessReshape       from '@/components/network-elements/elements/process-reshape/viewBox-process-reshape.vue'

  import MathArgmax           from '@/components/network-elements/elements/math-argmax/viewBox-math-argmax.vue'
  import MathMerge            from '@/components/network-elements/elements/math-merge/viewBox-math-merge.vue'
  import MathSoftmax          from '@/components/network-elements/elements/math-softmax/viewBox-math-softmax.vue'
  import MathSplit            from '@/components/network-elements/elements/math-split/viewBox-math-split.vue'

export default {
  name: "TheViewBox",
  components: {
    DataData, DataEnvironment,
    DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
    ProcessCrop, ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape,
    MathArgmax, MathMerge, MathSoftmax, MathSplit,
  },
  props: {
    elData: {
      type: Object,
      default: function () {
        return null
      }
    }
  },
  data() {
    return {

    }
  },
  mounted() {

  },
  methods: {

  },
  computed: {
    testIsOpen() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest
    }
    // viewBoxData() {
    //   return this.elData.find((element, index, array)=>{
    //     if(element.layerType !== 'Training') {
    //       return element
    //     }
    //     else return false
    //   });
    // }
    
  }
}
</script>

<style lang="scss">
  @import "../../scss/base";
  .open-statistic .the-view-box .info-section_main {
    border-left: 2px solid $bg-window;
  }
</style>
