<template lang="pug">
  section.network_info-section
    .info-section_head
      h3 Statistics
    .info-section_main(v-if="elData !== null")
      component(
        :is="elData.componentName"
        :elementData="elData.viewBox"
      )
</template>

<script>
  import LearnClassDbscans        from '@/components/network-elements/elements/learn-class-dbscans/viewBox-learn-class-dbscans.vue'
  import LearnClassKMeans         from '@/components/network-elements/elements/learn-class-k-means/viewBox-learn-class-k-means.vue'
  import LearnClassKNearest       from '@/components/network-elements/elements/learn-class-k-nearest/viewBox-learn-class-k-nearest.vue'
  import LearnClassRandomForest   from '@/components/network-elements/elements/learn-class-random-forest/viewBox-learn-class-random-forest.vue'
  import LearnClassVectorMachine  from '@/components/network-elements/elements/learn-class-vector-machine/viewBox-learn-class-vector-machine.vue'

  import TrainDynamic     from '@/components/network-elements/elements/train-dynamic/viewBox-train-dynamic.vue'
  import TrainGenetic     from '@/components/network-elements/elements/train-genetic/viewBox-train-genetic.vue'
  import TrainNormal      from '@/components/network-elements/elements/train-normal/viewBox-train-normal.vue'
  import TrainNormalData  from '@/components/network-elements/elements/train-normal-data/viewBox-train-normal-data.vue'
  import TrainReinforce   from '@/components/network-elements/elements/train-reinforce/viewBox-train-reinforce.vue'


export default {
  name: "TheStatistics",
  components: {
    LearnClassDbscans, LearnClassKMeans, LearnClassKNearest, LearnClassRandomForest, LearnClassVectorMachine,
    TrainDynamic, TrainGenetic, TrainNormal, TrainNormalData, TrainReinforce
  },
  props: {
    elData: {
      type: Object,
      default: function () {
        return {}
      }
    }
  },
  data() {
    return {

    }
  },
  methods: {

  },
  computed: {

  }
}
</script>

<style lang="scss" scoped>

</style>
