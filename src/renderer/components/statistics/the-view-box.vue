<template lang="pug">
  section.network_info-section
    .info-section_head
      h3 ViewBox
    .info-section_main(v-if="elData !== null")
      component(
        :is="elData.componentName"
        :elementData="elData.viewBox"
        )
</template>

<script>
  import DataData         from '@/components/network-elements/elements/data-data/viewBox-data-data.vue'
  import DataEnvironment  from '@/components/network-elements/elements/data-environment/viewBox-data-environment.vue'
  import LearnDeepConnect     from '@/components/network-elements/elements/learn-deep-connect/viewBox-learn-deep-connect.vue'
  import LearnDeepConvolut    from '@/components/network-elements/elements/learn-deep-convolut/viewBox-learn-deep-convolut.vue'
  import LearnDeepDeconvolut  from '@/components/network-elements/elements/learn-deep-deconvolut/viewBox-learn-deep-deconvolut.vue'
  import LearnDeepRecurrent   from '@/components/network-elements/elements/learn-deep-recurrent/viewBox-learn-deep-recurrent.vue'
  import MathArgmax   from '@/components/network-elements/elements/math-argmax/viewBox-math-argmax.vue'
  import MathMerge    from '@/components/network-elements/elements/math-merge/viewBox-math-merge.vue'
  import MathSoftmax  from '@/components/network-elements/elements/math-softmax/viewBox-math-softmax.vue'
  import MathSplit    from '@/components/network-elements/elements/math-split/viewBox-math-split.vue'
  import ProcessCrop      from '@/components/network-elements/elements/process-crop/viewBox-process-crop.vue'
  import ProcessEmbed     from '@/components/network-elements/elements/process-embed/viewBox-process-embed.vue'
  import ProcessGrayscale from '@/components/network-elements/elements/process-grayscale/viewBox-process-grayscale.vue'
  import ProcessHot       from '@/components/network-elements/elements/process-hot/viewBox-process-hot.vue'
  import ProcessReshape   from '@/components/network-elements/elements/process-reshape/viewBox-process-reshape.vue'

export default {
  name: "TheViewBox",
  components: {
    DataData, DataEnvironment,
    LearnDeepConnect, LearnDeepConvolut, LearnDeepDeconvolut, LearnDeepRecurrent,
    MathArgmax, MathMerge, MathSoftmax, MathSplit,
    ProcessCrop, ProcessEmbed, ProcessGrayscale, ProcessHot, ProcessReshape

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

<style lang="scss" scoped>

</style>
